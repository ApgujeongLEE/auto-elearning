# Design Spec: 디자이너를 위한 바이브 코딩

> **검증 가능한 의도 명세 v02**. Google Material Design 3 (Material You) 기반으로 전면 재작성.
> `sync_patcher`, `verify_playwright`, Vision 검증이 모두 이 문서를 참조한다.
> 버전: v02 (2026-05-16) — Material 3 적용

---

## 1. 비주얼 컨셉 한 줄

> **"Google I/O 2026 Keynote — 디자이너를 위한 챕터"**
>
> Material Design 3 (Material You)의 dynamic color · expressive typography · emphasized motion을 기반으로 한 빅테크 키노트 톤. 깊은 다크 surface 위에 expressive purple primary가 흐른다.

**참조 디자인 시스템**: [Material Design 3](https://m3.material.io/) — Google 공식 디자인 시스템 (Android 14+, ChromeOS, Google Workspace 적용)

---

## 2. 글로벌 시각 토큰 — Material 3 Color System

### Surface 톤 (다크 테마, M3 elevation 5단계)

Material 3는 단순 배경/카드가 아니라 **surface elevation**으로 깊이감 표현. 높을수록 더 밝음.

| 토큰 | HEX | M3 매핑 | 용도 |
|------|-----|---------|------|
| `--md-surface` | `#141218` | Surface | 메인 배경 |
| `--md-surface-dim` | `#141218` | Surface Dim | 가장 어두운 면 |
| `--md-surface-bright` | `#3B383E` | Surface Bright | 가장 밝은 면 |
| `--md-surface-container-lowest` | `#0F0D13` | Container Lowest | 가장 낮은 컨테이너 |
| `--md-surface-container-low` | `#1D1B20` | Container Low | 카드 base |
| `--md-surface-container` | `#211F26` | Container | 표준 카드 |
| `--md-surface-container-high` | `#2B2930` | Container High | 강조 카드 |
| `--md-surface-container-highest` | `#36343B` | Container Highest | 최상위 카드 |

### Color Roles — Primary / Secondary / Tertiary (M3 공식 다크 팔레트)

| 토큰 | HEX | M3 Role | 용도 |
|------|-----|---------|------|
| `--md-primary` | `#D0BCFF` | Primary 80 | 핵심 강조 (브랜드 컬러) |
| `--md-on-primary` | `#381E72` | On Primary | Primary 위의 글자 |
| `--md-primary-container` | `#4F378B` | Primary Container | 강조 컨테이너 배경 |
| `--md-on-primary-container` | `#EADDFF` | On Primary Container | 컨테이너 안 글자 |
| `--md-secondary` | `#CCC2DC` | Secondary 80 | 보조 강조 |
| `--md-secondary-container` | `#4A4458` | Secondary Container | 보조 카드 배경 |
| `--md-tertiary` | `#EFB8C8` | Tertiary 80 | 액센트 (희소 사용) |
| `--md-tertiary-container` | `#633B48` | Tertiary Container | 액센트 카드 |

### Text Roles

| 토큰 | HEX | 용도 |
|------|-----|------|
| `--md-on-surface` | `#E6E0E9` | 본문 텍스트 |
| `--md-on-surface-variant` | `#CAC4D0` | 보조 텍스트·캡션 |
| `--md-outline` | `#938F99` | 테두리 |
| `--md-outline-variant` | `#49454F` | 미묘한 테두리 |

### Custom Accents (M3 Extended Color — 통계 임팩트용)

| 토큰 | HEX | 용도 |
|------|-----|------|
| `--md-accent-success` | `#9DCC8A` | 긍정 통계 (성장) |
| `--md-accent-warning` | `#FFB870` | 주의 (S10 한계) |
| `--md-accent-info` | `#A8C7FA` | 정보 콜아웃 |

### Material 3 Gradients (Expressive)

Material 3는 단색보다 dynamic gradient를 적극 사용:
```css
--md-grad-primary:   linear-gradient(135deg, #D0BCFF 0%, #B69DF8 50%, #9A82DB 100%);
--md-grad-vibrant:   linear-gradient(135deg, #D0BCFF 0%, #EFB8C8 100%);  /* primary → tertiary */
--md-grad-stat:      linear-gradient(135deg, #FFB870 0%, #D0BCFF 50%, #A8C7FA 100%);  /* 통계 임팩트 3색 */
--md-mesh-bg:        radial-gradient(ellipse 1400px 900px at 15% 25%, rgba(208,188,255,0.10), transparent 65%),
                     radial-gradient(ellipse 1000px 800px at 85% 75%, rgba(239,184,200,0.06), transparent 60%);
```

---

## 3. Typography — Google Sans + Roboto Flex

### Font Family

- **Display/Heading**: `Google Sans Display` (Google Fonts CDN) — Google 제품 공식
- **Body**: `Google Sans Text` (Google Fonts CDN)
- **Mono/Code**: `Roboto Mono` (Google Fonts CDN)
- **Fallback 한글**: `Pretendard Variable` (한글은 Google Sans가 한국어 미지원이므로 Pretendard로 합성)
- **Icon**: `Material Symbols Outlined` (Google 공식 아이콘 폰트)

### Material 3 Type Scale (영상용 스케일 적용)

Material 3 표준 type scale × 3.0~4.5 (1920×1080 영상이라 확대)

| 역할 | 영상 크기 | 굵기 | 자간 | 행간 |
|------|---------|------|------|------|
| **Display Large** (Hero) | 280pt | 800~900 | -0.04em | 0.95 |
| **Display Medium** | 200pt | 800 | -0.03em | 1.0 |
| **Display Small** | 144pt | 700 | -0.02em | 1.05 |
| **Headline Large** | 96pt | 700 | -0.01em | 1.1 |
| **Headline Medium** | 72pt | 700 | 0 | 1.15 |
| **Headline Small** | 56pt | 600 | 0 | 1.2 |
| **Title Large** | 44pt | 600 | 0.05em | 1.25 |
| **Body Large** | 32pt | 500 | 0.01em | 1.45 |
| **Body Medium** | 28pt | 500 | 0.015em | 1.4 |
| **Label Large** | 24pt | 500 | 0.05em | 1.3 |

**한국어 자막**: Body Large + Pretendard Medium 44pt (영상용 확대)

---

## 4. Shape — Material 3 라운드 시스템

Material 3는 다양한 라운드 토큰을 정의:

| 토큰 | 값 | 용도 |
|------|-----|------|
| `--md-shape-corner-extra-small` | 4px | 미세 요소 |
| `--md-shape-corner-small` | 8px | 칩, 작은 버튼 |
| `--md-shape-corner-medium` | 12px | 카드 표준 |
| `--md-shape-corner-large` | 16px | 큰 카드 |
| `--md-shape-corner-extra-large` | 28px | Hero 카드, 모달 |
| `--md-shape-corner-full` | 9999px | Pill / FAB |

---

## 5. Iconography — Material Symbols (이모지 대신)

이모지 → Material Symbols 매핑 (`material-symbols-outlined` 폰트 클래스):

| 의미 | 이전 (이모지) | 새 (Material Symbol) | 컬러 토큰 |
|------|--------------|----------------------|----------|
| 속도 | ⚡ | `speed` | `--md-primary` |
| 도구 | 🔧 | `build` | `--md-primary` |
| 기억 | 🧠 | `psychology` | `--md-primary` |
| 점검 | 🔍 | `verified` | `--md-primary` |
| Prompt | 🔮 | `auto_awesome` | `--md-primary` |
| Evaluation | 🎯 | `target` (또는 `check_circle`) | `--md-secondary` |
| Design System | ⚙️ | `dashboard_customize` | `--md-tertiary` |
| 경고 | ⚠️ | `warning` | `--md-accent-warning` |
| 재생 | ▶ | `play_arrow` | `--md-primary` |
| 디자이너 | (없음) | `palette` | `--md-tertiary` |
| 코드 | (없음) | `code` | `--md-primary` |
| 자율 | (없음) | `bolt` | `--md-tertiary` |
| 트렌드 | (없음) | `trending_up` | `--md-accent-success` |
| 시간 | (없음) | `schedule` | `--md-on-surface-variant` |

**사용 예시**:
```html
<span class="material-symbols-outlined">speed</span>
<!-- font-variation-settings 로 옵션 제어 -->
<style>
  .material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 48;
  }
</style>
```

---

## 6. Motion — Material 3 Emphasized Easing

Material 3는 5가지 표준 이징을 정의:

| Material 3 Name | cubic-bezier | 용도 |
|----------------|--------------|------|
| **Emphasized** | `cubic-bezier(0.2, 0, 0, 1)` | 메인 모션 (등장·강조) |
| **Emphasized Decelerate** | `cubic-bezier(0.05, 0.7, 0.1, 1)` | 등장 (느려지며) |
| **Emphasized Accelerate** | `cubic-bezier(0.3, 0, 0.8, 0.15)` | 퇴장 (빨라지며) |
| **Standard** | `cubic-bezier(0.2, 0, 0, 1)` | 표준 |
| **Linear** | `cubic-bezier(0, 0, 1, 1)` | 카운트업·진행도 |

**GSAP 매핑**:
```js
const M3_EASE = {
  emphasized: "cubic-bezier(0.2, 0, 0, 1)",
  emphasized_decelerate: "cubic-bezier(0.05, 0.7, 0.1, 1)",
  emphasized_accelerate: "cubic-bezier(0.3, 0, 0.8, 0.15)",
  spring_gentle: "back.out(1.2)",  // M3 spring effect
  spring_bouncy: "elastic.out(1, 0.6)"
};
```

**표준 duration (Material 3 Motion Spec)**:
- Short: 100~200ms (작은 상태 변화)
- Medium: 250~400ms (표준 등장)
- Long: 500~700ms (큰 컴포넌트)
- Extra Long: 800~1000ms (Hero 모먼트)

---

## 7. Components — Material 3 Building Blocks

### Card 종류
1. **Filled Card** (`--md-surface-container`) — 가장 자주 사용. flat, 테두리 없음
2. **Elevated Card** (`--md-surface-container-low` + shadow) — 떠 보이는 느낌
3. **Outlined Card** (`--md-surface` + `--md-outline-variant` 1px border) — 미니멀

### Chip / Pill
- 라운드 full, padding 12px 24px
- Filled: `--md-secondary-container` 배경
- Outlined: 테두리만

### Stat Hero (S05 통계 콜아웃 전용)
- 거대 숫자 (Display Large 280pt) + `--md-grad-stat` 그라데이션 적용
- 라벨은 Headline Small + `--md-on-surface-variant`
- 좌측에 작은 supporting data card 2~3개 배치

---

## 8. 자막 스타일 — Material 3 Surface Tone

- 위치: 하단 중앙, Y=940px 베이스라인
- 박스: M3 surface-container-high tone + glass blur
  ```css
  background: rgba(43, 41, 48, 0.78);
  backdrop-filter: blur(24px) saturate(150%);
  border: 1px solid var(--md-outline-variant);
  border-radius: 12px;  /* corner-medium */
  padding: 14px 28px;
  ```
- 글자: `--md-on-surface` Pretendard Medium 44pt, letter-spacing -0.01em, line-height 1.3
- 한 줄 최대 22자, 줄바꿈 2줄

---

## 9. 씬별 비주얼 디렉션 — Material 3 Reinterpreted

### S01 — 인트로 (Hero Display Moment)
- **무드**: Google I/O Keynote 오프닝, Expressive
- **컬러**: Surface deep + Primary 80 그라데이션
- **핵심 비주얼**: Display Large 280pt "VIBE / CODING" + `--md-grad-primary` 적용. 좌하단에 작은 `palette` 아이콘 + "Designer Edition" 캡션
- **추가 보강 (v02)**: 우상단에 Material Symbols `auto_awesome` 작게 페이드인 (강조 시 글로우)

### S02 — 정의 (Karpathy Quote Card)
- **무드**: 권위·신뢰 (Material Elevated Card)
- **컬러**: Container-high surface, Primary 인용부 강조
- **핵심 비주얼**: Elevated Card 안에 인용 + 우측 노드 플로우 (자연어 → AI → 코드 → 결과). 각 노드는 Filled Chip 스타일

### S03 — 3가지 이유 (M3 Card Variants)
- **무드**: 정돈, 위계
- **컬러**: 카드 3개 — Filled / Elevated / Outlined 변형으로 서로 다른 톤
- **핵심 비주얼**: Bento → M3 grid card system
  - 좌측 큰 카드 (속도): Filled, `--md-primary-container` 배경, `speed` 아이콘
  - 우측 상 (동작 시안): Elevated, `--md-secondary-container`, `bolt` 아이콘
  - 우측 하 (자율): Outlined, `palette` 아이콘

### S04 — 도구 4종 (M3 Filled Cards)
- **무드**: 제품 카탈로그
- **컬러**: 4개 도구 카드 — primary container 톤. 각 도구별로 약간씩 색조 변형 (M3 tonal palette 활용)
- **핵심 비주얼**: 2×2 grid M3 Filled Card
  - v0: `code` icon, primary tone
  - Lovable: `favorite` icon, tertiary tone
  - Cursor: `cursor_click` icon, secondary tone
  - Bolt: `bolt` icon, accent-warning tone
- **추가 보강 (v02)**: 각 카드 우상단에 작은 "by..." chip (Vercel/Stripe-style attribution)

### S05 — 통계 (M3 Data Visualization) ⭐ **대폭 보강**
- **무드**: 데이터 임팩트, 빅테크 리포트 톤
- **컬러**: `--md-grad-stat` (3색 그라데이션) Hero 숫자, supporting data는 surface-container-high
- **핵심 비주얼 (v02 신규)**:
  1. **거대 "10×" 카운트업** — 0 → 10 카운트업 with Display Large 280pt
  2. **2단 막대 비교** — 전통 (며칠) vs 바이브 (분), 차오를 때 우측 시간 라벨 동시 카운트업
  3. **NEW: 좌측 supporting cards** (2~3개 미니 카드)
     - "AI 코딩 도구 채택" + Material `trending_up` + "+200%"
     - "디자이너 코드 시간" + Material `schedule` + "-60%"
     - "프로토타입 → 배포" + Material `rocket_launch` + "3일 → 30분"
  4. 출처 caption 우하단

### S06 — 워크플로우 비교 (M3 Flow Diagram)
- **무드**: 명확한 대조
- **컬러**: 좌 = surface-container-low + on-surface-variant (무채), 우 = primary-container + on-primary-container (강조)
- **핵심 비주얼**: 좌우 분할 노드 그래프. 노드는 M3 Pill (Chip) 스타일. 화살표는 Material `arrow_downward` 아이콘
- **추가 보강 (v02)**: 시간 라벨 옆에 `schedule` 아이콘

### S07 — Figma → v0 (3단 Surface Composition)
- **무드**: 시연·"되는구나"
- **컬러**: 좌 = secondary container (Figma 톤), 중앙 화살표 = primary, 우 = primary container (코드 결과)
- **핵심 비주얼**: 3단 grid, 가운데 큰 `arrow_forward` Material Symbol. Figma panel은 도형 placeholders, v0 panel은 코드 모노 텍스트

### S08 — 텍스트 → UI (Live Demo Card)
- **무드**: 마법 같은 시연, 인터랙티브
- **컬러**: 좌측 프롬프트 = surface-container-high + primary 강조, 우측 결과 UI = elevated card with mesh gradient bg
- **핵심 비주얼**: 좌측 타이프라이터 프롬프트 박스 + 우측 결과 UI 미니어처 (M3 컴포넌트 mockup으로 — App bar / FAB / Card / Bottom navigation 작게 표현)
- **추가 보강 (v02)**: 우측 UI 위에 작은 chip "Generated in 12s" 표시

### S09 — 새 스킬 (M3 Pill Chips)
- **무드**: 진지, 가치 전달
- **컬러**: 3개 칩 각각 다른 container 톤 (primary / secondary / tertiary)
- **핵심 비주얼**: M3 Filled Pill 3개 stagger. 각 칩 좌측에 Material Symbol (`auto_awesome`, `target`, `dashboard_customize`)

### S10 — 한계 (Warning Surface)
- **무드**: 균형, 솔직
- **컬러**: `--md-accent-warning` 톤
- **핵심 비주얼**: 중앙에 거대 `warning` Material Symbol + Headline 타이틀 + 리스트 (Material List item 스타일, 좌측 `cancel` 작은 아이콘)

### S11 — 미래/CTA (Hero Closing + FAB-style CTA)
- **무드**: 시그너처 마무리
- **컬러**: Mesh gradient bg + `--md-grad-primary` 거대 카피
- **핵심 비주얼**: Display Medium 카피 + 하단 M3 Extended FAB 스타일 CTA 카드 (`play_arrow` + "v0 실습 · 30분")

---

## 10. 빈 구간 채우기 전략 (v02 신규)

v01에서 비어 보였던 구간들:

| 씬 | 비어 보이던 구간 | v02 보강 |
|----|----------------|---------|
| S04 (47s~) | 46.9s ~ 50.6s (첫 도구 등장 전) | 타이틀 "디자이너의 새 도구 4종"이 천천히 페이드인하며 작은 `category` 아이콘 등장 |
| S05 (63s~) | 63.5s ~ 72.9s (10× 카운트업 전) | 좌측 supporting cards 3개가 stagger로 먼저 등장 |
| S07 (99s~) | 99.3s ~ 102s | 좌측 Figma panel이 살짝 일찍 등장, 화살표 부분에 작은 펄스 |
| S08 (116s~) | 116.3s ~ 119s | 프롬프트 박스 컨테이너가 발화 직전 페이드인 |

---

## 11. 발화-모션 싱크 룰 (v02 — global offset -0.20s)

**v02 핵심 변경**: 모든 룰에 global offset `-0.20s` 적용 — 모션이 발화보다 200ms 일찍 시작해 사용자 인지상 자연스러운 싱크 ("발화 시점에 등장 애니메이션이 80% 진행된 상태").

| 씬 | event_id | trigger_word | strategy | offset (v02) | 의도 |
|----|----------|--------------|----------|-------------|------|
| S01 | `s01-title-in` | 디자 | scene | -0.20 | VIBE/CODING 타이포 등장 |
| S01 | `s01-keyword-bibe` | 바이 | scene | -0.20 | 바이브 코딩 강조 |
| S02 | `s02-karpathy-in` | 카파시 | scene | -0.20 | Karpathy 카드 등장 |
| S02 | `s02-flow-start` | 자연 | scene | -0.20 | 4단 플로우 시작 |
| S03 | `s03-reason-1` | 속도 | scene | -0.20 | 첫 카드 |
| S03 | `s03-reason-2` | 동작 | scene | -0.20 | 두번째 카드 |
| S03 | `s03-reason-3` | 콘셉트 | scene | -0.20 | 세번째 카드 |
| S04 | `s04-tool-v0` | V0 | scene | -0.20 | v0 카드 |
| S04 | `s04-tool-cursor` | 커서 | scene | -0.20 | Cursor 카드 |
| S04 | `s04-tool-bolt` | 볼트 | scene | -0.20 | Bolt 카드 |
| S05 | `s05-num-callout` | 10배 | scene | -0.30 | 10× 카운트업 시작 |
| S05 | `s05-bars-start` | 짧아 | scene | -0.40 | 막대 grow 시작 |
| S06 | `s06-traditional` | 전통 | scene | -0.20 | 좌측 시작 |
| S06 | `s06-vibe-flow` | 바이 | scene | -0.20 | 우측 시작 |
| S07 | `s07-figma` | 피금 | scene | -0.30 | Figma panel |
| S07 | `s07-result` | 리액트 | scene | -0.20 | 결과 panel |
| S08 | `s08-prompt-typing` | 데시 | scene | -0.30 | 타이프라이터 시작 |
| S08 | `s08-ui-appear` | 넌트 | scene | -0.20 | UI 결과 |
| S09 | `s09-skill-1` | 프프트 | scene | -0.20 | Prompt 칩 |
| S09 | `s09-skill-2` | 평가 | scene | -0.20 | Evaluation 칩 |
| S09 | `s09-skill-3` | 시스 | scene | -0.20 | Design System 칩 |
| S10 | `s10-warn-in` | 물론 | scene | -0.20 | warning 등장 |
| S11 | `s11-closing` | 경계 | scene | -0.20 | 마무리 카피 |
| S11 | `s11-cta-card` | 다음영상 | scene | -0.20 | CTA 카드 |

**매칭 실패 (그대로 GSAP 추정값 사용)**:
- `s04-tool-lovable` — "러버블" 받아쓰기 누락

---

## 12. 자동 품질 체크리스트

`도구/verify_playwright` 자동 검사:
- [ ] 모든 `@sync:` 모션이 발화 시점과 ±0.15초 이내
- [ ] 한 시점에 active 한 `.scene` 컨테이너 1개
- [ ] 자막 한 줄 22자 이하
- [ ] Material Symbols 폰트가 정상 로딩 (글리프 누락 없음)
- [ ] 그라데이션이 메인 강조에만 적용됨 (본문 텍스트는 단색)

`도구/verify_vision` Vision LLM 검사:
- [ ] **Material 3 무드** — Google 제품의 톤이 살아 있는가
- [ ] Surface elevation 단계가 시각적으로 구분되는가
- [ ] 이모지 흔적 없이 Material Symbols만 사용되는가
- [ ] 빈 구간 없이 모든 시점에 시각 요소가 있는가
- [ ] 발화 키워드 ↔ 화면 강조 키워드 일치
- [ ] 통계 씬에 충분한 데이터 시각화 요소 (단순 "10×"만 있지 않음)

---

## 13. 참조 무드보드

- **Google I/O 2024-2025 Keynote** — 다크 모드 surface + Primary purple expressive
- **Material Design 3 Showcase** ([m3.material.io](https://m3.material.io)) — 공식 컴포넌트 라이브러리
- **Google Workspace Updates** — Card 시스템과 typography 위계
- **Material Symbols Library** ([fonts.google.com/icons](https://fonts.google.com/icons)) — 이 영상의 모든 아이콘 출처

이 영상은 위 4개의 톤을 한국 디자이너 시청자에게 어울리는 한글 타이포(Pretendard)와 결합해야 함.
