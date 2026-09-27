# Conpot methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `upstream-docker` · base `python:3.14-slim` · target `conpot:lab-fixed`

Upstream Dockerfile is documented. Compatibility shim: pin `setuptools<81` so `pkg_resources` remains available. Not Ubuntu latest because upstream ships a maintained image.

| Field | Value |
| --- | --- |
| Commit | `35e2dfeca70c3b7d961843bd08f35529a75eaed2` |
| Host / port | `conpot-lab:5020` (container; host map 502 is not the graded port) |
| Verdict | INCOMPLETE / ungraded |

Module E uses moderated concurrency because the default template uses serial Modbus with a 100 ms delay.
