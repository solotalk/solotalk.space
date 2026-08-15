# Contributing to Solotalk Space

**Read this document in full before writing any code.**

## Workflow Overview

1. **Issues first.** Every feature or bug fix starts with an issue in the **main repository**. Feature requests and bug reports also go to the main repository's issue tracker.
2. **Assignment.** Issues are assigned to members by the main repository admin. Do not start work on an unassigned issue.
3. **Fork.** Fork the main repository to your personal account and do all development there.
4. **Branch.** Create a branch following the naming rules below.
5. **Pull Request.** When the work is done, open a PR from your fork back to the main repository. Merges happen only through PRs on GitHub.

## Branch Model (GitHub-Flow)

| Branch | Purpose |
| --- | --- |
| `master` | Main branch, always releasable |
| `dev` | Integration branch for ongoing development |
| `release/*` | Pre-release branches |
| `hotfix/*` | Urgent production fixes |
| `feat/{issue-number}-{issue-title}` | Feature branches |
| `fix/{issue-number}-{issue-title}` | Bug-fix branches |

Naming rules for `feat/` and `fix/` branches: issue number, followed by the issue title in all lowercase with spaces replaced by `-`.

Example: issue `#13` titled "[Bug] Wrong Redirect" → branch `fix/13-wrong-redirect`.

## Merge Rules

- **Never merge `master`, `dev`, or `release/*` locally.** All merges into these branches go through GitHub Pull Requests.
- When developing locally with git worktrees, merging a temporary working branch into its parent `feat/` or `fix/` branch is allowed.

## Commit Messages

Commit messages follow the **Conventional Commits** specification:

```
feat: add per-IP rate limiting for downloads
fix: correct redirect after login
docs: update deployment guide
```

- Only commit at a meaningful milestone that introduces no known issues.
- If a commit completes an issue, close it from the commit message, e.g. append `Closes #13`.

## Language Convention

Everything in the project is written in **English** (identifiers, comments, commit messages, documentation), except user-facing frontend display copy.
