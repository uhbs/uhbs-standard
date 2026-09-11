# Upstream PR pack: add UHBS to fucking-awesome-honeypots

**Target:** [Correia-jpv/fucking-awesome-honeypots](https://github.com/Correia-jpv/fucking-awesome-honeypots)  
**Proposal issue:** https://github.com/Correia-jpv/fucking-awesome-honeypots/issues/5  
**Related detector PR (same list):** https://github.com/Correia-jpv/fucking-awesome-honeypots/pull/3

## Why not opened as a GitHub PR from this agent

The Cursor GitHub App can open issues on the upstream list, but **cannot fork**
third-party repositories or push to `mziqudhd92/fucking-awesome-honeypots`.
A formal PR therefore needs a human (or PAT) push to an existing fork.

## Apply from the existing fork (recommended)

```bash
git clone https://github.com/mziqudhd92/fucking-awesome-honeypots.git
cd fucking-awesome-honeypots
git remote add upstream https://github.com/Correia-jpv/fucking-awesome-honeypots.git
git fetch upstream
git checkout -b add-uhbs-standard upstream/main
git am path/to/uhbs-standard/docs/conformance/awesome-honeypots/ADD-UHBS-PR.patch
git push -u origin add-uhbs-standard
gh pr create --repo Correia-jpv/fucking-awesome-honeypots \
  --base main --head mziqudhd92:add-uhbs-standard \
  --title "Add UHBS to Guides" \
  --body-file - <<'BODY'
## Summary
- Adds [UHBS](https://github.com/uhbs/uhbs-standard) under **Guides**, alongside T-Pot and the Security Canary Maturity Model.
- Short description: open-source, vendor-neutral framework for evaluating honeypot / deception fidelity (UHQS scoring).

## Why this fits
- UHBS is an evaluation / benchmarking standard and lab tooling for honeypots — not a honeypot itself — so it belongs with Guides / related components.
- Complements Anti-honeypot detectors (e.g. honeydet, honeypot-auditor): those ask “is this a honeypot?”; UHBS asks “how realistic / safe / useful is this honeypot?”.
- Open source (Apache-2.0), actively maintained, with CLI + published scorecards.
- Not a duplicate (searched for UHBS / uhbs-standard / UHQS).

## Checklist
- [x] Searched for existing suggestions (not listed)
- [x] Individual PR for this suggestion
- [x] Format matches surrounding entries (stars/forks badges + description ending with period)
- [x] Spelling / grammar checked

Closes Correia-jpv/fucking-awesome-honeypots#5

Made with [Cursor](https://cursor.com)
BODY
```

## Proposed entry (`README.md` → Guides)

```markdown
- <b><code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2⭐</code></b> <b><code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0🍴</code></b> [UHBS](https://github.com/uhbs/uhbs-standard)) - Open-source Universal Honeypot Benchmarking Standard for vendor-neutral honeypot and deception evaluation (UHQS scoring).
```
