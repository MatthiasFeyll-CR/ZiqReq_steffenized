#!/usr/bin/env bash
set -euo pipefail

echo "=== Frontend tests ==="
cd "$(dirname "$0")/../frontend"
npm test

echo ""
echo "=== Gateway tests ==="
cd "$(dirname "$0")/../services/gateway"
python -m pytest

echo ""
echo "=== Core tests ==="
cd "$(dirname "$0")/../services/core"
python -m pytest

echo ""
echo "All tests passed."
