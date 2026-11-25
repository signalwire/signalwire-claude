# Releasing

Releases are automatic. Don't change `version` in `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` in a pull request: the release workflow (`.github/workflows/release.yml`) sets it after you merge.

## What happens after a merge

1. A push to `main` starts the Release workflow, which waits five minutes. Another merge in that time cancels the waiting run and starts a new one, so merges that land together become one release.
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

To change the wait, set the repository variable `RELEASE_DELAY_SECONDS` (**Settings > Secrets and variables > Actions > Variables**). It defaults to 300.

## When a release fails

If the workflow can't merge its release pull request, the run fails and the pull request stays open. Merge it yourself. The next run finds that the new version has no tag yet, then tags it and publishes the release.

If a run is cancelled partway through, the next run picks up where it stopped: it updates the open release pull request rather than opening another, and tags any release that was merged but not tagged.

## Changing the release script

The version logic is in `.github/scripts/release.py`. Run its tests with:

```bash
uv run --script .github/scripts/test_release.py
```

They also run on any pull request that changes the script or the release workflow.
