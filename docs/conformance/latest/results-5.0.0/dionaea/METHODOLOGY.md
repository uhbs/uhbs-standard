# Methodology: Dionaea multi-protocol UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` / `uhbs:5.0.0-full`  
**Upstream commit:** `4e459f1b672a5b4c1e8335c0bff1b93738019215` (`master`)

## Runtime

- Strategy: `upstream-docker` (`dinotools/dionaea:latest`; Dockerfile `FROM ubuntu:18.04`)
- Reason not Ubuntu latest: upstream ships a maintained official image; Dockerfile pins Ubuntu 18.04
- Platform: `linux/amd64` (emulated on arm64 Docker Desktop)
- Target image id: `sha256:9e0b7572d5638eacd7ce785ff8f2d776af91f9040c6871926d967defb05a3a22`
- Network: `uhbs-lab`, alias `dionaea-lab`

## What was graded

FTP, SMB, HTTP — quick + full, all **INCOMPLETE / ungraded** (honest v5 Safety Gate). Module C incomplete on declared-format; Module D critical controls NOT_TESTED/ERROR under attested air-gap.

## Limitations

- Do not transplant archived 4.x letter grades
- Official image is amd64-only
- Product name is evaluation proof only
