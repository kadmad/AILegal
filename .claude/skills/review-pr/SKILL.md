---
name: review-pr
description: Review a GitHub pull request for bugs, security issues, and design problems
context: fork
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <pr-number>
---

You are reviewing PR #$ARGUMENTS in this repository.

Fetch the PR details:
- Metadata: `gh pr view $ARGUMENTS`
- Files changed: `gh pr diff --name-only $ARGUMENTS`
- Full diff: `gh pr diff $ARGUMENTS`

Read any changed files you need more context on.

## Review focus (in priority order)

1. **Bugs** — logic errors, off-by-ones, unhandled edge cases, race conditions
2. **Security** — injection, exposed secrets, missing auth checks, unsafe deserialization
3. **Correctness** — does the code actually do what the PR description says?
4. **Design** — obvious architecture issues or patterns that will cause pain later

## What to skip

Don't flag:
- Minor style/formatting issues that a linter handles
- Variable naming that is clear enough in context
- Personal preference differences with no functional impact

## Output

Write a concise review:

**Summary** — one or two sentences on what the PR does and your overall impression.

**Issues** — list only things worth fixing. For each:
- What is the problem
- Where it is (file + line if possible)
- A brief suggestion

**Looks good** — anything notably well done (optional, only if genuine).

**Verdict** — Approve / Request changes / Needs discussion
