#!/usr/bin/env bash
# Tests for hooks/self-update.sh
#
# Every test runs against a throwaway HOME with a fixture marketplace git repo
# and stub `claude` on PATH. Nothing here touches the real ~/.claude.
#
# Run: hooks/tests/self-update.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUT="${HERE}/../self-update.sh"
SUT="$(cd "$(dirname "$SUT")" && pwd)/$(basename "$SUT")"

passed=0
failed=0
current_test=""

# ---------------------------------------------------------------- assertions

ok()   { passed=$((passed + 1)); printf '  ok   %s\n' "$1"; }
nope() { failed=$((failed + 1)); printf '  FAIL %s\n       %s\n' "$current_test" "$1"; }

assert_eq() {
  local want="$1" got="$2" what="${3:-value}"
  if [ "$want" = "$got" ]; then ok "$current_test"
  else nope "$what: want [$want] got [$got]"; fi
}

assert_contains() {
  local hay="$1" needle="$2" what="${3:-output}"
  case "$hay" in
    *"$needle"*) ok "$current_test" ;;
    *) nope "$what did not contain [$needle]; was [$hay]" ;;
  esac
}

assert_empty() {
  local got="$1" what="${2:-output}"
  if [ -z "$got" ]; then ok "$current_test"
  else nope "$what should have been empty, was [$got]"; fi
}

# ------------------------------------------------------------------- fixture

# Builds a sandbox in $SANDBOX with:
#   $HOME                        throwaway home, deliberately NOT the plugins root
#   $PLUGINS_ROOT                <config>/plugins, as CLAUDE_CONFIG_DIR relocates it
#   $PLUGIN_ROOT                 <plugins_root>/cache/<mkt>/<plugin>/<version>
#   $MKT_DIR                     a real git clone, on its default branch, clean,
#                                carrying .claude-plugin/marketplace.json
#   $CLAUDE_LOG                  every stub `claude` invocation, one per line
#
# The plugins root sits outside $HOME on purpose. Claude Code honors
# CLAUDE_CONFIG_DIR, so a script that hardcodes ~/.claude writes its stamp into
# the wrong tree and re-checks forever. Deriving it from $CLAUDE_PLUGIN_ROOT is
# the only thing that holds in both layouts.
#
# setup_sandbox <installed_version> <advertised_version>
setup_sandbox() {
  local installed="${1:-1.4.0}" advertised="${2:-1.4.0}"

  SANDBOX="$(mktemp -d)"
  export HOME="${SANDBOX}/home"
  export CLAUDE_LOG="${SANDBOX}/claude.log"
  PLUGIN="testplugin"
  MKT="testmkt"
  ID="${PLUGIN}@${MKT}"
  PLUGINS_ROOT="${SANDBOX}/config/plugins"
  STAMP_DIR="${PLUGINS_ROOT}/data/${PLUGIN}-${MKT}"
  STAMP="${STAMP_DIR}/update-stamp"
  PLUGIN_ROOT="${PLUGINS_ROOT}/cache/${MKT}/${PLUGIN}/${installed}"
  MKT_DIR="${PLUGINS_ROOT}/marketplaces/${MKT}"

  mkdir -p "$PLUGIN_ROOT" "$HOME"
  : > "$CLAUDE_LOG"

  # A real clone, so origin/HEAD and `git status --porcelain` behave normally.
  # The advertised version is committed, so the clone starts clean.
  local origin="${SANDBOX}/origin.git"
  git init -q --bare --initial-branch=main "$origin"
  local seed="${SANDBOX}/seed"
  git -c init.defaultBranch=main init -q "$seed"
  ( cd "$seed"
    mkdir -p .claude-plugin
    cat > .claude-plugin/marketplace.json <<EOF
{"name":"${MKT}","owner":{"name":"t"},"plugins":[
  {"name":"other","source":"./other","description":"d","version":"9.9.9"},
  {"name":"${PLUGIN}","source":"./${PLUGIN}","description":"d","version":"${advertised}"}
]}
EOF
    git add -A
    git -c user.email=t@t -c user.name=t commit -qm init
    git remote add origin "$origin"
    git push -q origin main
  ) >/dev/null 2>&1
  mkdir -p "$(dirname "$MKT_DIR")"
  git clone -q "$origin" "$MKT_DIR" >/dev/null 2>&1
  git -C "$MKT_DIR" remote set-head origin -a >/dev/null 2>&1

  cat > "${PLUGINS_ROOT}/known_marketplaces.json" <<EOF
{"${MKT}":{"source":{"source":"github","repo":"t/${MKT}"},
 "installLocation":"${MKT_DIR}","lastUpdated":"2026-01-01T00:00:00.000Z"}}
EOF

  make_stub_bin
  export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
  unset SKILL_AUTO_UPDATE SKILL_AUTO_UPDATE_INTERVAL 2>/dev/null || true
}

