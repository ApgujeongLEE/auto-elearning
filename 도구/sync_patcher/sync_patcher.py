#!/usr/bin/env python3
"""
sync_patcher — Whisper 받아쓰기 기반 GSAP 시점 자동 보정 도구

입력:
  --transcript  Whisper word-level SRT 파일 (04_녹음/받아쓰기/auto_transcript.srt)
  --design      design.md 파일 (4. 발화-모션 싱크 룰 표를 읽음)
  --gsap        GSAP 코드를 포함한 HTML 파일 (06_편집/hyperframes/index.html)

출력:
  --sync-map    sync_map.json (의도된 트리거 vs 실측 시점 매핑)
  --patch       --gsap 파일의 // @sync:event_id 주석이 달린 라인의 timing을 자동 교체

워크플로우:
  1. design.md의 싱크 룰 표 파싱
  2. SRT를 단어 단위로 파싱
  3. 각 (trigger_word, match_strategy) 조합에 해당하는 글로벌 시점 추출
  4. sync_map.json 생성 (event_id → resolved_time)
  5. GSAP HTML의 // @sync:event_id 주석 라인을 정규식으로 찾아 timing 인자 교체
  6. dry-run 모드 지원 (--dry-run): 패치하지 않고 변경 사항만 출력

사용 예:
  python3 sync_patcher.py \\
    --transcript "../../프로젝트/001_agentic-ai_2026-05-15/04_녹음/받아쓰기/auto_transcript.srt" \\
    --design "../../프로젝트/001_agentic-ai_2026-05-15/03_스토리보드/design.md" \\
    --gsap "../../프로젝트/001_agentic-ai_2026-05-15/06_편집/hyperframes/index.html" \\
    --sync-map "../../프로젝트/001_agentic-ai_2026-05-15/06_편집/검증/sync_map.json" \\
    --dry-run
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────
# SRT 파싱
# ──────────────────────────────────────────────────────────────────────

@dataclass
class Word:
    start: float  # seconds
    end: float
    text: str


def parse_srt_time(s: str) -> float:
    """'00:01:23,456' → 83.456"""
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def parse_srt(path: Path) -> list[Word]:
    """Whisper word-level SRT를 파싱해 Word 리스트로 반환.

    Whisper-cli 출력에는 multi-byte 한글의 부분 바이트가 single token으로 잘려 깨진
    UTF-8 시퀀스가 섞일 수 있음. errors='replace'로 깨진 부분만 U+FFFD로 치환.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\s*\n", text.strip())
    words: list[Word] = []
    for block in blocks:
        lines = [ln for ln in block.strip().split("\n") if ln.strip()]
        if len(lines) < 2:
            continue
        # lines[0] = index, lines[1] = "HH:MM:SS,mmm --> HH:MM:SS,mmm", lines[2:] = text
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not m:
            continue
        t_start = parse_srt_time(m.group(1))
        t_end = parse_srt_time(m.group(2))
        word_text = " ".join(lines[2:]).strip()
        if word_text:
            words.append(Word(start=t_start, end=t_end, text=word_text))
    return words


# ──────────────────────────────────────────────────────────────────────
# design.md 싱크 룰 파싱
# ──────────────────────────────────────────────────────────────────────

@dataclass
class SyncRule:
    scene: str
    event_id: str
    trigger_word: str
    match_strategy: str  # "first" | "scene" | "nth=N"
    offset: float
    intent: str = ""


def parse_design_rules(path: Path) -> list[SyncRule]:
    """design.md의 "4. 발화-모션 싱크 룰" 표를 파싱."""
    text = path.read_text(encoding="utf-8")
    rules: list[SyncRule] = []

    # 표 영역만 추출 ("발화-모션 싱크 룰" 헤더 — 섹션 번호 무관)
    sec_match = re.search(r"##\s*[\d]+\.\s*발화-모션 싱크 룰.*?(?=\n##\s|\Z)", text, re.DOTALL)
    if not sec_match:
        return rules
    section = sec_match.group(0)

    # 마크다운 표 행 추출 (헤더·구분선 제외, 백틱으로 감싸지 않은 행만)
    for line in section.split("\n"):
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        # 헤더 행 스킵
        if cells[0] in ("씬", "scene"):
            continue
        scene, event_id_raw, trigger_word_raw, strategy, offset_raw, intent = cells[:6]
        # 백틱 제거
        event_id = event_id_raw.strip("`")
        trigger_word = trigger_word_raw.strip("`").strip()
        # placeholder/빈 행 무시
        if not event_id or not trigger_word:
            continue
        if event_id in ("...", "—", "-") or trigger_word in ("...", "—", "-"):
            continue
        try:
            offset = float(offset_raw.replace("+", "").strip())
        except ValueError:
            offset = 0.0
        rules.append(SyncRule(
            scene=scene,
            event_id=event_id,
            trigger_word=trigger_word,
            match_strategy=strategy.strip(),
            offset=offset,
            intent=intent.strip(),
        ))
    return rules


