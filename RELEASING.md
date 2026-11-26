# Releasing

Releases are automatic. Don't change `version` in `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` in a pull request: the release workflow (`.github/workflows/release.yml`) sets it after you merge. A check fails any pull request that changes it.

## What happens after a merge

1. A push to `main` starts the Release workflow, which waits five minutes. Another merge in that time cancels the waiting run and starts a new one, so merges that land together become one release. A merge that arrives while a release is already in progress waits for it to finish instead of interrupting it.
2. The workflow compares `main` with the last release tag. If nothing in `skills/`, `commands/`, `hooks/`, `.claude-plugin/`, or `.mcp.json` has changed, it stops, so a change to only the docs or `.github/` doesn't make a release.
3. Otherwise it opens a pull request titled `Release vX.Y.Z` that sets the new version, and merges it. `main` only accepts changes through pull requests, so the version bump needs one too.
4. It tags the merge commit `vX.Y.Z` and publishes a GitHub release listing the merged pull requests.

Users get the new version once the release pull request is on `main`: Claude Code detects updates by the plugin's `version`, and in Claude Code the plugin's daily self-update installs it. The tag and the GitHub release record what shipped; they don't affect installs.

## Picking the version

Each release is a patch bump unless a merged pull request has one of these labels:

| Label | Bump |
|---|---|
| `release:minor` | 1.2.3 → 1.3.0 |
| `release:major` | 1.2.3 → 2.0.0 |

When several pull requests go out together, the largest bump wins.

## Releasing now

To skip the wait, run the workflow by hand: **Actions > Release > Run workflow**, or `gh workflow run release.yml`. It still releases only if something that ships has changed.

To see what a release would contain without making one, run it with **dry run** checked, or `gh workflow run release.yml -f dry_run=true`. The log shows the next version, the pull requests it would list, and each change it would make.

To change the wait, set the repository variable `RELEASE_DELAY_SECONDS` (**Settings > Secrets and variables > Actions > Variables**). It defaults to 300.

## What the workflow relies on

The `protect-main` ruleset only lets changes into `main` through pull requests, and nothing bypasses it, which is why the version bump goes through a release pull request. The workflow can merge that pull request itself only while two things stay true:

- The ruleset requires no approving reviews. If it requires one, the bot can't approve its own pull request.
- The ruleset requires no status checks. A pull request opened by the workflow doesn't start other workflows, so a required check never reports.

If either changes, every release stops at an open release pull request for a person to merge.

## When a release fails

If the workflow can't merge its release pull request, the run fails and the pull request stays open. Merge it yourself. The next run finds that the new version has no tag or GitHub release yet and publishes both, with notes listing the pull requests since the previous release.

If a run stops partway through, the next one picks up where it left off. It updates the open release pull request rather than opening another, and tags and publishes any release that was merged but not published.

## Changing the release script

The steps are in `.github/scripts/release.sh` and the version logic in `.github/scripts/release.py`. Run the tests with:

```bash
uv run --script .github/scripts/test_release.py
```

A pull request that changes either script or the release workflow runs the tests, `actionlint`, `shellcheck`, and a dry run against `main`. To dry-run locally, use a scratch worktree, because the script edits the version files and commits on a local `release/next` branch:

```bash
git worktree add --detach /tmp/release-dry-run origin/main
cp .github/scripts/release.* /tmp/release-dry-run/.github/scripts/
cd /tmp/release-dry-run
GITHUB_REPOSITORY=signalwire/signalwire-claude GH_TOKEN=$(gh auth token) DRY_RUN=1 .github/scripts/release.sh release
```
