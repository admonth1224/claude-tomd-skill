#!/usr/bin/env bash
# tomd skill installer (macOS / Linux)
# Usage:  bash install.sh
set -euo pipefail

echo "==> tomd 스킬 설치 시작"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/tomd"
DEST="$HOME/.claude/skills/tomd"

# 1) Python 확인
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "Python을 찾을 수 없습니다. python3 설치 후 다시 실행하세요." >&2
  exit 1
fi

# 2) 의존성 설치
echo "==> Python 의존성 설치 중 (markitdown[all], pyhwp)..."
"$PY" -m pip install -r "$REPO_ROOT/requirements.txt"

# 3) 스킬 복사
echo "==> 스킬 복사: $DEST"
mkdir -p "$DEST"
cp -R "$SRC/." "$DEST/"

echo ""
echo "✅ 설치 완료!"
echo "   Claude Code에서 다음처럼 사용하세요:  /tomd <파일명>"
echo "   (Claude Code가 실행 중이면 한 번 재시작하면 /tomd 가 인식됩니다.)"
