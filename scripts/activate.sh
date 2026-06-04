#!/usr/bin/env zsh

script_path="${(%):-%N}"
script_dir="${script_path:A:h}"
root="${script_dir:h}"
mise_dir="$root/.cache/mise/bin"

export MISE_DATA_DIR="$root/.cache/mise/data"
export MISE_CACHE_DIR="$root/.cache/mise/cache"
export MISE_TMP_DIR="$root/.cache/mise/tmp"
mkdir -p "$MISE_DATA_DIR" "$MISE_CACHE_DIR" "$MISE_TMP_DIR"

if [[ ! -x "$mise_dir/mise" ]] && ! command -v mise >/dev/null 2>&1; then
  echo "mise was not found. Run ./scripts/install.sh first." >&2
  return 1
fi

case ":$PATH:" in
  *":$mise_dir:"*) ;;
  *) export PATH="$mise_dir:$PATH" ;;
esac

if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh)"
fi

if [[ -z "${ASSETS_MISE_PROMPT_ACTIVE:-}" ]]; then
  export ASSETS_MISE_PROMPT_ACTIVE=1
  export ASSETS_MISE_ORIG_PROMPT="${PROMPT:-}"
  PROMPT="%F{cyan}(Assets)%f ${PROMPT:-%n@%m %1~ %# }"
fi
