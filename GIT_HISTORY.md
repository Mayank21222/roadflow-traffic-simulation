# Git history preservation

The published GitHub repository is the primary project history. During development, Git metadata was kept outside the workspace because the environment blocked creation of the `.git` entry in the project root. That local arrangement is not part of the public submission.

`roadflow-history.bundle` is an optional local Git bundle created after the latest committed history. It is a portable backup of all repository refs. `roadflow-history.bundle.sha256` is an ignored checksum companion generated immediately after the bundle. Neither file is tracked or uploaded; they are not required to build or run the app.

To restore and verify a bundle elsewhere:

```bash
git clone roadflow-history.bundle roadflow-restored
git -C roadflow-restored log --oneline --all
git -C roadflow-restored status --short
shasum -a 256 -c roadflow-history.bundle.sha256
```

The bundle is intentionally not committed: a bundle cannot include the commit that would record the bundle itself. To regenerate it from the environment that holds the Git metadata, run:

```bash
PROJECT_ROOT="$(pwd)"
GIT_METADATA="/path/to/git-metadata"
git --git-dir="$GIT_METADATA" --work-tree="$PROJECT_ROOT" bundle create roadflow-history.bundle --all
shasum -a 256 roadflow-history.bundle > roadflow-history.bundle.sha256
shasum -a 256 -c roadflow-history.bundle.sha256
```

The final audit implementation commit is `235d14e`; see [FINAL_AUDIT.md](FINAL_AUDIT.md) for the public audit summary and publication state. The latest commit hash and current bundle checksum are available from `git log` and the ignored checksum file; they are deliberately not duplicated here because the bundle is regenerated after the documentation commit. The later OpenCode verification and fix record is in [OPENCODE_VERIFICATION.md](OPENCODE_VERIFICATION.md); the original Codex session log is not modified.
