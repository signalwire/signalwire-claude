#!/usr/bin/env bash
# Keeps this plugin up to date. Invoked from a SessionStart hook.
#
#   notify  synchronous, no network, prints at most one short line
#   check   asynchronous, silent, does the network work and the update
#
# Both modes exit 0 unconditionally. A broken or offline update check must
# never disrupt a session.
#
# Bash specifically, not sh: `printf %q`, `local`, and arithmetic are all used
# below, and the hook declares "shell": "bash" for the same reason.
set -uo pipefail

CHECK_INTERVAL="${SKILL_AUTO_UPDATE_INTERVAL:-86400}"

[ "${SKILL_AUTO_UPDATE:-1}" = "0" ] && exit 0

# $CLAUDE_PLUGIN_ROOT is <plugins_root>/cache/<marketplace>/<plugin>/<version>.
# Anything else (a bare skills directory, a local path install) is out of scope.
root="${CLAUDE_PLUGIN_ROOT:-}"
case "$root" in
  */plugins/cache/*/*/*) ;;
  *) exit 0 ;;
esac

version=$(basename "$root")
plugin=$(basename "$(dirname "$root")")
marketplace=$(basename "$(dirname "$(dirname "$root")")")
id="${plugin}@${marketplace}"

# Derive the plugins root from the plugin's own path rather than assuming
# ~/.claude. CLAUDE_CONFIG_DIR relocates the whole tree, and a hardcoded home
# path would write the stamp somewhere Claude Code never reads, so the check
# would repeat every session forever.
plugins_root=$(dirname "$(dirname "$(dirname "$(dirname "$root")")")")

# Claude Code already reserves data/<plugin>-<marketplace> for per-plugin state.
# Use it rather than inventing a parallel location.
STATE_DIR="${plugins_root}/data/${plugin}-${marketplace}"
stamp="${STATE_DIR}/update-stamp"
OPT_OUT="${plugins_root}/.no-auto-update"

[ -e "$OPT_OUT" ] && exit 0

last_checked=0
disclosed=0
notice=

load_stamp() { [ -f "$stamp" ] && . "$stamp"; return 0; }

# Merge on write. `notify` and `check` both run at session start and both touch
# the stamp, so writing the whole record blind would let one clobber a field the
# other just set. Name the keys this call owns; everything else is re-read from
# disk and preserved.
#
#   save_stamp disclosed notice
#
save_stamp() {
  local own_checked="${last_checked:-0}"
  local own_disclosed="${disclosed:-0}"
  local own_notice="${notice:-}"
  local key

  load_stamp
  for key in "$@"; do
    case "$key" in
      last_checked) last_checked="$own_checked" ;;
      disclosed)    disclosed="$own_disclosed" ;;
      notice)       notice="$own_notice" ;;
    esac
  done

  mkdir -p "$STATE_DIR" || return 0
  {
    printf 'last_checked=%s\n' "${last_checked:-0}"
    printf 'disclosed=%s\n'    "${disclosed:-0}"
    printf 'notice=%q\n'       "${notice:-}"
  } > "${stamp}.tmp" 2>/dev/null && mv -f "${stamp}.tmp" "$stamp" 2>/dev/null
  return 0
}

have() { command -v "$1" >/dev/null 2>&1; }

# jq is not installed everywhere, so python3 is the fallback -- but on macOS
# without the Command Line Tools, /usr/bin/python3 is a stub whose only behavior
# is to pop the Xcode installer dialog. Running it blind from a startup hook
# would ambush the user with a GUI prompt they never asked for.
python_ok() {
  have python3 || return 1
  [ "$(uname -s 2>/dev/null)" != "Darwin" ] || xcode-select -p >/dev/null 2>&1
}