# ──────────────────────────────────────────────────────────────────────
# 매칭: 트리거 단어 → 글로벌 시점
# ──────────────────────────────────────────────────────────────────────

def _build_accumulated(words: list[Word]) -> tuple[str, list[tuple[int, float]]]:
    """Whisper word 토큰들을 공백·구두점 제거하여 누적 텍스트로 만들고,
    (누적텍스트의 끝 인덱스 → 그 토큰의 시작 시점) 매핑 리스트를 반환.
    한글이 글자별로 잘려있는 경우 직접 단어 매칭이 어렵기 때문에 누적 텍스트에서 검색."""
    acc = ""
    index_to_time: list[tuple[int, float]] = []
    for w in words:
        # 공백·구두점·깨진 UTF-8 치환 문자(U+FFFD) 제거
        clean = re.sub(r"[\s.,?!\"'()\[\]�]+", "", w.text)
        if not clean:
            continue
        acc += clean
        index_to_time.append((len(acc), w.start))
    return acc, index_to_time


def _time_at_index(idx: int, index_to_time: list[tuple[int, float]]) -> float | None:
    """누적 텍스트의 idx 위치를 포함하는 토큰의 시작 시점."""
    for end_idx, t in index_to_time:
        if end_idx > idx:
            return t
    return index_to_time[-1][1] if index_to_time else None


def _all_occurrences(haystack: str, needle: str) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        i = haystack.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def resolve_time(rule: SyncRule, words: list[Word], scene_ranges: dict[str, tuple[float, float]]) -> float | None:
    """싱크 룰을 받아 받아쓰기에서 트리거 단어의 글로벌 시점을 찾아 반환.

    한글 word-level SRT는 글자 단위로 잘려있을 수 있으므로:
      1) 모든 단어 텍스트를 공백·구두점 제거 후 하나의 누적 문자열로 합침
      2) 누적 문자열에서 trigger_word(공백 제거판)을 search
      3) match_strategy에 따라 적절한 위치 선택
      4) 그 위치의 토큰 시작 시점을 시점으로 반환
    """
    # 누적 텍스트
    acc, index_to_time = _build_accumulated(words)
    trigger_clean = re.sub(r"\s+", "", rule.trigger_word)
    if not trigger_clean:
        return None

    occurrences = _all_occurrences(acc, trigger_clean)
    if not occurrences:
        return None

    chosen_idx: int | None = None

    if rule.match_strategy.startswith("nth="):
        try:
            n = int(rule.match_strategy.split("=")[1])
            if 1 <= n <= len(occurrences):
                chosen_idx = occurrences[n - 1]
        except ValueError:
            pass
    elif rule.match_strategy == "scene":
        rng = scene_ranges.get(rule.scene)
        if rng:
            # 씬 범위 안에 들어오는 첫 등장
            for idx in occurrences:
                t = _time_at_index(idx, index_to_time)
                if t is not None and rng[0] <= t < rng[1]:
                    chosen_idx = idx
                    break
        if chosen_idx is None:
            # 폴백: 첫 등장
            chosen_idx = occurrences[0]
    else:
        # 기본 (first)
        chosen_idx = occurrences[0]

    if chosen_idx is None:
        return None
    t = _time_at_index(chosen_idx, index_to_time)
    if t is None:
        return None
    return t + rule.offset


# ──────────────────────────────────────────────────────────────────────
# GSAP 코드 패치
# ──────────────────────────────────────────────────────────────────────

# 다음 형태의 라인을 인식:
#   tl.fromTo("#x", {...}, {... duration: 0.5 ...}, 3.8);   // @sync:s01-check-in
#   tl.to("#x", {... duration: 0.3 ...}, 3.5);             // @sync:s01-check-out
# 마지막 인자(시점)를 교체한다.
PATCH_RE = re.compile(
    r"(,\s*)([0-9.]+)(\s*\)\s*;?\s*//\s*@sync:(\S+))"
)


def patch_gsap(html_text: str, resolved: dict[str, float]) -> tuple[str, list[dict]]:
    """// @sync:event_id 주석이 달린 GSAP 호출의 시점 인자를 resolved[event_id]로 교체."""
    changes: list[dict] = []

    def _sub(m: re.Match) -> str:
        head, old_time, tail = m.group(1), m.group(2), m.group(3)
        event_id = m.group(4)
        if event_id not in resolved:
            return m.group(0)
        new_time = f"{resolved[event_id]:.3f}"
        changes.append({"event_id": event_id, "old": float(old_time), "new": float(new_time), "delta": float(new_time) - float(old_time)})
        return f"{head}{new_time}{tail}"

    patched = PATCH_RE.sub(_sub, html_text)
    return patched, changes


