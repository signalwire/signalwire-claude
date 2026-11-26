#!/usr/bin/env bash
# Release steps for .github/workflows/release.yml. See RELEASING.md.
#
#   release.sh tag-untagged   tag and publish the current version if it has no tag yet
#   release.sh release        open, merge, tag, and publish a release if anything ships
#
# Needs GH_TOKEN and GITHUB_REPOSITORY, and a checkout of main with full history and tags.
# With DRY_RUN=1 it reads everything and prints what it would change, but pushes,
# tags, and opens nothing.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
SCRIPTS=.github/scripts
RELEASE_BRANCH=${RELEASE_BRANCH:-release/next}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# Run a command that changes something, or only print it in a dry run.
change() {
  if [ "${DRY_RUN:-0}" = 1 ]; then
    echo "DRY RUN: $*"
  else
    "$@"
  fi
}

# PRs merged in FROM..TO, skipping release PRs. Writes $WORK/notes.md and $WORK/level.txt.
collect_prs() {
  local from=$1 to=$2 sha
  for sha in $(git log --format=%H "${from}..${to}"); do
    gh api "repos/${GITHUB_REPOSITORY}/commits/${sha}/pulls" \
      --jq '.[] | select(.merged_at != null) | {number, title, labels: [.labels[].name]}'
  done | jq -s 'unique_by(.number) | sort_by(.number) | map(select(.title | startswith("Release v") | not))' \
    > "$WORK/prs.json"
  jq '[.[].labels]' "$WORK/prs.json" | "$SCRIPTS/release.py" level > "$WORK/level.txt"
  jq -r '.[] | "- \(.title) (#\(.number))"' "$WORK/prs.json" > "$WORK/notes.md"
}

# Tag SHA as TAG and publish a GitHub release whose notes list the PRs since the previous tag.
publish() {
  local tag=$1 sha=$2 previous
  if ! git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    change git tag "$tag" "$sha"
    change git push origin "$tag"
  fi
  if gh release view "$tag" >/dev/null 2>&1; then
    echo "Release ${tag} is already published."
    return
  fi
  if previous=$(git describe --tags --abbrev=0 "${sha}^" 2>/dev/null); then
    collect_prs "$previous" "$sha"
  else
    : > "$WORK/notes.md"
  fi
  { echo "Merged since ${previous:-the first commit}:"; echo; cat "$WORK/notes.md"; } > "$WORK/release.md"
  [ "${DRY_RUN:-0}" = 1 ] && cat "$WORK/release.md"
  change gh release create "$tag" --title "$tag" --notes-file "$WORK/release.md" --verify-tag
}

# The commit that set the current version is the last release.
last_release() {
  git log -1 --format=%H -G'"version"' -- .claude-plugin/plugin.json
}

# Tag and publish the last release if nobody did, such as after a release PR that a person
# merged by hand.
tag_untagged() {
  publish "v$("$SCRIPTS/release.py" current)" "$(last_release)"
}

release() {
  local last version pr url merged
  last=$(last_release)
  if ! git diff --name-only "$last" HEAD | "$SCRIPTS/release.py" releasable; then
    echo "Nothing an install receives has changed since v$("$SCRIPTS/release.py" current)."
    return
  fi

  collect_prs "$last" HEAD
  version=$("$SCRIPTS/release.py" next "$(cat "$WORK/level.txt")")
  echo "Releasing v${version} ($(cat "$WORK/level.txt") bump):"
  cat "$WORK/notes.md"

  "$SCRIPTS/release.py" set "$version"
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git switch -q -C "$RELEASE_BRANCH"
  git commit -q -am "Release v${version}"
  change git push --force origin "$RELEASE_BRANCH"

  { echo "Releases v${version}, with these merges:"; echo; cat "$WORK/notes.md"; } > "$WORK/body.md"
  pr=$(gh pr list --head "$RELEASE_BRANCH" --state open --json number --jq '.[0].number')
  if [ -n "$pr" ]; then
    change gh pr edit "$pr" --title "Release v${version}" --body-file "$WORK/body.md"
  elif [ "${DRY_RUN:-0}" = 1 ]; then
    change gh pr create --base main --head "$RELEASE_BRANCH" --title "Release v${version}" --body-file "$WORK/body.md"
    return
  else
    url=$(gh pr create --base main --head "$RELEASE_BRANCH" --title "Release v${version}" --body-file "$WORK/body.md")
    pr=${url##*/}
  fi

  if ! change gh pr merge "$pr" --squash --subject "Release v${version} (#${pr})"; then
    echo "::error::Release PR #${pr} couldn't be merged automatically. Merge it by hand; the next run tags and publishes it."
    exit 1
  fi
  [ "${DRY_RUN:-0}" = 1 ] && return

  merged=$(gh pr view "$pr" --json mergeCommit --jq .mergeCommit.oid)
  git fetch -q origin "$merged"
  publish "v${version}" "$merged"
}

case "${1:-}" in
  tag-untagged) tag_untagged ;;
  release) release ;;
  *) sed -n '2,10p' "$0" >&2; exit 2 ;;
esac
