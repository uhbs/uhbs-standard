# Upstream PR pack: add UHBS to okhosting/awesome-cyber-security

**Target:** [okhosting/awesome-cyber-security](https://github.com/okhosting/awesome-cyber-security)

## Why this agent opens issues (not GitHub PRs) on third-party lists

A GitHub **pull request** requires either:

1. push access to the target repository, or
2. a **fork** of that repository plus a branch push, then `gh pr create`.

The Cursor GitHub App used in this environment:

- **cannot fork** third-party repos (`HTTP 403` on the forks API)
- **cannot push** to personal forks such as `mziqudhd92/*` (`Permission denied to cursor[bot]`)
- **can** open issues on some public repos, and **can** prepare a patch + PR body for a human/PAT to push

So for `paralax/awesome-honeypots` and `Correia-jpv/fucking-awesome-honeypots`, the agent filed proposal issues with full PR descriptions and left apply packs here. That is not preferred over a real PR — it is the only write path available without your local credentials.

## Proposed entry

Under `## Lists of cyber security resources` (after Watchtower):

```markdown
* [UHBS](https://github.com/uhbs/uhbs-standard) - Open-source Universal Honeypot Benchmarking Standard for vendor-neutral honeypot and deception evaluation (UHQS scoring).
```

## Open the real PR from your machine

```bash
gh repo fork okhosting/awesome-cyber-security --clone
cd awesome-cyber-security
git checkout -b add-uhbs-standard
git am /path/to/uhbs-standard/docs/conformance/awesome-honeypots/ADD-UHBS-OKHOSTING-PR.patch
git push -u origin add-uhbs-standard
gh pr create --repo okhosting/awesome-cyber-security \
  --base main --head "$(gh api user --jq .login):add-uhbs-standard" \
  --title "Add UHBS honeypot evaluation framework" \
  --body "$(cat <<'BODY'
## Summary
- Adds [UHBS](https://github.com/uhbs/uhbs-standard) under **Lists of cyber security resources**.
- Open-source, vendor-neutral framework for evaluating honeypot / deception fidelity (UHQS scoring).

## Why this fits
- UHBS is evaluation / benchmarking tooling for honeypots and deception tech (not a honeypot itself).
- Complements detector-style tools: those ask “is this a honeypot?”; UHBS asks “how realistic / safe / useful is this honeypot?”.
- Apache-2.0, actively maintained, with CLI + published scorecards.
- Not a duplicate (searched for UHBS / uhbs-standard / UHQS).

## Checklist
- [x] Searched for existing suggestions
- [x] Individual PR for this suggestion
- [x] Description ends with a period
- [x] Spelling / grammar checked

Made with [Cursor](https://cursor.com)
BODY
)"
```
