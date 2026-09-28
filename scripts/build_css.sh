#!/bin/sh
# Build Tailwind CSS with the standalone CLI — no node/npm (design-log: no frontend build pipeline).
# Usage: scripts/build_css.sh        → one-off minified build
#        scripts/build_css.sh --watch → rebuild on change
set -e
cd "$(dirname "$0")/.."

TAILWIND_VERSION=v4.1.13
BIN="bin/tailwindcss"

if [ ! -x "$BIN" ]; then
  echo "Downloading Tailwind standalone CLI $TAILWIND_VERSION..."
  mkdir -p bin
  curl -sL -o "$BIN" "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/tailwindcss-linux-x64"
  chmod +x "$BIN"
fi

if [ "$1" = "--watch" ]; then
  exec "$BIN" -i static/css/src/input.css -o static/css/app.css --watch
fi

"$BIN" -i static/css/src/input.css -o static/css/app.css --minify
