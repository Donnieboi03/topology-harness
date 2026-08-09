#!/usr/bin/env bash
# Apply nest-orchestrator patch (agent-topo-harness Hermes adapter) to the live Hermes tools/delegate_tool.py.
#
# Usage:
#   ./scripts/apply_hermes_delegate_patch.sh
#   ./scripts/apply_hermes_delegate_patch.sh --print-live   # detect path only
#   ./scripts/apply_hermes_delegate_patch.sh --force-copy   # skip patch(1); copy full file
#
# Idempotent when VIRGIL_NEST_ORCHESTRATOR_PATCH is already present.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="${ROOT}/adapters/hermes/delegate_tool"
PATCH_FILE="${PATCH_DIR}/nest_orchestrator.patch"
FULL_FILE="${PATCH_DIR}/delegate_tool.patched.py"
MARKER="VIRGIL_NEST_ORCHESTRATOR_PATCH"

PRINT_LIVE=0
FORCE_COPY=0
for arg in "$@"; do
  case "${arg}" in
    --print-live) PRINT_LIVE=1 ;;
    --force-copy) FORCE_COPY=1 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "error: unknown arg: ${arg}" >&2
      exit 2
      ;;
  esac
done

detect_live() {
  local candidate=""

  # 1) Whatever `hermes` on PATH actually imports
  if command -v hermes >/dev/null 2>&1; then
    local hermes_bin hermes_py
    hermes_bin="$(command -v hermes)"
    hermes_py="$(head -1 "${hermes_bin}" | sed -n 's/^#!//p')"
    if [[ -n "${hermes_py}" && -x "${hermes_py}" ]]; then
      candidate="$("${hermes_py}" -c 'import tools.delegate_tool as d; print(d.__file__)' 2>/dev/null | tail -1 || true)"
    fi
  fi

  # 2) Common installs
  if [[ -z "${candidate}" || ! -f "${candidate}" ]]; then
    local paths=(
      "/opt/homebrew/lib/python3.11/site-packages/tools/delegate_tool.py"
      "/opt/homebrew/lib/python3.12/site-packages/tools/delegate_tool.py"
      "/opt/homebrew/lib/python3.13/site-packages/tools/delegate_tool.py"
      "/usr/local/lib/python3.11/site-packages/tools/delegate_tool.py"
      "${ROOT}/.venv/lib/python3.14/site-packages/tools/delegate_tool.py"
      "${ROOT}/.venv/lib/python3.13/site-packages/tools/delegate_tool.py"
      "${ROOT}/.venv/lib/python3.12/site-packages/tools/delegate_tool.py"
      "${ROOT}/.venv/lib/python3.11/site-packages/tools/delegate_tool.py"
    )
    for p in "${paths[@]}"; do
      if [[ -f "${p}" ]]; then
        candidate="${p}"
        break
      fi
    done
  fi

  # 3) Glob Homebrew / user site-packages
  if [[ -z "${candidate}" || ! -f "${candidate}" ]]; then
    local found
    found="$(
      # shellcheck disable=SC2086
      find /opt/homebrew/lib/python*/site-packages /usr/local/lib/python*/site-packages \
        "${HOME}/Library/Python"/*/lib/python*/site-packages \
        -name delegate_tool.py 2>/dev/null | head -1 || true
    )"
    if [[ -n "${found}" && -f "${found}" ]]; then
      candidate="${found}"
    fi
  fi

  if [[ -z "${candidate}" || ! -f "${candidate}" ]]; then
    return 1
  fi
  printf '%s\n' "${candidate}"
}

LIVE="$(detect_live || true)"
if [[ -z "${LIVE}" ]]; then
  cat >&2 <<EOF
error: Hermes tools/delegate_tool.py not found.

Install hermes-agent (so \`hermes\` is on PATH), or set the live file
manually after locating it, e.g.:

  find /opt/homebrew /usr/local "${ROOT}/.venv" -name delegate_tool.py

Then either re-run this script or:
  cp "${FULL_FILE}" /path/to/tools/delegate_tool.py
EOF
  exit 1
fi

if [[ "${PRINT_LIVE}" -eq 1 ]]; then
  printf '%s\n' "${LIVE}"
  exit 0
fi

if [[ ! -f "${PATCH_FILE}" || ! -f "${FULL_FILE}" ]]; then
  echo "error: missing patch artifacts under ${PATCH_DIR}" >&2
  exit 1
fi

SITE_PACKAGES="$(cd "$(dirname "${LIVE}")/.." && pwd)"

echo "==> agent-topo-harness Hermes nest-orchestrator patch"
echo "    live: ${LIVE}"
echo "    site: ${SITE_PACKAGES}"

if grep -q "${MARKER}" "${LIVE}"; then
  echo "    already applied (${MARKER} present) — nothing to do"
  exit 0
fi

backup="${LIVE}.virgil-pre-nest.bak"
cp "${LIVE}" "${backup}"
echo "    backup: ${backup}"

apply_via_patch() {
  # Non-interactive: refuse reverse-apply prompts
  if patch -p1 --forward --dry-run -d "${SITE_PACKAGES}" < "${PATCH_FILE}" >/dev/null 2>&1; then
    patch -p1 --forward -d "${SITE_PACKAGES}" < "${PATCH_FILE}"
    return 0
  fi
  return 1
}

apply_via_copy() {
  cp "${FULL_FILE}" "${LIVE}"
}

ok=0
if [[ "${FORCE_COPY}" -eq 1 ]]; then
  apply_via_copy
  ok=1
  echo "    applied via full-file copy (--force-copy)"
elif apply_via_patch; then
  ok=1
  echo "    applied via nest_orchestrator.patch"
else
  echo "    warn: unified diff did not apply cleanly (upstream drift?)"
  echo "    falling back to full patched copy (may miss newer upstream lines)"
  apply_via_copy
  ok=1
  echo "    applied via delegate_tool.patched.py fallback"
fi

if [[ "${ok}" -ne 1 ]] || ! grep -q "${MARKER}" "${LIVE}"; then
  echo "error: patch did not land; restoring backup" >&2
  cp "${backup}" "${LIVE}"
  exit 1
fi

echo "    OK — Topic Owner nest (role=orchestrator @ depth 1) is wired"
echo "    Reminder: after \`hermes\` / hermes-agent upgrade, re-run this script."
