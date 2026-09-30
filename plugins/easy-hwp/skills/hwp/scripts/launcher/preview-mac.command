#!/bin/bash
# claw-hwp local preview launcher (macOS)
# Place this next to a .hwp/.hwpx file and double-click. Or pass a file path.
set -e

cd "$(dirname "$0")"

FILE="${1:-}"
if [ -z "$FILE" ]; then
  FILE=$(ls -t *.hwp *.hwpx 2>/dev/null | head -1)
fi
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "❌ No .hwp/.hwpx file found next to this script."
  echo "   Drop one in the same folder, or pass a path as argument."
  read -p "Press Enter to close..."
  exit 1
fi
FILE_ABS="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"

if ! command -v node >/dev/null 2>&1; then
  echo "❌ Node.js 18+ required. Install from https://nodejs.org/"
  read -p "Press Enter to close..."
  exit 1
fi

SERVER=$(find "$HOME/.claude/plugins/cache" -path '*/claw-hwp/*/skills/hwp/scripts/preview-server.js' 2>/dev/null | sort -V | tail -1)
if [ -z "$SERVER" ]; then
  CACHE="$HOME/.claw-hwp-launcher"
  SERVER="$CACHE/scripts/preview-server.js"
  if [ ! -f "$SERVER" ]; then
    echo "⏬ First run — downloading preview server (~5MB) from GitHub..."
    mkdir -p "$CACHE"
    curl -fsSL https://codeload.github.com/DoHyun468/claw-hwp/tar.gz/main \
      | tar -xz -C "$CACHE" --strip-components=5 \
        claw-hwp-main/plugins/claw-hwp/skills/hwp/scripts \
      || { echo "❌ Download failed."; read -p "Press Enter to close..."; exit 1; }
  fi
fi

if ! curl -fsS -o /dev/null http://127.0.0.1:3737/__heartbeat 2>/dev/null; then
  echo "🚀 Starting preview server..."
  node "$SERVER" >/tmp/claw-hwp-preview.log 2>&1 &
  disown 2>/dev/null || true
  for i in 1 2 3 4 5 6 7 8; do
    sleep 0.3
    curl -fsS -o /dev/null http://127.0.0.1:3737/__heartbeat 2>/dev/null && break
  done
fi

URL_PATH=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$FILE_ABS" 2>/dev/null \
  || printf '%s' "$FILE_ABS" | sed 's/ /%20/g')
URL="http://localhost:3737/?path=$URL_PATH"
echo "✅ Opening $URL"
open "$URL"
