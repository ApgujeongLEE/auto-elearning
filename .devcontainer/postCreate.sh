#!/usr/bin/env bash
# ============================================================
# Codespaces postCreate hook
# ============================================================
# devcontainer.json의 postCreateCommand에서 호출됨.
# Codespaces 환경 (Ubuntu)용 의존성 설치.
# ============================================================
set -euo pipefail

echo "🚀 Auto E-learning Codespaces 환경 셋업"
echo ""

# ---------- 1. apt 패키지 (ffmpeg, build tools) ----------
echo "📦 시스템 패키지 설치..."
sudo apt-get update -qq
sudo apt-get install -y -qq ffmpeg build-essential cmake git curl ca-certificates
echo "✓ ffmpeg: $(ffmpeg -version 2>&1 | head -1)"

# ---------- 2. whisper.cpp 빌드 ----------
# Linux용 whisper-cli는 brew가 아니라 소스에서 빌드
WHISPER_DIR="$HOME/.local/whisper.cpp"
if [[ ! -f "$WHISPER_DIR/build/bin/whisper-cli" ]]; then
  echo ""
  echo "🤖 whisper.cpp 소스 빌드..."
  mkdir -p "$HOME/.local"
  if [[ ! -d "$WHISPER_DIR" ]]; then
    git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
  fi
  cd "$WHISPER_DIR"
  cmake -B build -DGGML_OPENMP=OFF
  cmake --build build --config Release -j $(nproc)
  cd -
  echo "✓ whisper-cli built: $WHISPER_DIR/build/bin/whisper-cli"
fi

# PATH에 추가
if ! grep -q "whisper.cpp/build/bin" "$HOME/.bashrc"; then
  echo "export PATH=\"$WHISPER_DIR/build/bin:\$PATH\"" >> "$HOME/.bashrc"
fi
export PATH="$WHISPER_DIR/build/bin:$PATH"

# ---------- 3. Whisper 모델 ----------
MODEL_DIR="$HOME/.cache/whisper-models"
MODEL_FILE="$MODEL_DIR/ggml-small.bin"
mkdir -p "$MODEL_DIR"
if [[ ! -f "$MODEL_FILE" ]]; then
  echo ""
  echo "📥 Whisper small 모델 다운로드 (~466 MB)..."
  curl -L --progress-bar -o "$MODEL_FILE" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
  echo "✓ 모델 저장: $MODEL_FILE"
fi

# ---------- 4. Playwright (DOM 검증용) ----------
echo ""
echo "🎭 Playwright 설치..."
cd "$(git rev-parse --show-toplevel)/도구/verify-playwright"
npm install --silent
npx playwright install --with-deps chromium
cd - > /dev/null

# ---------- 5. 검증 ----------
echo ""
echo "🔍 환경 검증..."
for cmd in ffmpeg node npx python3 whisper-cli; do
  if command -v "$cmd" &>/dev/null; then
    echo "  ✓ $cmd ($(command -v $cmd))"
  else
    echo "  ❌ $cmd 미설치"
  fi
done

echo ""
echo "🎉 Codespaces 환경 준비 완료!"
echo ""
echo "포워딩된 포트:"
echo "  - 3002 → Hyperframes Studio (https URL 자동 발급)"
echo ""
echo "시작:"
echo "  cd 프로젝트/<프로젝트명>/06_편집/hyperframes"
echo "  npm run dev"