# ──────────────────────────────────────────────────────────────────────
# 씬 범위 추출 (design.md 또는 GSAP 코드에서 추출 가능. 여기선 GSAP의 scenes 배열을 찾음)
# ──────────────────────────────────────────────────────────────────────

SCENES_RE = re.compile(
    r"id:\s*\"#scene-(\w+)\",?\s*in:\s*([\d.]+),?\s*out:\s*([\d.]+)"
)


def extract_scene_ranges(html_text: str) -> dict[str, tuple[float, float]]:
    """index.html의 scenes 배열에서 (scene_name → (in, out)) 추출."""
    ranges: dict[str, tuple[float, float]] = {}
    for m in SCENES_RE.finditer(html_text):
        name = m.group(1).upper()  # s01 → S01
        ranges[name] = (float(m.group(2)), float(m.group(3)))
    return ranges


# ──────────────────────────────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcript", required=True, type=Path)
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--gsap", required=True, type=Path)
    ap.add_argument("--sync-map", type=Path, default=None, help="저장 경로 (.json)")
    ap.add_argument("--dry-run", action="store_true", help="패치하지 않고 미리보기만")
    args = ap.parse_args()

    if not args.transcript.exists():
        sys.exit(f"❌ 받아쓰기 파일 없음: {args.transcript}")
    if not args.design.exists():
        sys.exit(f"❌ design.md 없음: {args.design}")
    if not args.gsap.exists():
        sys.exit(f"❌ GSAP HTML 없음: {args.gsap}")

    print(f"📖 받아쓰기 파싱: {args.transcript}")
    words = parse_srt(args.transcript)
    print(f"   → 단어 {len(words)}개")

    print(f"📐 design.md 룰 파싱: {args.design}")
    rules = parse_design_rules(args.design)
    print(f"   → 싱크 룰 {len(rules)}개")
    if not rules:
        sys.exit("❌ design.md 4번 섹션에 싱크 룰이 없습니다. 표를 먼저 채워주세요.")

    print(f"🎬 GSAP HTML 읽기: {args.gsap}")
    html_text = args.gsap.read_text(encoding="utf-8")
    scene_ranges = extract_scene_ranges(html_text)
    print(f"   → 씬 범위 {len(scene_ranges)}개: {scene_ranges}")

    # 트리거 시점 추출
    resolved: dict[str, float] = {}
    report: list[dict] = []
    for rule in rules:
        t = resolve_time(rule, words, scene_ranges)
        if t is None:
            print(f"   ⚠️  미해결 [{rule.event_id}]: '{rule.trigger_word}' 못 찾음")
            report.append({**asdict(rule), "resolved_time": None, "status": "UNRESOLVED"})
            continue
        resolved[rule.event_id] = t
        print(f"   ✅ [{rule.event_id}] '{rule.trigger_word}' → {t:.3f}s (offset {rule.offset:+.2f})")
        report.append({**asdict(rule), "resolved_time": t, "status": "OK"})

    # sync_map.json 저장
    if args.sync_map:
        args.sync_map.parent.mkdir(parents=True, exist_ok=True)
        args.sync_map.write_text(json.dumps({
            "transcript": str(args.transcript),
            "design": str(args.design),
            "scene_ranges": {k: list(v) for k, v in scene_ranges.items()},
            "rules": report,
            "resolved": {k: round(v, 3) for k, v in resolved.items()},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"💾 sync_map 저장: {args.sync_map}")

    # GSAP 패치
    patched_html, changes = patch_gsap(html_text, resolved)
    print(f"\n🔧 패치할 위치 {len(changes)}개:")
    for c in changes:
        print(f"   [{c['event_id']}] {c['old']:.3f}s → {c['new']:.3f}s  (Δ {c['delta']:+.3f}s)")

    if not changes:
        print("\n⚠️  // @sync:event_id 주석이 달린 라인이 없습니다.")
        print("   GSAP 코드에 마킹 주석을 추가해야 자동 패치됩니다.")
        print("   예: tl.fromTo(\"#s01-check\", {...}, 3.8);   // @sync:s01-check-in")
        return

    if args.dry_run:
        print("\n💡 --dry-run 모드: 파일을 변경하지 않았습니다.")
    else:
        backup = args.gsap.with_suffix(args.gsap.suffix + ".bak")
        backup.write_text(html_text, encoding="utf-8")
        args.gsap.write_text(patched_html, encoding="utf-8")
        print(f"\n✅ GSAP 파일 패치 완료. 백업: {backup}")


if __name__ == "__main__":
    main()