# A PATH containing only the real tools the script may use, plus a stub
# `claude`. Built by symlink so individual tests can drop jq/python3.

# Write an executable stub, removing any existing entry first.
#
# ALWAYS use this instead of a bare `> "${STUB_BIN}/name"`. Most entries in
# STUB_BIN are symlinks to real system tools, and a `>` redirect follows the
# symlink and overwrites its target. Writing a fake python3 over the symlink
# destroys the machine's actual python3 binary. Ask how this comment got here.
stub() { # stub <name> <script-body>
  rm -f "${STUB_BIN}/$1"
  printf '%s\n' "$2" > "${STUB_BIN}/$1"
  chmod +x "${STUB_BIN}/$1"
}

make_stub_bin() {
  STUB_BIN="${SANDBOX}/bin"
  mkdir -p "$STUB_BIN"
  local tool path
  for tool in bash env basename dirname date mkdir mv rm rmdir find sort tail head cat grep wc tr touch git printf; do
    path="$(command -v "$tool" 2>/dev/null)" && ln -sf "$path" "${STUB_BIN}/${tool}"
  done
  for tool in jq python3; do
    path="$(command -v "$tool" 2>/dev/null)" && ln -sf "$path" "${STUB_BIN}/${tool}"
  done

  # Records every invocation and returns nothing. The advertised version comes
  # from the marketplace manifest, not from the CLI, so no canned output is
  # needed -- `claude plugin list --available` omits installed plugins and can
  # never report a plugin's own version.
  rm -f "${STUB_BIN}/claude"
  cat > "${STUB_BIN}/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$CLAUDE_LOG"
exit "${STUB_CLAUDE_EXIT:-0}"
STUB
  chmod +x "${STUB_BIN}/claude"
  export PATH="$STUB_BIN"
}

teardown_sandbox() {
  [ -n "${SANDBOX:-}" ] && [ -d "$SANDBOX" ] && rm -rf "$SANDBOX"
  PATH="$ORIGINAL_PATH"
  HOME="$ORIGINAL_HOME"
}

claude_called_with() { grep -qF "$1" "$CLAUDE_LOG" 2>/dev/null; }
claude_call_count()  { wc -l < "$CLAUDE_LOG" | tr -d ' '; }

write_stamp() { # write_stamp <last_checked> <disclosed> <notice>
  mkdir -p "$STAMP_DIR"
  { printf 'last_checked=%s\n' "$1"
    printf 'disclosed=%s\n' "$2"
    printf 'notice=%q\n' "$3"
  } > "$STAMP"
}

read_stamp_key() { # read_stamp_key <key>
  ( . "$STAMP" 2>/dev/null; eval "printf '%s' \"\${$1:-}\"" )
}

describe() { current_test="$1"; }

# ---------------------------------------------------------------- notify

test_notify_discloses_on_first_run() {
  describe "notify: discloses on first run"
  setup_sandbox
  local out; out="$("$SUT" notify 2>/dev/null)"
  assert_contains "$out" "keeps itself up to date" "disclosure"
  teardown_sandbox
}

test_notify_records_disclosure() {
  describe "notify: records disclosed=1 after disclosing"
  setup_sandbox
  "$SUT" notify >/dev/null 2>&1
  assert_eq "1" "$(read_stamp_key disclosed)" "disclosed"
  teardown_sandbox
}

test_notify_silent_second_run() {
  describe "notify: silent on second run"
  setup_sandbox
  "$SUT" notify >/dev/null 2>&1
  local out; out="$("$SUT" notify 2>/dev/null)"
  assert_empty "$out" "second notify"
  teardown_sandbox
}

test_notify_prints_pending_notice() {
  describe "notify: prints a pending notice"
  setup_sandbox
  write_stamp 0 1 "Updated testplugin 1.4.0 → 1.5.0."
  local out; out="$("$SUT" notify 2>/dev/null)"
  assert_contains "$out" "1.4.0 → 1.5.0" "notice"
  teardown_sandbox
}

