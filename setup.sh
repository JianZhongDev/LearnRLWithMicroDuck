#!/usr/bin/env bash
# Set up everything the course needs: checkouts of the two MicroDuck repositories
# (kept OUTSIDE this repository), a private Python 3.12 environment, and a check
# of compute and rendering support.
#
#   ./setup.sh                    full setup (safe to re-run; it only does what is missing)
#   ./setup.sh --sources DIR      where the MicroDuck checkouts live or should be cloned:
#                                 DIR/microduck_rl and DIR/microduck
#                                 (default: the folder that contains this repository)
#   ./setup.sh --checkout-pinned  switch an existing, clean checkout to the tested commit
#   ./setup.sh --latest           use the newest upstream MicroDuck code instead of the tested commits
#   ./setup.sh --cpu              use the CPU even if an NVIDIA GPU is present
#   ./setup.sh --skip-selftest    do not run the 2-4 minute simulation self-test at the end
#   ./setup.sh --yes              do not ask before installing uv (the Python package manager)
#   ./setup.sh --check            only check the existing setup (same as: ./lab.sh doctor)
#
# Windows: run .\setup in PowerShell or cmd; it runs this script inside WSL 2.
# Nothing is installed system-wide except uv (into ~/.local/bin) if it is missing.
# This repository never contains MicroDuck source code; it only records where the
# checkouts are (.course/env.json).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "$ROOT/tools/pins.env"

say()  { printf '\n==> %s\n' "$*"; }
note() { printf '    %s\n' "$*"; }
die()  { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

CHECK_ONLY=0; FORCE_CPU=0; LATEST=0; SELFTEST=1; ASSUME_YES=0; CHECKOUT_PINNED=0
SOURCES="${MICRODUCK_SOURCES:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) CHECK_ONLY=1 ;;
    --cpu) FORCE_CPU=1 ;;
    --latest) LATEST=1 ;;
    --checkout-pinned) CHECKOUT_PINNED=1 ;;
    --skip-selftest) SELFTEST=0 ;;
    --yes|-y) ASSUME_YES=1 ;;
    --sources) shift; [[ $# -gt 0 ]] || die "--sources needs a folder"; SOURCES="$1" ;;
    --sources=*) SOURCES="${1#--sources=}" ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
  shift
done

if [[ $CHECK_ONLY -eq 1 ]]; then exec bash "$ROOT/lab.sh" doctor; fi

# ---------------------------------------------------------------- 1. platform
say "Checking the platform"
KERNEL="$(uname -s)"; ARCH="$(uname -m)"; OS_KIND=""
case "$KERNEL" in
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then OS_KIND="wsl"; else OS_KIND="linux"; fi ;;
  Darwin) OS_KIND="macos" ;;
  MINGW*|MSYS*|CYGWIN*)
    die "This is a Windows shell (Git Bash/MSYS). Run .\\setup from PowerShell or cmd instead; it uses WSL 2." ;;
  *) die "Unsupported system: $KERNEL" ;;
esac
DISTRO_ID="unknown"
if [[ -r /etc/os-release ]]; then DISTRO_ID="$(. /etc/os-release && echo "${ID:-unknown}")"; fi
note "system: $OS_KIND ($KERNEL $ARCH, $DISTRO_ID)"

if [[ "$OS_KIND" == "macos" ]]; then
  DISTRO_ID="macos"
  if [[ "$(sysctl -n sysctl.proc_translated 2>/dev/null || echo 0)" == "1" ]]; then
    die "This terminal runs under Rosetta (Intel emulation). Open a native Apple Silicon shell first:
       arch -arm64 /bin/zsh        then run ./setup.sh again.
       (Or untick 'Open using Rosetta' in the Terminal app's Get Info window.)"
  fi
  if [[ "$ARCH" != "arm64" ]]; then
    die "Intel Macs are not supported: the simulation library (NVIDIA Warp) no longer ships Intel macOS builds.
       Use an Apple Silicon Mac, or a Linux/Windows machine."
  fi
  xcode-select -p >/dev/null 2>&1 \
    || die "Apple's command line tools are required (they provide git). Run:  xcode-select --install"
  note "Apple Silicon: the robot simulation runs on the CPU (no NVIDIA GPU; the simulation library has"
  note "no Apple-GPU backend). Neural-network-only lessons can use the Apple GPU through PyTorch MPS."
fi

install_hint() {  # $1 = packages for apt, $2 = for dnf/pacman, $3 = for brew
  case "$DISTRO_ID" in
    ubuntu|debian|linuxmint|pop) echo "sudo apt update && sudo apt install -y $1" ;;
    fedora|rhel|centos|rocky|almalinux) echo "sudo dnf install -y $2" ;;
    arch|manjaro) echo "sudo pacman -S --needed $2" ;;
    macos) echo "xcode-select --install   (or: brew install $3)" ;;
    *) echo "install: $1" ;;
  esac
}
for tool in git curl; do
  command -v "$tool" >/dev/null 2>&1 \
    || die "'$tool' is required. Install it with:  $(install_hint "git curl ca-certificates" "git curl" "git curl")"
