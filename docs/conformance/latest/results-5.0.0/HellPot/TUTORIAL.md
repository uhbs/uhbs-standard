# Tutorial: grade HellPot (yunginnanet) (http) with UHBS (quick + full)

**Status:** Informative · evaluation proof  
**Outputs:** [`quick/`](http/quick/README.md) · [`full/`](http/full/README.md) · [METHODOLOGY.md](METHODOLOGY.md) · [EXECUTION-STEPS.md](http/EXECUTION-STEPS.md)

Clone `https://github.com/yunginnanet/HellPot.git` at `main` HEAD `0ba62c99ea4599ec32474e4982a8ea4d4105c471`. Runtime: `ubuntu-wrapper` / `ubuntu:latest`. Upstream Dockerfile is golang:1.23 + distroless; lab uses golang:1.23 builder then ubuntu:latest runtime with catch-all bind and no curl UA blacklist.

Exact commands: [EXECUTION-STEPS.md](http/EXECUTION-STEPS.md).

**Published results (UHBS 5.0.1):** INCOMPLETE / INCOMPLETE — ungraded unless the Safety Gate passed. See [`http/full/SCORECARD.txt`](http/full/SCORECARD.txt).
