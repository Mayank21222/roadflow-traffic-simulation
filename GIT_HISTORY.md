# Git history preservation

The active Git metadata is stored outside this workspace at `/private/tmp/roadflow-git` because the environment blocks creation of the `.git` entry in the project root.

`roadflow-history.bundle` is an ignored, project-resident Git bundle created after the latest committed history. It is a portable backup of all repository refs. To restore it elsewhere:

```bash
git clone roadflow-history.bundle roadflow-restored
```

The bundle is intentionally not committed: a bundle cannot include the commit that would record the bundle itself. It must be regenerated after later commits with:

```bash
git --git-dir=/private/tmp/roadflow-git --work-tree=/Users/mayankkashyap/Desktop/Project2 bundle create /Users/mayankkashyap/Desktop/Project2/roadflow-history.bundle --all
```