done

# ---------------------------------------------------------------- 2. uv
say "Checking uv (Python package manager)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  if [[ $ASSUME_YES -eq 0 && -t 0 ]]; then
    read -r -p "    uv is not installed. Install it into ~/.local/bin now? [Y/n] " reply
    [[ -z "$reply" || "$reply" =~ ^[Yy] ]] \
      || die "uv is required. See https://docs.astral.sh/uv/getting-started/installation/"
  fi
  note "installing uv from https://astral.sh/uv/install.sh"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
  command -v uv >/dev/null 2>&1 || die "uv installation did not put 'uv' on PATH (~/.local/bin)."
fi
note "$(uv --version)"

# ---------------------------------------------------------------- 3. sources
say "Locating the MicroDuck source code (kept outside this repository, used read-only)"
# A Windows path such as D:\Code given through .\setup needs translating inside WSL.
if [[ "$SOURCES" =~ ^[A-Za-z]:[\\/] ]] && command -v wslpath >/dev/null 2>&1; then
  SOURCES="$(wslpath -u "$SOURCES")"
fi
if [[ -z "$SOURCES" && -f "$ROOT/.course/env.sh" ]]; then
  # Re-running setup: keep the location chosen before.
  PREVIOUS="$( (source "$ROOT/.course/env.sh" >/dev/null 2>&1; echo "${MICRODUCK_RL_REPO:-}") )"
  if [[ -n "$PREVIOUS" && -d "$PREVIOUS" ]]; then SOURCES="$(dirname "$PREVIOUS")"; fi
