# AGENTS.md — Global Working Agreement

These rules apply to every task in this repository, for every agent session.

## Communication

1. **Think in English, reply in Simplified Chinese.** Regardless of the language the user writes in, internal reasoning is done in English and all replies to the user are in Simplified Chinese.
2. **Ask before acting when things are unclear.** When requirements are ambiguous, tests fail, or the next step is not obvious, present concrete options and let the user choose (or reply with an explicit plan). Do not guess.
3. **Git mutations require explicit authorization.** Every `git commit` or other git mutation needs the user's approval for that specific action. Details live in the `git-workflow` skill.

## Development Workflow

4. **Parallelize with subagents and git worktrees.** Whenever work can be split into independent pieces, run them asynchronously via subagents and/or worktrees to improve efficiency.
5. **No over-testing.** Test what the change actually needs, nothing more. If tests fail and a retry or a different testing approach is needed, ask for authorization first.
6. **Comments are allowed where necessary.** Write comments where they add real value; neither ban them nor litter them.

## Language & Content Conventions

7. **English everywhere in the project**, except user-facing frontend display copy. This includes identifiers, code comments, commit messages, and all documentation. Key documents (README, CONTRIBUTE) may additionally ship a Chinese version with identical content, e.g. `README.zh-CN.md`.
8. **No excessive explanatory text on frontend pages.** UI copy stays minimal and functional.
