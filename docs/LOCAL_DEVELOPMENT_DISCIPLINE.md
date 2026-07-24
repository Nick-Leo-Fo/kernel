# Local Development Discipline

## Purpose

This checkout combines an external open-source upstream with private or
personal framework development. Preserve a clean upstream synchronization path
without losing local history.

## Remote contract

```text
upstream fetch = git@github.com:isaacsight/kernel.git
upstream push  = DISABLED
origin         = git@github.com:Nick-Leo-Fo/kernel.git
```

- `upstream` is the open-source source of updates. Fetch from it; do not push
  personal work to it.
- `origin` is the personal fork. Push personal branches and the fork's mirror
  of `main` to it.
- Do not swap these names or configure one remote with split ownership.

Before any remote-changing or publishing operation, verify:

```bash
git remote -v
git branch -vv
git status --short --branch
```

Stop if the URLs, tracking branches, or dirty-file ownership differ from this
contract.

## Branch contract

### `main`

`main` mirrors `upstream/main`.

- Do not create personal commits on `main`.
- Update it only by fast-forward from `upstream/main`.
- Mirror the result to `origin/main`.

### `personal/*`

Long-lived personal framework work belongs on a clearly named `personal/*`
branch. The current Kernel evaluation, Recursive Project Tree, and related
local governance work belongs on:

```text
personal/recursive-project-tree
```

Merge updated `main` into this branch by default. This preserves published
history and avoids routine force-pushes.

### `contrib/*`

Changes intended for an upstream pull request use a fresh `contrib/*` branch
created from current `upstream/main`. Do not include unrelated personal
framework commits.

## First-time fork setup

The expected one-time configuration is:

```bash
git remote rename origin upstream
git remote set-url --push upstream DISABLED
git remote add origin git@github.com:Nick-Leo-Fo/kernel.git
git fetch upstream
git fetch origin
```

Preserve existing local commits before restoring `main`:

```bash
git switch -c personal/recursive-project-tree
git push -u origin personal/recursive-project-tree
```

Only after the personal branch is confirmed on `origin` may local `main` be
recreated or moved to `upstream/main`. Never reset the only copy of local
commits.

## Normal upstream synchronization

First update the clean mirror:

```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main
```

Then update personal development:

```bash
git switch personal/recursive-project-tree
git merge main
git push origin personal/recursive-project-tree
```

If the worktree is dirty, stop before switching or merging. Commit the bounded
work on its owning branch, or ask the user how to preserve it. Do not
automatically stash.

## Optional rebase

Use rebase only when the branch is personally owned and a linear history has
material value:

```bash
git fetch upstream
git rebase upstream/main
git push --force-with-lease origin personal/recursive-project-tree
```

Never use plain `--force`. Do not rebase a shared branch without explicit
agreement from every owner.

## Upstream contribution workflow

Create a clean contribution branch:

```bash
git fetch upstream
git switch -c contrib/<topic> upstream/main
```

Commit only the upstream-suitable change, push it to the fork, and open the
pull request from `Nick-Leo-Fo:contrib/<topic>` to
`isaacsight:main`:

```bash
git push -u origin contrib/<topic>
gh pr create --repo isaacsight/kernel --base main --head Nick-Leo-Fo:contrib/<topic>
```

Personal evaluations, workflow experiments, local governance files, and
unrelated refactors must not leak into an upstream contribution.

## Safety and evidence

- A Git commit is local; `git push` selects the remote boundary.
- Fetch before judging whether a branch is current.
- Use `--ff-only` for the upstream mirror so divergence fails visibly.
- Resolve merge conflicts on the personal branch, never by rewriting
  `upstream/main`.
- Preserve user-owned untracked and modified files exactly as found.
- Before declaring synchronization complete, verify remote URLs, tracking
  relationships, worktree status, and the remote branch commit.