# `claude plugin update` defaults to user scope. A plugin installed at project
# or local scope would have the wrong installation updated, or none at all.
install_scope() {
  local f="${plugins_root}/installed_plugins.json" s=""
  if [ -f "$f" ]; then
    if have jq; then
      s=$(jq -r --arg id "$id" '.plugins[$id][0].scope // empty' "$f" 2>/dev/null)
    elif python_ok; then
      s=$(python3 -c 'import json,sys
d = json.load(open(sys.argv[1]))
e = d.get("plugins", {}).get(sys.argv[2]) or [{}]
print(e[0].get("scope", ""))' "$f" "$id" 2>/dev/null)
    fi
  fi
  printf '%s' "$s"
}

newer() {
  [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -1)" = "$2" ]
}

# Where this marketplace actually lives. `known_marketplaces.json` is
# authoritative: a marketplace added from a local directory is never cloned
# under marketplaces/ at all, and installLocation points at the original.
marketplace_dir() {
  local kmf="${plugins_root}/known_marketplaces.json" loc=""
  if [ -f "$kmf" ]; then
    if have jq; then
      loc=$(jq -r --arg m "$marketplace" '.[$m].installLocation // empty' "$kmf" 2>/dev/null)
    elif python_ok; then
      loc=$(python3 -c 'import json,sys
d = json.load(open(sys.argv[1]))
print(d.get(sys.argv[2], {}).get("installLocation", ""))' "$kmf" "$marketplace" 2>/dev/null)
    fi
  fi
  [ -n "$loc" ] || loc="${plugins_root}/marketplaces/${marketplace}"
  printf '%s' "$loc"
}

# The advertised version, straight from the refreshed marketplace manifest.
# Note that `claude plugin list --available` cannot be used here: it lists only
# plugins that are NOT installed, so a plugin never appears in its own lookup.
latest_version() {
  local manifest="$1/.claude-plugin/marketplace.json"
  [ -f "$manifest" ] || return 1
  if have jq; then
    jq -r --arg p "$plugin" '.plugins[]? | select(.name == $p) | .version' \
      "$manifest" 2>/dev/null | head -1
  elif python_ok; then
    python3 -c 'import json,sys
d = json.load(open(sys.argv[1]))
print(next((p.get("version","") for p in d.get("plugins", [])
            if p.get("name") == sys.argv[2]), ""))' "$manifest" "$plugin" 2>/dev/null
  else
    return 1
  fi
}

# The marketplace clone belongs to the user. If they are developing against it,
# leave it alone entirely -- `marketplace update` would pull under their feet.
marketplace_is_pristine() {
  local dir="$1"
  [ -d "${dir}/.git" ] || return 0   # not a git checkout; nothing to disturb
  local default current
  default=$(git -C "$dir" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
  default="${default#origin/}"
  current=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
  [ -n "$default" ] && [ -n "$current" ] && [ "$default" != "$current" ] && return 1
  [ -n "$(git -C "$dir" status --porcelain 2>/dev/null)" ] && return 1
  return 0
}

do_notify() {
  load_stamp
  local out=""

  if [ "${disclosed:-0}" != "1" ]; then
    out="${plugin} keeps itself up to date: once a day it checks its marketplace"
    out="${out} and installs any newer version, which takes effect the next time"
    out="${out} you start Claude Code. To turn this off, set SKILL_AUTO_UPDATE=0"
    out="${out} or create ${OPT_OUT}"
    disclosed=1
  fi

  if [ -n "${notice:-}" ]; then
    out="${out:+${out} }${notice}"
    notice=
  fi

  [ -n "$out" ] || return 0
  save_stamp disclosed notice
  printf '%s\n' "$out"
}

do_check() {
  load_stamp
  local now; now=$(date +%s)
  [ $(( now - ${last_checked:-0} )) -lt "$CHECK_INTERVAL" ] && return 0

  have claude || return 0
  local mkt_dir; mkt_dir="$(marketplace_dir)"
  marketplace_is_pristine "$mkt_dir" || return 0

  # mkdir is atomic; flock does not exist on macOS.
  mkdir -p "$STATE_DIR" || return 0
  # Script-scoped, not local: the EXIT trap fires after this function has
  # returned, when a local would already be out of scope.
  LOCK="${STATE_DIR}/.lock-${id}"
  if ! mkdir "$LOCK" 2>/dev/null; then
    # Reap a lock abandoned by a killed session, then let the next run proceed.
    [ -n "$(find "$LOCK" -maxdepth 0 -mmin +10 2>/dev/null)" ] && rmdir "$LOCK" 2>/dev/null
    return 0
  fi
  trap 'rmdir "$LOCK" 2>/dev/null' EXIT

  # Record the attempt before doing the work, so a persistent failure backs off
  # for a full interval instead of retrying at every session start.
  last_checked="$now"
  save_stamp last_checked

  claude plugin marketplace update "$marketplace" >/dev/null 2>&1 || return 0

  local remote; remote=$(latest_version "$mkt_dir") || return 0
  [ -n "$remote" ] || return 0
  newer "$version" "$remote" || return 0

  local scope updated=1
  scope="$(install_scope)"
  if [ -n "$scope" ]; then
    claude plugin update "$id" --scope "$scope" >/dev/null 2>&1 && updated=0
  else
    claude plugin update "$id" >/dev/null 2>&1 && updated=0
  fi

  if [ "$updated" -eq 0 ]; then
    notice="Updated ${plugin} ${version} -> ${remote}. It takes effect the next time you start Claude Code."
    save_stamp notice
  fi
}

case "${1:-}" in
  notify) do_notify ;;
  check)  do_check ;;
esac
exit 0
