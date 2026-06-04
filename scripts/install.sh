#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$script_dir/.." && pwd)
mise_bin="$root/.cache/mise/bin/mise"

export MISE_DATA_DIR="$root/.cache/mise/data"
export MISE_CACHE_DIR="$root/.cache/mise/cache"
export MISE_TMP_DIR="$root/.cache/mise/tmp"

if command -v mise >/dev/null 2>&1; then
  mise_bin=$(command -v mise)
elif [ ! -x "$mise_bin" ]; then
  mkdir -p "$(dirname "$mise_bin")"

  if command -v curl >/dev/null 2>&1; then
    curl https://mise.run | MISE_INSTALL_PATH="$mise_bin" sh
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://mise.run | MISE_INSTALL_PATH="$mise_bin" sh
  else
    echo "curl or wget is required to install mise." >&2
    exit 1
  fi
fi

mkdir -p "$MISE_DATA_DIR" "$MISE_CACHE_DIR" "$MISE_TMP_DIR"
"$mise_bin" install --locked
"$mise_bin" run bootstrap
