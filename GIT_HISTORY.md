# Git history preservation

The active Git metadata is stored outside this workspace at `/private/tmp/roadflow-git` because the environment blocks creation of the `.git` entry in the project root.

`roadflow-history.bundle` is an ignored, project-resident Git bundle created after the latest committed history. It is a portable backup of all repository refs. `roadflow-history.bundle.sha256` is an ignored checksum companion generated immediately after the bundle.

To restore and verify it elsewhere:

```bash
git clone roadflow-history.bundle roadflow-restored
git -C roadflow-restored log --oneline --all
git -C roadflow-restored status --short
shasum -a 256 -c roadflow-history.bundle.sha256
```

The bundle is intentionally not committed: a bundle cannot include the commit that would record the bundle itself. Regenerate the bundle and checksum after later commits with:

```bash
git --git-dir=/private/tmp/roadflow-git --work-tree=/Users/mayankkashyap/Desktop/Project2 bundle create /Users/mayankkashyap/Desktop/Project2/roadflow-history.bundle --all
shasum -a 256 /Users/mayankkashyap/Desktop/Project2/roadflow-history.bundle > /Users/mayankkashyap/Desktop/Project2/roadflow-history.bundle.sha256
shasum -a 256 -c /Users/mayankkashyap/Desktop/Project2/roadflow-history.bundle.sha256
```

The latest commit hash and bundle checksum are available from `git log` and the checksum file; they are deliberately not duplicated here because the bundle is regenerated after the documentation commit. The later OpenCode verification and fix record is in `OPENCODE_VERIFICATION.md`; the original Codex JSONL session log is not modified.
