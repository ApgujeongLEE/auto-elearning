# Changelog

워크스페이스 차원의 변경 이력. 폴더 구조, 템플릿, 공용자산, 워크플로우 규칙의 변경을 기록.

---

## 2026-05-18 — 자동 검증 루프 정식 적용 · Material 3 · 이식성

### 자동 검증 루프 (002 영상에 첫 정식 적용)
- `도구/sync_patcher/sync_patcher.py` 신규 — Whisper 받아쓰기 기반 GSAP `// @sync:event_id` 시점 자동 보정
  - 한글 word-level SRT 글자 잘림·깨진 글자(U+FFFD) 대응 (누적 텍스트 기반 매칭)
  - PATCH_RE 정규식: `// @sync:` 주석 라인의 마지막 시점 인자만 정확히 교체
  - design.md 헤더 번호 무관 파싱 (`발화-모션 싱크 룰` 표만 찾음)
- `도구/verify-playwright/verify.mjs` 신규 — Playwright + Chromium 기반 DOM 검증 (시점별 opacity·transform·bbox)
- `도구/verify_vision.md` 신규 — Vision LLM 시각 검증 절차 명세
- `_템플릿/03_스토리보드/design.md` 신규 — 시각 토큰·발화-모션 싱크 룰 표 템플릿
- `_템플릿/체크리스트.md` 갱신 — "🔬 7. 자동 검증 루프" 섹션 추가
- README 핵심 규칙 6번 추가: "GSAP timing은 받아쓰기 기반으로만 확정"

### Material Design 3 시스템
- 002 영상의 design.md를 Google Material 3 기반으로 전면 재작성
  - Surface elevation 5단계, Primary/Secondary/Tertiary 컬러 롤
  - Google Sans Display/Text + Roboto Mono + Material Symbols Outlined 폰트
  - 이모지 → Material Symbols 아이콘 일괄 교체
- 002 index.html에 M3 토큰 적용, S05 통계 씬 보강 (supporting cards 3개 + 10× count-up)
- preview_v02.mp4 렌더 (166.43s, 8.4MB)

### 이식성 (Git LFS + macOS bootstrap + Codespaces)
- `setup.sh` 신규 — macOS bootstrap (brew/ffmpeg/node@22/whisper-cpp/playwright/whisper 모델 자동)
- `.devcontainer/devcontainer.json` + `postCreate.sh` 신규 — GitHub Codespaces 자동 환경 구축
- `.gitattributes` 신규 — Git LFS 트래킹 (mp4/mp3/m4a/mov/마스터/에셋/공용자산)
- `.gitignore` 정비 — 재생성 가능 산출물만 ignore (분할 wav, 프리뷰 mp4)
- README "이식성" + "Git LFS" + "새 주제로 영상 만들기" 섹션 추가
- GitHub 리포: https://github.com/ApgujeongLEE/auto-elearning

### 운영 개선
- `.claude/settings.local.json` 을 `.gitignore` 처리 (개인 설정, 푸시 X)

### 영상 산출물
- 001 agentic-ai: preview_v01.mp4 (58.89s, 3.4MB) — 사후 어긋남 발견 (검증 루프 도입 전)
- 002 vibe-coding-for-design: preview_v02.mp4 (166.43s, 8.4MB) — **자동 검증 루프 첫 정식 적용**

---

## 2026-05-15 — 초기 구성

- 워크스페이스 초기 생성
- `_템플릿/` 골격 + 핵심 문서 3종 (기획서, 스크립트 2종, 스토리보드) 작성
- `공용자산/` 디렉토리 골격 + 스타일가이드, 컬러팔레트 초안
- `INDEX.md` 대시보드 초안
- 폴더명 한글 결정 (단, Hyperframes 내부 디렉토리는 영문 유지)
- 스크립트는 편집용(`스크립트.md`) + 낭독용(`📢_녹음용_스크립트.md`) 두 파일로 분리하기로 결정
