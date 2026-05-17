# Hyperframes 공통 자원

여러 프로젝트에서 공유하는 Hyperframes 설정·어댑터·스니펫 보관소.

---

## 구조

- `shared_adapters/` — 커스텀 프레임 어댑터 (필요 시 추가)
- (`package.json`) — 공용 의존성. 모노레포 워크스페이스로 구성할 경우 추가

---

## 사용 방법

각 프로젝트의 `06_편집/hyperframes/`는 `npx hyperframes init`로 독립적으로 생성된다. 공용 자원이 필요하면 심볼릭 링크로 참조:

```bash
cd 프로젝트/NNN_xxx/06_편집/hyperframes/
ln -s ../../../../공용자산/hyperframes_공통/shared_adapters scripts/shared_adapters
```

---

## 신규 어댑터 추가 시

1. `shared_adapters/` 에 어댑터 파일 추가
2. `CHANGELOG.md` 에 어댑터 이름·용도·추가일 기록
3. 적용 가능한 진행 중 프로젝트에 알림
