#!/usr/bin/env bash
# Run a lesson's lab, or any course script, with the course Python environment.
#
#   ./lab.sh list                     show all labs
#   ./lab.sh 08/L01                   run Module 08, lesson L01 with default settings
#   ./lab.sh 08/L01 help              list the settings this lab lets you change
#   ./lab.sh 08/L01 action_noise=0.3  change one setting (results are kept per setting)
#   ./lab.sh py <script.py> [args]    run any script with duckkit available
#   ./lab.sh doctor [--full]          check the environment
#
# On Windows use `.\lab ...` (lab.cmd), which runs this script inside WSL.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_SH="$ROOT/.course/env.sh"
if [[ ! -f "$ENV_SH" ]]; then
  echo "The course environment is not set up yet. Run ./setup.sh (Windows: .\setup) first." >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$ENV_SH"
if [[ ! -x "${COURSE_PYTHON:-}" ]]; then
  echo "Course Python not found at '${COURSE_PYTHON:-}'. Re-run ./setup.sh." >&2
  exit 1
fi
export COURSE_ROOT="$ROOT"
export PYTHONPATH="$ROOT/LearningProgress/_shared${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
MODULES="$ROOT/LearningProgress"

cmd="${1:-list}"
case "$cmd" in
  list)
    echo "Labs (run with: lab <module>/<lesson> [key=value ...]):"
    found=0
    for f in "$MODULES"/[0-9][0-9]-*/lessons/L*/lab.py; do
      [[ -e "$f" ]] || continue
      d=$(dirname "$f"); m=$(basename "$(dirname "$(dirname "$d")")"); l=$(basename "$d")
      echo "  ${m%%-*}/${l%%-*}   $m / $l"
      found=1
    done
    [[ $found -eq 1 ]] || echo "  (none yet: the teaching agent creates labs as lessons are prepared)"
    ;;
  doctor)
    shift
    exec "$COURSE_PYTHON" -B "$ROOT/tools/doctor.py" "$@"
    ;;
  py)
    shift
    [[ $# -ge 1 ]] || { echo "usage: lab py <script.py> [args]" >&2; exit 1; }
    [[ -f "$1" ]] || { echo "No such script: $1" >&2; exit 1; }
    script_dir="$(cd "$(dirname "$1")" && pwd)"; script="$script_dir/$(basename "$1")"; shift
    cd "$script_dir"
    exec "$COURSE_PYTHON" -B "$script" "$@"
    ;;
  -h|--help|help)
    sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    ;;
  */*)
    module="${cmd%%/*}"; lesson="${cmd#*/}"; shift
    matches=( "$MODULES"/"$module"-*/lessons/"$lesson"*/lab.py )
    if [[ ! -e "${matches[0]}" ]]; then
      echo "No lab found for $module/$lesson. Try: lab list" >&2
      exit 1
    fi
    cd "$(dirname "${matches[0]}")"
    exec "$COURSE_PYTHON" -B lab.py "$@"
    ;;
  *)
    echo "Unknown command '$cmd'. Try: lab help" >&2
    exit 1
    ;;
esac
