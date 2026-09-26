# Tutorial: grade Conpot with UHBS (quick + full)

**Target:** [mushorg/conpot](https://github.com/mushorg/conpot) · Modbus `:5020`  
**Commit:** `35e2dfeca70c3b7d961843bd08f35529a75eaed2` (`main`)

Upstream Dockerfile is the documented install path. Lab wrapper `docs/conformance/labs/conpot/Dockerfile.lab` pins `setuptools<81` because `fs` still imports `pkg_resources`. Grade **inside `uhbs-lab` on port 5020** (not host-mapped 502). Full load is `--concurrency 5 --requests 50`.

Exact commands: [EXECUTION-STEPS.md](EXECUTION-STEPS.md). **Published (UHBS 5.0.0):** INCOMPLETE / ungraded.
