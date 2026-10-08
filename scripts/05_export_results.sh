#!/usr/bin/env bash
# Collect all results into a small text-only folder + archive (no checkpoints) and print every table.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
"$PY" export_results.py --name flair2
cat results_export/flair2/results_summary.md
cat << MSG

Getting the results off the server (pick whatever is easiest):
  * copy-paste the tables printed above, or:  cat results_export/flair2/results_summary.md
  * push to the team's GitHub repo:  git add results_export/flair2 && git commit -m "results" && git push
  * download the one archive:        results_export/flair2.tar.gz
Checkpoints stay in runs/ on the server for the viva demo.
MSG
