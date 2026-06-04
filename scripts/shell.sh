#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$script_dir/.." && pwd)
shell_dir="$root/.cache/shell"
zshrc="$shell_dir/.zshrc"

mkdir -p "$shell_dir"

cat > "$zshrc" <<EOF
if [ -f "\$HOME/.zshrc" ]; then
  source "\$HOME/.zshrc"
fi

if [ -f "$root/scripts/activate.sh" ]; then
  source "$root/scripts/activate.sh" || echo "Project activation skipped. Run ./scripts/install.sh, then source ./scripts/activate.sh."
fi
EOF

ZDOTDIR="$shell_dir" exec zsh -i