fi
if [[ -z "$SOURCES" ]]; then SOURCES="$(dirname "$ROOT")"; fi
INSIDE_MSG="The MicroDuck checkouts must live outside this repository. Choose another folder with --sources DIR."
case "$SOURCES" in /*) ;; *) SOURCES="$PWD/$SOURCES" ;; esac
case "$SOURCES/" in "$ROOT"/*) die "$INSIDE_MSG" ;; esac        # checked before creating anything
mkdir -p "$SOURCES" 2>/dev/null || die "Cannot create '$SOURCES'. Choose another folder with --sources DIR."
SOURCES="$(cd "$SOURCES" && pwd)"
case "$SOURCES/" in "$ROOT"/*) die "$INSIDE_MSG" ;; esac        # again, after resolving links and ..
[[ -w "$SOURCES" ]] || die "'$SOURCES' is not writable. Choose another folder with --sources DIR."
note "sources folder: $SOURCES"

checkout() {  # name url commit  ->  sets CHECKOUT_DIR
  local name="$1" url="$2" commit="$3" dir="$SOURCES/$1" fresh=0
  local git=(git -c safe.directory="$dir" -c advice.detachedHead=false -c core.fileMode=false -C "$dir")
  if [[ -e "$dir" && ! -d "$dir/.git" ]]; then
    die "'$dir' exists but is not a Git checkout of $name. Move it, or choose another folder with --sources DIR."
  fi
  if [[ ! -d "$dir/.git" ]]; then
    note "cloning $url"
    git clone --quiet --filter=blob:none --no-checkout "$url" "$dir" \
      || { rm -rf "$dir"; git clone --quiet --no-checkout "$url" "$dir"; }
    fresh=1
  else
    local origin; origin="$("${git[@]}" config --get remote.origin.url 2>/dev/null || true)"
    case "$origin" in
      *pollen-robotics/"$name"|*pollen-robotics/"$name".git|*pollen-robotics/"$name"/) ;;
      *) note "NOTE: $dir has origin '$origin' (expected pollen-robotics/$name); using it as it is." ;;
    esac
    # A checkout interrupted before any file was written counts as fresh.
    if [[ -z "$(ls -A "$dir" | grep -v '^\.git$' || true)" ]]; then fresh=1; fi
  fi
  if [[ $LATEST -eq 1 ]]; then
    "${git[@]}" fetch --quiet origin
    commit="$("${git[@]}" rev-parse origin/HEAD)"
  fi
  local head=""; [[ $fresh -eq 1 ]] || head="$("${git[@]}" rev-parse -q --verify HEAD 2>/dev/null || true)"
  if [[ "$head" != "$commit" ]]; then
    if [[ $fresh -eq 0 && -n "$("${git[@]}" status --porcelain 2>/dev/null | head -1)" ]]; then
      note "WARNING: $name has local changes and is at ${head:0:10}, not the tested ${commit:0:10}. Left untouched."
    elif [[ $fresh -eq 0 && $CHECKOUT_PINNED -eq 0 && $LATEST -eq 0 ]]; then
      note "WARNING: existing $name checkout is at ${head:0:10}; the course was tested with ${commit:0:10}."
      note "         Left untouched. Re-run with --checkout-pinned to switch it, or accept small differences."
    else
      "${git[@]}" cat-file -e "$commit^{commit}" 2>/dev/null \
        || "${git[@]}" fetch --quiet origin "$commit" || "${git[@]}" fetch --quiet origin
      "${git[@]}" checkout --quiet --detach "$commit"
    fi
  fi
  note "$name @ $("${git[@]}" rev-parse --short=10 HEAD)  ($dir)"
  CHECKOUT_DIR="$dir"
}
checkout microduck_rl "$MICRODUCK_RL_URL" "$MICRODUCK_RL_COMMIT"; RL_REPO="$CHECKOUT_DIR"
checkout microduck "$MICRODUCK_URL" "$MICRODUCK_COMMIT"; RUNTIME_REPO="$CHECKOUT_DIR"
[[ -f "$RL_REPO/pyproject.toml" ]] || die "$RL_REPO does not look like microduck_rl (no pyproject.toml)."

# ---------------------------------------------------------------- 4. python env
say "Creating the Python environment (first time: several GB of downloads, 5-20 minutes)"
FS_TYPE="$(stat -f -c %T "$ROOT" 2>/dev/null || echo unknown)"
if [[ -n "${COURSE_VENV:-}" ]]; then
  VENV="$COURSE_VENV"
elif [[ "$OS_KIND" == "wsl" && ( "$FS_TYPE" == "v9fs" || "$FS_TYPE" == "9p" || "$FS_TYPE" == "drvfs" || "$ROOT" == /mnt/* ) ]]; then
  # The repository is on a Windows drive. Virtual environments are slow and fragile
  # there, so this one goes on the Linux filesystem.
  KEY="$(printf '%s' "$ROOT" | cksum | cut -d' ' -f1)"
  VENV="$HOME/.local/share/learn-rl-with-microduck/venv-$KEY"
  note "repository is on a Windows drive: placing the environment at $VENV"
else
  VENV="$ROOT/.venv"
fi
mkdir -p "$(dirname "$VENV")"
(
  cd "$RL_REPO"
  export UV_PROJECT_ENVIRONMENT="$VENV"
  export UV_HTTP_TIMEOUT="${UV_HTTP_TIMEOUT:-600}"
  # --frozen installs exactly the locked versions and never rewrites files in the checkout.
  uv sync --frozen
) || die "Installing Python packages failed. Read the message above, then see docs/ENVIRONMENT.md (Troubleshooting).
       If a package has no build for your machine, the agent skill 'setup-environment' describes the fallback."
PY="$VENV/bin/python"
[[ -x "$PY" ]] || die "The Python environment was not created at $VENV"
note "$("$PY" --version) at $VENV"

# ---------------------------------------------------------------- 5. record
say "Recording the setup in .course/"
mkdir -p "$ROOT/.course"
LAUNCHER="./lab.sh"; WIN_DISTRO=""
if [[ "$OS_KIND" == "wsl" ]]; then
  WIN_DISTRO="${WSL_DISTRO_NAME:-}"
  case "$ROOT" in /mnt/*) LAUNCHER='.\lab' ;; esac
  if [[ -n "$WIN_DISTRO" ]]; then printf '%s\r\n' "$WIN_DISTRO" > "$ROOT/.course/wsl-distro.txt"; fi
fi
{
  printf 'export COURSE_PYTHON=%q\n' "$PY"
  printf 'export MICRODUCK_RL_REPO=%q\n' "$RL_REPO"
  printf 'export MICRODUCK_RUNTIME_REPO=%q\n' "$RUNTIME_REPO"
} > "$ROOT/.course/env.sh"
"$PY" "$ROOT/tools/write_env.py" "$ROOT" "$OS_KIND" "$ARCH" "$DISTRO_ID" "$LAUNCHER" "$PY" "$WIN_DISTRO" \
  "$RL_REPO" "$RUNTIME_REPO"

# ---------------------------------------------------------------- 6. verify
say "Checking packages, compute device and rendering"
DOCTOR_ARGS=(--write)
if [[ $FORCE_CPU -eq 1 ]]; then DOCTOR_ARGS+=(--cpu); fi
if [[ $SELFTEST -eq 1 ]]; then DOCTOR_ARGS+=(--full); fi
bash "$ROOT/lab.sh" doctor "${DOCTOR_ARGS[@]}" \
  || die "The environment check failed. See the FAIL lines above and docs/ENVIRONMENT.md."

say "Setup complete"
note "MicroDuck sources: $SOURCES/microduck_rl and $SOURCES/microduck (read-only for the course)"
note "Run a lab:         $LAUNCHER list"
note "Start learning:    open this folder in your AI coding agent and type:  start-course"
note "                   (Codex: \$start-course    Claude Code: /start-course)    See START_HERE.md"
