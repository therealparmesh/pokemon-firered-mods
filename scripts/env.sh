#!/usr/bin/env bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v brew >/dev/null 2>&1; then
    BREW_PREFIX="$(brew --prefix)"
    export PATH="$BREW_PREFIX/opt/make/libexec/gnubin:$BREW_PREFIX/bin:$PATH"
    export PKG_CONFIG_PATH="$BREW_PREFIX/opt/libpng/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
export MAKE="${MAKE:-$(command -v gmake || command -v make || true)}"
export LC_ALL=C