test_notify_clears_notice() {
  describe "notify: clears the notice so it prints once"
  setup_sandbox
  write_stamp 0 1 "Updated testplugin 1.4.0 → 1.5.0."
  "$SUT" notify >/dev/null 2>&1
  local out; out="$("$SUT" notify 2>/dev/null)"
  assert_empty "$out" "repeat notify"
  teardown_sandbox
}

test_notify_never_calls_network() {
  describe "notify: never invokes claude"
  setup_sandbox
  "$SUT" notify >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_stamp_survives_awkward_notice() {
  describe "stamp: round-trips spaces, arrows and quotes"
  setup_sandbox
  local awkward='Updated "test" 1.0 → 2.0; done'
  write_stamp 0 1 "$awkward"
  assert_eq "$awkward" "$(read_stamp_key notice)" "notice"
  teardown_sandbox
}

# ---------------------------------------------------------------- check

test_check_throttles() {
  describe "check: does nothing when the stamp is fresh"
  setup_sandbox 1.4.0 1.5.0
  write_stamp "$(date +%s)" 1 ""
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_check_runs_when_stale() {
  describe "check: runs when the stamp is older than the interval"
  setup_sandbox 1.4.0 1.5.0
  write_stamp 1 1 ""
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin marketplace update testmkt"; then ok "$current_test"
  else nope "expected a marketplace refresh; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_updates_when_newer() {
  describe "check: updates when the advertised version is greater"
  setup_sandbox 1.4.0 1.5.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then ok "$current_test"
  else nope "expected an update; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_handles_double_digit_minor() {
  describe "check: treats 1.10.0 as newer than 1.9.0"
  setup_sandbox 1.9.0 1.10.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then ok "$current_test"
  else nope "1.9.0 -> 1.10.0 should update; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_updates_on_major_bump() {
  describe "check: updates on a major bump"
  setup_sandbox 1.4.0 2.0.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then ok "$current_test"
  else nope "1.4.0 -> 2.0.0 should update; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_never_downgrades() {
  describe "check: never downgrades"
  setup_sandbox 1.4.0 1.3.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then
    nope "downgraded 1.4.0 to 1.3.0"
  else ok "$current_test"; fi
  teardown_sandbox
}

test_check_noop_on_equal_version() {
  describe "check: does not update when versions match"
  setup_sandbox 1.4.0 1.4.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then
    nope "updated when already current"
  else ok "$current_test"; fi
  teardown_sandbox
}

test_check_records_notice() {
  describe "check: records a notice after updating"
  setup_sandbox 1.4.0 1.5.0
  "$SUT" check >/dev/null 2>&1
  assert_contains "$(read_stamp_key notice)" "1.5.0" "recorded notice"
  teardown_sandbox
}

test_check_is_silent() {
  describe "check: writes nothing to stdout"
  setup_sandbox 1.4.0 1.5.0
  local out; out="$("$SUT" check 2>/dev/null)"
  assert_empty "$out" "check stdout"
  teardown_sandbox
}

test_check_skips_feature_branch() {
  describe "check: skips a marketplace clone on a feature branch"
  setup_sandbox 1.4.0 1.5.0
  git -C "$MKT_DIR" checkout -qb my-feature
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_check_skips_dirty_clone() {
  describe "check: skips a dirty marketplace clone"
  setup_sandbox 1.4.0 1.5.0
  echo "local edit" >> "${MKT_DIR}/marketplace.json"
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_check_records_attempt_before_work() {
  describe "check: stamps the attempt so failures back off"
  setup_sandbox 1.4.0 1.5.0
  STUB_CLAUDE_EXIT=1 "$SUT" check >/dev/null 2>&1
  local stamped; stamped="$(read_stamp_key last_checked)"
  if [ "${stamped:-0}" -gt 1 ]; then ok "$current_test"
  else nope "last_checked was not recorded; got [$stamped]"; fi
  teardown_sandbox
}

test_check_survives_missing_claude() {
  describe "check: exits cleanly when claude is unavailable"
  setup_sandbox 1.4.0 1.5.0
  rm -f "${STUB_BIN}/claude"
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$?" "exit status"
  teardown_sandbox
}

test_check_survives_no_json_parser() {
  describe "check: exits cleanly with neither jq nor python3"
  setup_sandbox 1.4.0 1.5.0
  rm -f "${STUB_BIN}/jq" "${STUB_BIN}/python3"
  "$SUT" check >/dev/null 2>&1
  local status=$?
  if [ "$status" -eq 0 ] && ! claude_called_with "plugin update testplugin@testmkt"; then
    ok "$current_test"
  else nope "expected a clean no-op; status [$status] log [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_defers_when_locked() {
  describe "check: defers while another session holds the lock"
  setup_sandbox 1.4.0 1.5.0
  mkdir -p "${STAMP_DIR}/.lock-${ID}"
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_check_reaps_stale_lock() {
  describe "check: reaps a lock abandoned by a dead session"
  setup_sandbox 1.4.0 1.5.0
  local lock="${STAMP_DIR}/.lock-${ID}"
  mkdir -p "$lock"
  touch -t 200001010000 "$lock"
  "$SUT" check >/dev/null 2>&1
  if [ -d "$lock" ]; then nope "stale lock was not reaped"
  else ok "$current_test"; fi
  teardown_sandbox
}

test_check_releases_lock() {
  describe "check: releases its lock on the way out"
  setup_sandbox 1.4.0 1.5.0
  "$SUT" check >/dev/null 2>&1
  if [ -d "${STAMP_DIR}/.lock-${ID}" ]; then nope "lock was left behind"
  else ok "$current_test"; fi
  teardown_sandbox
}

# ------------------------------------------------------- concurrency & guards

test_check_preserves_disclosure() {
  describe "check: does not clobber the disclosure flag"
  setup_sandbox 1.4.0 1.5.0
  write_stamp 1 1 ""
  "$SUT" check >/dev/null 2>&1
  assert_eq "1" "$(read_stamp_key disclosed)" "disclosed after check"
  teardown_sandbox
}

test_notify_preserves_last_checked() {
  describe "notify: does not clobber the check timestamp"
  setup_sandbox
  write_stamp 1757625000 0 ""
  "$SUT" notify >/dev/null 2>&1
  assert_eq "1757625000" "$(read_stamp_key last_checked)" "last_checked after notify"
  teardown_sandbox
}

test_opt_out_env() {
  describe "opt-out: SKILL_AUTO_UPDATE=0 disables check"
  setup_sandbox 1.4.0 1.5.0
  SKILL_AUTO_UPDATE=0 "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_opt_out_env_silences_notify() {
  describe "opt-out: SKILL_AUTO_UPDATE=0 silences notify"
  setup_sandbox
  local out; out="$(SKILL_AUTO_UPDATE=0 "$SUT" notify 2>/dev/null)"
  assert_empty "$out" "notify output"
  teardown_sandbox
}

test_opt_out_file() {
  describe "opt-out: .no-auto-update file disables check"
  setup_sandbox 1.4.0 1.5.0
  mkdir -p "$PLUGINS_ROOT"
  touch "${PLUGINS_ROOT}/.no-auto-update"
  "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_ignores_non_cache_root() {
  describe "guard: ignores a plugin root outside the cache"
  setup_sandbox 1.4.0 1.5.0
  CLAUDE_PLUGIN_ROOT="${HOME}/.claude/skills/loose-skill" "$SUT" check >/dev/null 2>&1
  assert_eq "0" "$(claude_call_count)" "claude invocations"
  teardown_sandbox
}

test_ignores_unset_root() {
  describe "guard: ignores an unset plugin root"
  setup_sandbox 1.4.0 1.5.0
  local out
  out="$(env -u CLAUDE_PLUGIN_ROOT "$SUT" notify 2>/dev/null)"
  assert_empty "$out" "notify output"
  teardown_sandbox
}

test_unknown_mode_is_silent() {
  describe "guard: an unknown mode is a silent no-op"
  setup_sandbox
  local out; out="$("$SUT" wat 2>/dev/null)"
  assert_empty "$out" "output"
  teardown_sandbox
}

test_stamp_follows_relocated_config() {
  describe "layout: stamp follows CLAUDE_CONFIG_DIR, never ~/.claude"
  setup_sandbox
  "$SUT" notify >/dev/null 2>&1
  if [ -f "$STAMP" ] && [ ! -e "${HOME}/.claude" ]; then ok "$current_test"
  else nope "stamp missing at ${STAMP}, or something was written under \$HOME/.claude"; fi
  teardown_sandbox
}

test_check_reads_marketplace_manifest() {
  describe "check: reads the advertised version from the marketplace manifest"
  setup_sandbox 1.4.0 1.5.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then ok "$current_test"
  else nope "did not find 1.5.0 in the manifest; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_resolves_marketplace_by_install_location() {
  describe "check: locates the marketplace via known_marketplaces installLocation"
  setup_sandbox 1.4.0 1.5.0
  # Move the clone somewhere the conventional path would never find it.
  local moved="${SANDBOX}/elsewhere/${MKT}"
  mkdir -p "$(dirname "$moved")"
  mv "$MKT_DIR" "$moved"
  cat > "${PLUGINS_ROOT}/known_marketplaces.json" <<EOF
{"${MKT}":{"source":{"source":"github","repo":"t/${MKT}"},
 "installLocation":"${moved}","lastUpdated":"2026-01-01T00:00:00.000Z"}}
EOF
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update testplugin@testmkt"; then ok "$current_test"
  else nope "did not follow installLocation; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_ignores_other_plugins_in_manifest() {
  describe "check: ignores other plugins listed in the same manifest"
  setup_sandbox 1.4.0 1.4.0
  # The fixture manifest also advertises "other" at 9.9.9.
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update"; then
    nope "matched another plugin's version; log was [$(cat "$CLAUDE_LOG")]"
  else ok "$current_test"; fi
  teardown_sandbox
}

test_state_uses_plugin_data_dir() {
  describe "layout: state lives in the conventional plugins/data directory"
  setup_sandbox
  "$SUT" notify >/dev/null 2>&1
  if [ -f "${PLUGINS_ROOT}/data/${PLUGIN}-${MKT}/update-stamp" ]; then ok "$current_test"
  else nope "no stamp at ${PLUGINS_ROOT}/data/${PLUGIN}-${MKT}/update-stamp"; fi
  teardown_sandbox
}

test_check_passes_install_scope() {
  describe "check: passes the recorded install scope to plugin update"
  setup_sandbox 1.4.0 1.5.0
  cat > "${PLUGINS_ROOT}/installed_plugins.json" <<EOF
{"version":2,"plugins":{"${ID}":[{"scope":"project","installPath":"${PLUGIN_ROOT}","version":"1.4.0"}]}}
EOF
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update ${ID} --scope project"; then ok "$current_test"
  else nope "scope not passed; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_check_defaults_scope_when_unrecorded() {
  describe "check: still updates when no install record exists"
  setup_sandbox 1.4.0 1.5.0
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update ${ID}"; then ok "$current_test"
  else nope "no update without an install record; log was [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

test_refuses_macos_python_stub() {
  describe "portability: never runs python3 on macOS without Command Line Tools"
  setup_sandbox 1.4.0 1.5.0
  rm -f "${STUB_BIN}/jq"
  stub uname        '#!/usr/bin/env bash
echo Darwin'
  stub xcode-select '#!/usr/bin/env bash
exit 2'
  stub python3      '#!/usr/bin/env bash
echo PYTHON_RAN >> "$CLAUDE_LOG"
exit 0'
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "PYTHON_RAN"; then
    nope "ran the python3 stub; it would pop the Xcode installer dialog"
  else ok "$current_test"; fi
  teardown_sandbox
}

test_allows_python_with_clt() {
  describe "portability: uses python3 on macOS when Command Line Tools are present"
  setup_sandbox 1.4.0 1.5.0
  rm -f "${STUB_BIN}/jq"
  stub uname        '#!/usr/bin/env bash
echo Darwin'
  stub xcode-select '#!/usr/bin/env bash
echo /Library/Developer/CommandLineTools'
  "$SUT" check >/dev/null 2>&1
  if claude_called_with "plugin update ${ID}"; then ok "$current_test"
  else nope "python3 path did not resolve the version; log [$(cat "$CLAUDE_LOG")]"; fi
  teardown_sandbox
}

# ------------------------------------------------------------------- runner

ORIGINAL_PATH="$PATH"
ORIGINAL_HOME="$HOME"

if [ ! -x "$SUT" ]; then
  printf 'self-update.sh not found or not executable at %s\n' "$SUT"
  exit 1
fi

printf 'self-update.sh\n'
for t in $(declare -F | sed -n 's/^declare -f \(test_.*\)$/\1/p'); do
  "$t"
done

printf '\n%d passed, %d failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
