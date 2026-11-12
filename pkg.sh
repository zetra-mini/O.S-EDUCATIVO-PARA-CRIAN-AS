#!/usr/bin/env bash
# Wrapper de compatibilidade para './pkg.sh'
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/pkg" "$@"
