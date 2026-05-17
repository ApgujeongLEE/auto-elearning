# Auto E-learning

Hyperframes 기반 이러닝 영상 제작 워크스페이스. 동시에 5~20개의 강의·튜토리얼형 영상 프로젝트를 관리한다.

---

## 워크플로우 한눈에 보기

```
[1. 기획서]  →  [2. 스크립트]  →  [3. 스토리보드 + design.md]
                       ↓
              📢 녹음용 스크립트 전달
                       ↓
              [4. 사용자 녹음 → mp4]
                       ↓
[5. 음성 분할·받아쓰기]  →  [6. 에셋]  →  [7. Hyperframes 편집(GSAP + @sync 주석)]
                                              ↓
                              [8. 자동 검증 루프]
                              ├─ sync_patcher.py  (받아쓰기 → GSAP 시점 패치)
                              ├─ verify.mjs       (Playwright DOM 검증)
                              └─ verify_vision    (Claude Vision 시각 검증)
                                              ↓
                                       [9. 최종 렌더 → 검수]
```

**핵심 원칙**: 씬 ID (`S01`, `S02`...)가 모든 산출물을 1:1로 관통한다. 스크립트의 `S07`은 스토리보드의 `S07`, 음성 파일 `S07.wav`, Hyperframes 컴포지션 `S07.html`, 자막의 `S07` 라인과 동일하다.

---

## 폴더 구조

| 경로 | 용도 |
|---|---|
| `_템플릿/` | 신규 프로젝트 골격. `cp -r` 로 복제해서 사용 |
| `공용자산/` | 모든 프로젝트가 공유하는 브랜드·폰트·BGM·SFX·템플릿 |
| `프로젝트/` | 실제 프로젝트 (`NNN_slug_YYYY-MM-DD/`) |
| `도구/` | 워크플로우 헬퍼 스크립트 (선택) |
| `INDEX.md` | 전체 프로젝트 현황 대시보드 |
| `CHANGELOG.md` | 워크스페이스 차원의 변경 이력 |

---

## 신규 프로젝트 시작

```bash
# 1. 템플릿 복제
cp -r _템플릿 "프로젝트/004_git-intro_2026-05-20"

# 2. Hyperframes 초기화 (선택, 편집 단계 진입 시)
cd "프로젝트/004_git-intro_2026-05-20/06_편집/hyperframes"
npx hyperframes init .

# 3. 자산 심볼릭 링크 연결
ln -s ../../../04_녹음/가공 public/audio
ln -s ../../../05_에셋/이미지 public/images
ln -s ../../../05_에셋/PPT/slides_png public/ppt
ln -s ../../../../공용자산/폰트 public/fonts
ln -s ../../../../공용자산/BGM라이브러리 public/bgm
ln -s ../../../../공용자산/효과음라이브러리 public/sfx

# 4. INDEX.md 에 한 줄 추가
```

---

## 프로젝트 폴더 명명 규칙

`NNN_slug_YYYY-MM-DD/`

- `NNN`: 3자리 일련번호
- `slug`: **영문 소문자-하이픈** (Hyperframes CLI 인자로 쓰이므로 영문 필수)
- `YYYY-MM-DD`: 착수일

예: `001_python-basics_2026-05-15/`, `015_chatgpt-prompt_2026-06-30/`

---

## 사용자 ↔ 클로드 분담

| 단계 | 클로드 | 사용자 |
|---|---|---|
| 1 기획 | 기획서 작성 | 검토 |
| 2 스크립트 | 스크립트 + 📢 녹음용 스크립트 작성 | 검토 |
| 3 스토리보드 | Hyperframes 명세 작성 | 검토 |
| 4 녹음 | 📢 녹음용 스크립트 전달 | **녹음 → mp4 전달** |
| 5 음성 처리 | 노이즈 제거 / 씬별 분할 | — |
| 6 에셋 | 수집·PPT PNG 익스포트 | PPT 원본 제공 |
| 7 편집 | Hyperframes HTML 컴포지션 작성 | — |
| 8 검수 | 프리뷰 렌더 전달 | 피드백 |
| 9 최종 | 마스터 + 플랫폼별 인코딩 | 납품 확인 |

---

## Hyperframes 메모

