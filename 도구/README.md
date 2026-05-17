# 도구 (Tools)

워크스페이스 차원의 자동화·검증 헬퍼.

---

## 현재 도구

### `sync_patcher/sync_patcher.py`
Whisper 받아쓰기(SRT) + `design.md` 의 싱크 룰 표를 입력받아:
1. 각 `event_id`의 트리거 단어가 실제로 발화된 글로벌 시점을 추출
2. `sync_map.json` 생성 (event_id → resolved_time)
3. GSAP 코드의 `// @sync:event_id` 주석이 달린 라인의 timing 인자를 자동 교체

**호출**
```bash
python3 도구/sync_patcher/sync_patcher.py \
  --transcript 프로젝트/NNN_xxx/04_녹음/받아쓰기/auto_transcript.srt \
  --design     프로젝트/NNN_xxx/03_스토리보드/design.md \
  --gsap       프로젝트/NNN_xxx/06_편집/hyperframes/index.html \
  --sync-map   프로젝트/NNN_xxx/06_편집/검증/sync_map.json \
  --dry-run    # 미리보기 (실제 패치 안 함)
```

**GSAP 코드 마킹 규칙**
```js
tl.fromTo("#s01-check", {...}, {...}, 3.8);   // @sync:s01-check-in
//                                             ^^^^^^^^^^^^^^^^^^^^^^
//                                 design.md의 event_id와 일치
```

---

### `verify-playwright/verify.mjs`
헤드리스 Chromium으로 Hyperframes 컴포지션을 열고, GSAP timeline을 seek해 시점별 DOM 상태를 검증.

**호출**
```bash
# Studio가 켜져 있을 때
node 도구/verify-playwright/verify.mjs \
  --sync-map 프로젝트/NNN_xxx/06_편집/검증/sync_map.json \
  --studio   http://localhost:3002/#project/composition \
  --report   프로젝트/NNN_xxx/06_편집/검증

# 정적 파일 직접 검증
node 도구/verify-playwright/verify.mjs \
  --sync-map 프로젝트/NNN_xxx/06_편집/검증/sync_map.json \
  --html     프로젝트/NNN_xxx/06_편집/hyperframes/index.html \
  --report   프로젝트/NNN_xxx/06_편집/검증
```

**출력**
- `verify_report.json` — 기계 판독용
- `verify_report.md` — 사람 판독용 (각 event_id의 PASS/FAIL + opacity·display·bbox)

**컨벤션**
- `event_id` 가 `s01-check-in` 이면 검증 대상 셀렉터는 `#s01-check` (`-in`/`-out`/`-on`/`-off` 자동 strip)
- opacity > 0.1 + visibility ≠ hidden + display ≠ none → PASS

---

### `verify_vision.md`
Vision LLM(클로드 등)로 시각적 의도(무드·정보 과밀·강조 누락 등)를 검증하는 절차 문서.
에이전트가 직접 따라 실행할 수 있도록 단계별로 명세되어 있음.

---

## 추가 예정

- `new_project.sh` — `_템플릿/` 복제 + `INDEX.md` 갱신 + Hyperframes 초기화
- `setup_symlinks.sh` — `06_편집/hyperframes/public/` 심볼릭 링크 일괄 생성
- `split_audio.py` — mp4 → 씬별 wav 자동 분할 (silencedetect)
- `status_report.sh` — 프로젝트들의 상태 자동 집계 → INDEX.md 갱신

---

## 사용 원칙

- 모든 스크립트는 사용법을 헤더 주석에 명시
- 파괴적 작업(rm, 덮어쓰기)은 `--dry-run` 또는 `--confirm` 보호
- 추가/변경 시 `CHANGELOG.md` 갱신
