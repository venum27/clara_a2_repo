#!/usr/bin/env bash
# Readiness check: packages, GPUs, both backbones (downloaded if missing), the synthesiser, both datasets.
# Writes setup_report.txt.
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
"$PY" check_setup.py 2>&1 | grep -v -E "^\s*warnings.warn|FutureWarning|UserWarning"
