#!/usr/bin/env bash
# ============================================================
# Auto E-learning Workspace Setup (macOS)
# ============================================================
# 다른 macOS PC에서 이 워크스페이스를 처음 사용할 때 실행.
# brew, ffmpeg, node@22, whisper-cpp, playwright, whisper 모델까지 자동 설치.
#
# 사용: bash setup.sh
# ============================================================
set -euo pipefail

echo "🚀 Auto E-learning workspace setup 시작"
echo ""

# ---------- 1. Homebrew ----------
if ! command -v brew &>/dev/null; then
  echo "📦 Homebrew 설치 중..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo "✅ Homebrew 설치 완료"
else
  echo "✓ Homebrew 이미 설치됨 ($(brew --version | head -1))"
fi

# Apple Silicon vs Intel Mac PATH
if [[ -d /opt/homebrew/bin ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -d /usr/local/bin ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

# ---------- 2. Core CLI tools ----------
echo ""
echo "🛠  CLI 도구 설치 (ffmpeg, node@22, whisper-cpp, python)..."
brew install ffmpeg node@22 whisper-cpp || true
brew link --overwrite --force node@22 || true

NODE_PATH=$(brew --prefix node@22)/bin
if ! grep -q "node@22/bin" "$HOME/.zprofile" 2>/dev/null; then
  echo "export PATH=\"$NODE_PATH:\$PATH\"" >> "$HOME/.zprofile"
  echo "  → ~/.zprofile에 node@22 PATH 추가"
fi
export PATH="$NODE_PATH:$PATH"

echo "✓ ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
echo "✓ node:   $(node --version)"
echo "✓ whisper-cli: $(which whisper-cli || echo 'NOT FOUND')"

# ---------- 3. Whisper model ----------
MODEL_DIR="$HOME/.cache/whisper-models"
MODEL_FILE="$MODEL_DIR/ggml-small.bin"
mkdir -p "$MODEL_DIR"
if [[ ! -f "$MODEL_FILE" ]]; then
  echo ""
  echo "🤖 Whisper small 모델 다운로드 (~466 MB)..."
  curl -L -o "$MODEL_FILE" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
  echo "✅ 모델 저장: $MODEL_FILE"
else
  echo "✓ Whisper 모델 이미 존재: $MODEL_FILE"
fi

# ---------- 4. Playwright (DOM 검증용) ----------
echo ""
echo "🎭 Playwright + Chromium 설치..."
cd "$(dirname "$0")/도구/verify-playwright"
npm install --silent
npx playwright install chromium
cd - > /dev/null
echo "✅ Playwright ready"

# ---------- 5. Python 의존성 (sync_patcher 는 standard lib만 사용) ----------
echo ""
echo "🐍 Python 확인..."
python3 --version
echo "✓ sync_patcher.py는 표준 라이브러리만 사용 — 추가 설치 불필요"

# ---------- 6. 검증 ----------
echo ""
echo "🔍 환경 검증..."
ERRORS=0
for cmd in ffmpeg node npx python3 whisper-cli; do
  if command -v "$cmd" &>/dev/null; then
    echo "  ✓ $cmd"
  else
    echo "  ❌ $cmd 미설치"
    ERRORS=$((ERRORS+1))
  fi
done

echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "🎉 Setup 완료. 다음 단계:"
  echo ""
  echo "  1. 새 셸을 열거나 'source ~/.zprofile' 로 PATH 적용"
  echo "  2. 새 프로젝트 시작:"
  echo "       cp -r _템플릿 \"프로젝트/NNN_slug_\$(date +%Y-%m-%d)\""
  echo "  3. README.md 의 워크플로우 따라 진행"
else
  echo "⚠️  $ERRORS 개 도구 미설치. 위 메시지 확인 후 수동 설치 필요"
  exit 1
fi