- 공식 저장소: https://github.com/heygen-com/hyperframes
- 필수 환경: Node.js ≥ 22, FFmpeg
- 주요 명령: `npx hyperframes init`, `npx hyperframes preview`, `npx hyperframes render`
- 컴포지션 = HTML + `data-start`/`data-duration`/`data-track-index` 데이터 속성
- 어댑터: GSAP, Lottie, CSS, Three.js
- `06_편집/hyperframes/` 내부는 **영문 폴더명 유지** (Node.js/CLI 호환성)

---

## 핵심 규칙 6가지

1. **씬 ID는 영구 식별자** — 한 번 부여하면 변경 금지. 씬 삭제 시 결번 처리.
2. **단계별 폴더는 섞이지 않음** — 기획에 소스 금지, 소스에 편집물 금지.
3. **스크립트는 두 파일로 분리** — 편집용(`스크립트.md`) + 낭독용(`📢_녹음용_스크립트.md`). 항상 동시 갱신.
4. **자산은 심볼릭 링크로 연결** — `06_편집/hyperframes/public/`은 다른 폴더의 자산을 가리키는 링크만 둔다.
5. **상태는 폴더가 아니라 `INDEX.md`로 추적** — 폴더 이동 없이 메타데이터로 진행도 관리.
6. **GSAP timing은 받아쓰기 기반으로만 확정** — 스토리보드의 추정 타임코드는 초안. `design.md`의 싱크 룰 + `sync_patcher`로 실측 시점 자동 패치, `verify.mjs`로 DOM 검증.

---

## 이식성 — 다른 PC / 클라우드에서 작업하기

이 워크스페이스는 **두 가지 방식**으로 어디서든 작업할 수 있도록 구성됨.

### A. 다른 macOS PC (`setup.sh`)

```bash
git clone <이 리포 URL>
cd "Auto E-learning"
bash setup.sh
# brew, ffmpeg, node@22, whisper-cpp, whisper 모델, playwright 자동 설치 (~10-15분)
# 끝나면: source ~/.zprofile
```

이후 평소처럼 `cp -r _템플릿 프로젝트/...` 로 새 프로젝트 시작.

### B. 어떤 디바이스든 브라우저로 (GitHub Codespaces)

GitHub 리포에서 **Code → Codespaces → Create codespace** 클릭.
`.devcontainer/devcontainer.json` 이 자동으로:
- Ubuntu + Node 22 + Python 3.13 컨테이너 빌드
- ffmpeg, whisper.cpp, playwright 자동 설치
- VS Code + Claude Code 확장 자동 설치
- 포트 3002 (Hyperframes Studio) 자동 포워딩 (https URL 발급)

브라우저에서 VS Code가 열리고 즉시 작업 가능. 노트북·태블릿·다른 OS 모두 OK.

> **유료 시간**: GitHub Codespaces는 월 60시간 무료 (개인 계정 기준), 그 이후 시간당 ~$0.18

### 어떤 PC에서 작업하든 동일한 도구

| 도구 | macOS | Codespaces |
|---|---|---|
| ffmpeg | `brew install ffmpeg` | `apt install ffmpeg` |
| whisper-cli | `brew install whisper-cpp` | source 빌드 (`whisper.cpp`) |
| node@22 | `brew install node@22` | devcontainer feature |
| playwright | `npm install` + chromium | 동일 + `--with-deps` |
| Hyperframes | `npx hyperframes` | 동일 |

`도구/sync_patcher`, `도구/verify-playwright` 등 자체 도구는 OS 무관하게 동작.

---

## 자동 검증 루프 (신규)

`도구/` 안에 워크스페이스 공유 도구가 있습니다.

| 도구 | 역할 | 호출 |
|------|------|------|
| `도구/sync_patcher/sync_patcher.py` | Whisper SRT + `design.md` 싱크 룰 → `sync_map.json` 생성 + GSAP `// @sync:ID` 라인 자동 패치 | `python3 도구/sync_patcher/sync_patcher.py --help` |
| `도구/verify-playwright/verify.mjs` | Playwright로 GSAP timeline을 seek해 시점별 DOM 상태(opacity·transform·bbox) 검사 | `node 도구/verify-playwright/verify.mjs --sync-map ...` |
| `도구/verify_vision.md` | Vision LLM(클로드 등)로 스크린샷 시각 검증 절차 명세 | (에이전트가 따라 실행) |

자세한 사용은 `_템플릿/체크리스트.md` 의 "🔬 7. 자동 검증 루프" 섹션 참조.
