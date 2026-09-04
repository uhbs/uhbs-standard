# Install and use UHBS

**Status:** Informative · getting started  
**Time:** a few minutes · no honeypot required

This is the short path: install the CLI, check a profile, check a scorecard, and
compute UHQS from module scores. It does **not** start Docker labs or grade a
live decoy.

!!! tip "Two different kinds of docs"
    | You want… | Go here |
    | --- | --- |
    | Install UHBS and run the CLI | **This page** |
    | Full command reference | [CLI & Validator](cli.md) |
    | Grade a live lab decoy | [Lab harness](../reference-implementation.md) |
    | Re-run a **published** honeypot grade | [Published grades](../conformance/reports/index.md) |

Conformance pages titled “tutorial” (Conpot, Cowrie, miniprint, …) are
**reproduce-a-grade recipes**, not this getting-started guide.

---

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install uhbs
uhbs --version
```

You should see `uhbs, version 4.5.2` (or newer).

From a git checkout of this repository:

```bash
git clone https://github.com/uhbs/uhbs-standard.git
cd uhbs-standard
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uhbs --version
```

!!! warning "Lab / sandbox only"
    UHBS evaluates honeypots and decoys in a lab or sandbox. Do not point it at
    production or systems you are not authorized to test.

---

## 2. Validate a profile

A **Target Profile Specification** (TPS) describes the decoy class and module
weights. Copy the starter template and validate it:

```bash
# from a git checkout
cp templates/profile.yaml ./my-honeypot.profile.yaml
uhbs validate-profile my-honeypot.profile.yaml
```

Expected: `OK` and `weights sum=1.000`.

---

## 3. Validate a scorecard

A **scorecard** is a finished UHBS result (JSON). The repository ships sample
fixtures under `docs/conformance/fixtures/` so you can practice without running a
lab. The filename may mention a product (for example Cowrie) — that is only a
**label on a sample file**. This command does not start that honeypot.

```bash
uhbs validate-scorecard \
  docs/conformance/fixtures/cowrie-low-interaction.scorecard.json
```

Expected: `OK` and a UHQS value (this fixture is **61.37**).

Any valid scorecard path works the same way.

---

## 4. Compute UHQS from module scores

If you already have module scores `A`–`F` (0–100), write them to a JSON file and
score:

```bash
cat > scores.json <<'EOF'
{
  "A": 23.5,
  "B": 42.5,
  "C": 57.0,
  "D": 100,
  "E": 55.0,
  "F": 69.0
}
EOF

uhbs score --class Low-Interaction --scores scores.json
```

Expected for this worked example: **UHQS ≈ 46.97**, grade **F**, Safety Gate
passed (`δ_C = 1.0`).

---

## 5. What to do next

| Next step | Command / page |
| --- | --- |
| See all CLI commands | `uhbs --help` · [CLI guide](cli.md) |
| List lab protocols (no live probe) | `pip install 'uhbs[lab]'` then `uhbs lab --list-protocols` |
| Grade a decoy you control | [Lab harness](../reference-implementation.md) |
| Reproduce a published Conpot / Cowrie / … grade | [Published grades](../conformance/reports/index.md) |
| Optional offline evidence layer | [AEP beginner tutorial](../advanced-evidence/tutorial-beginner.md) |
| Use UHBS from Cursor / Claude | [MCP server](mcp.md) |

You are done with “how to use UHBS” when steps 1–4 succeed. Everything under
**Published grades** is optional proof you can audit or re-run later.
