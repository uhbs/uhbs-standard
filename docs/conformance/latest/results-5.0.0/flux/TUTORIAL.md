# Tutorial: grade flux (http) with UHBS (quick + full)

**Status:** Informative · evaluation proof  
**Outputs:** [`quick/`](http/quick/README.md) · [`full/`](http/full/README.md) · [METHODOLOGY.md](METHODOLOGY.md) · [EXECUTION-STEPS.md](http/EXECUTION-STEPS.md)

Clone `https://github.com/andrewmichaelsmith/flux.git` at `main` HEAD `0db4b8b0b87243d2061137212e49311bfbbd38b1`. Runtime: `custom-base` / `python:3.12-slim`. No upstream Dockerfile. README is pip install aiohttp; python -m flux (Python 3.11+). python:3.12-slim matches documented runtime; bind patched 0.0.0.0:8080; tarpit disabled so grader probes on /login do not hang.

Exact commands: [EXECUTION-STEPS.md](http/EXECUTION-STEPS.md).

**Published results (UHBS 5.0.0):** INCOMPLETE / INCOMPLETE — ungraded unless the Safety Gate passed. See [`http/full/SCORECARD.txt`](http/full/SCORECARD.txt).
