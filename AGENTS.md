# Local Agent Development Rules

All repository-specific craft rules in `.agents/AGENTS.md` remain applicable.
For Git ownership, branch selection, upstream synchronization, and publishing,
read and follow `docs/LOCAL_DEVELOPMENT_DISCIPLINE.md` before any commit,
rebase, merge, push, pull, remote change, or pull-request operation.

Non-negotiable Git rules:

- Treat `upstream` as read-only.
- Treat `origin` as the personal fork.
- Keep `main` synchronized with `upstream/main`; do not place personal
  development commits directly on `main`.
- Put personal framework work on `personal/*` branches.
- Never reset, stash, overwrite, or clean a dirty worktree without explicit
  user authorization.
- Never use plain `--force`; use `--force-with-lease` only when the documented
  rebase workflow requires it.
