#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$REPO/.app-store-audit"
mkdir -p "$OUT"
python3 "$SCRIPT_DIR/app_store_static_scan.py" --repo "$REPO" --out "$OUT"
echo ""
echo "Audit scan complete. Open: $OUT/app-store-static-scan.md"
