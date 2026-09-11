# Upstream PR pack: add UHBS to paralax/awesome-honeypots

**Target:** [paralax/awesome-honeypots](https://github.com/paralax/awesome-honeypots)  
**Proposal issue:** https://github.com/paralax/awesome-honeypots/issues/166  
**Existing fork:** https://github.com/mziqudhd92/awesome-honeypots

## Why this is an issue + patch (not an opened GitHub PR)

The Cursor GitHub App can open issues on `paralax/awesome-honeypots`, but **cannot
fork** that repository or push branches to `mziqudhd92/awesome-honeypots`. A
formal PR needs a human (or PAT) push from the existing fork.

## Proposed entry (`README.md` → `## Guides`)

```markdown
- [UHBS](https://github.com/uhbs/uhbs-standard) - Open-source Universal Honeypot Benchmarking Standard for vendor-neutral honeypot and deception evaluation (UHQS scoring).
```

Place after the Security Canary Maturity Model bullet (before Deployment).

## Apply from the existing fork

```bash
git clone https://github.com/mziqudhd92/awesome-honeypots.git
cd awesome-honeypots
git remote add upstream https://github.com/paralax/awesome-honeypots.git || true
git fetch upstream
git checkout -b add-uhbs-standard upstream/master
git am path/to/uhbs-standard/docs/conformance/awesome-honeypots/ADD-UHBS-PARALAX-PR.patch
git push -u origin add-uhbs-standard
gh pr create --repo paralax/awesome-honeypots \
  --base master --head mziqudhd92:add-uhbs-standard \
  --title "Add UHBS to Guides" \
  --body "$(cat <<'BODY'
## Summary
- Adds [UHBS](https://github.com/uhbs/uhbs-standard) under **Guides**, alongside T-Pot and the Security Canary Maturity Model.
- Short description: open-source, vendor-neutral framework for evaluating honeypot / deception fidelity (UHQS scoring).

## Why this fits
- UHBS is an evaluation / benchmarking standard and lab tooling for honeypots — not a honeypot itself — so it belongs with Guides.
- Complements Anti-honeypot detectors (e.g. honeydet, honeypot-auditor): those ask “is this a honeypot?”; UHBS asks “how realistic / safe / useful is this honeypot?”.
- Open source (Apache-2.0), actively maintained, with CLI + published scorecards.
- Not a duplicate (searched for UHBS / uhbs-standard / UHQS).

## Checklist
- [x] Searched for existing suggestions (not listed)
- [x] Individual PR for this suggestion
- [x] Format: `[PACKAGE](LINK) - DESCRIPTION.`
- [x] Description ends with a period
- [x] Spelling / grammar checked

Closes paralax/awesome-honeypots#166

Made with [Cursor](https://cursor.com)
BODY
)"
```
