import { motion } from "framer-motion";
import {
  Shield,
  CheckCircle,
  XCircle,
  GitCommit,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const FiveDimensionComparison = () => {
  const mappingRows = [
    {
      dim: "Fingerprinting Resistance",
      module: "Module A",
      moduleName: "Protocol & Syntax Fidelity",
      color: "text-main",
      expansion: "Adds statistical Inter-Arrival Time (IAT) side-channel testing via Kolmogorov-Smirnov distribution test and strict finite state machine (FSM) validation.",
    },
    {
      dim: "Interaction",
      module: "Module B",
      moduleName: "Behavioral & Stateful Realism",
      color: "text-main",
      expansion: "Evaluates dynamic cross-session state persistence (100% state modification retention) and non-UTF8 binary fuzzing.",
    },
    {
      dim: "Data Quality",
      module: "Module C",
      moduleName: "Telemetry Quality & Pipeline Resilience",
      color: "text-main",
      expansion: "Enforces 100% schema compliance against STIX 2.1, OpenTelemetry, and ECS standards, and tests SIEM log-parser injection resistance.",
    },
    {
      dim: "Stealth & Containment",
      module: "Module D",
      moduleName: "Safety, Containment & Boundary Controls",
      color: "text-danger",
      expansion: "Upgraded from a simple score into a Non-Linear Safety Gate (δ_C) with out-of-bound egress sweeps and exponential penalty on breach.",
    },
    {
      dim: "Resource Efficiency",
      module: "Module E",
      moduleName: "Scalability, Latency & Stress Performance",
      color: "text-warning",
      expansion: "Enforces strict response percentile cutoffs (P95 < 150ms) under load and tests circuit-breaker recovery under memory flooding.",
    },
    {
      dim: "— Not Covered —",
      module: "Module F",
      moduleName: "White-Box Static Code Audit",
      color: "text-success",
      expansion: "Module F (white-box): Scans repository code, container build manifests, and system prompts for SAST flaws, default keys, and unhandled command stubs.",
      isNew: true,
    },
  ];

  const differences = [
    {
      num: "01",
      title: "Dual-Plane Audit vs. Runtime-Only",
      left: { label: "5-Dimension Framework", text: "Functions purely as an operational runtime framework, observing honeypot behavior during active exposure." },
      right: { label: "UHBS v4.6.0", text: "Employs a Dual-Plane Audit Philosophy — requires pre-deployment static code analysis (Module F) to catch hardcoded SSH keys, static seeds, or vulnerable command wrappers before dynamic sandbox probing begins." },
    },
    {
      num: "02",
      title: "Non-Linear Safety Gate vs. Linear Averaging",
      left: { label: "5-Dimension Framework", text: "Aggregates metrics using simple linear weighted averages. A high interaction score can mask a serious containment flaw, allowing dangerous decoys to pass evaluation." },
      right: { label: "UHBS v4.6.0", text: "Implements a strict Safety Gate Multiplier (δ_C). If Module D containment drops below 95/100, an exponential penalty degrades the entire UHQS score regardless of performance elsewhere." },
    },
    {
      num: "03",
      title: "Profile-Adaptive Context (TPS) vs. Static Metrics",
      left: { label: "5-Dimension Framework", text: "Applies identical static metric weights across all honeypot classes — a SCADA PLC and an SSH shell are evaluated with the same emphasis." },
      right: { label: "UHBS v4.6.0", text: "Target Profile Specification (profile.yaml) adjusts evaluation weights. ICS-SCADA weights protocol fidelity at w_A = 0.35, while POSIX shells emphasize state behavior at w_B = 0.25." },
    },
    {
      num: "04",
      title: "GenAI & Cloud Coverage vs. Traditional IT Only",
      left: { label: "5-Dimension Framework", text: "Designed around traditional IT OS and network service emulators — SSH servers, HTTP endpoints, and network stacks." },
      right: { label: "UHBS v4.6.0", text: "Explicitly tests next-generation decoys: indirect prompt injections, system prompt leaks, context exhaustion attacks, and cloud API boundary breaches across public-cloud control planes and container orchestration surfaces." },
    },
  ];

  return (
    <section id="compare" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-4 flex items-center gap-3">
          <div className="h-0.5 w-8 bg-main"></div>
          <span className="font-mono text-main uppercase tracking-widest text-xs">Framework Analysis</span>
        </motion.div>
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-heading mb-4 flex items-center gap-3">
            <GitCommit className="text-main w-8 h-8" aria-hidden />
            UHBS v4.6.0 vs. 5-Dimension Framework
          </h2>
          <p className="text-muted-foreground max-w-3xl">
            Proposed five-dimension honeypot metrics (interaction, data quality, resource efficiency, stealth, fingerprinting resistance) are a useful conceptual lens—not an adopted industry standard. UHBS v4.6.0 operationalizes overlapping axes with dual-plane auditing, a non-linear Safety Gate, and coverage for modern decoy classes. For the full evidence-graded comparison against fourteen framework/model families, see the{" "}
            <a href="mkdocs/mappings/related-frameworks/" className="text-main hover:underline">
              related frameworks
            </a>{" "}
            mapping.
          </p>
        </motion.div>

        {/* Mapping Table */}
        <motion.div variants={fadeUpVariant} className="mb-16">
          <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider mb-4">Direct Dimension Mapping</div>
          <div className="border-2 border-border rounded-base shadow-shadow bg-secondary-background overflow-x-auto">
            <table className="w-full text-left text-sm font-mono">
              <thead>
                <tr className="border-b border-border text-muted-foreground bg-page">
                  <th className="py-3 px-4 font-normal w-1/4">5-Dimension Metric</th>
                  <th className="py-3 px-4 font-normal w-1/5">UHBS v4.6.0 Module</th>
                  <th className="py-3 px-4 font-normal">Key Expansion in UHBS v4.6.0</th>
                </tr>
              </thead>
              <tbody>
                {mappingRows.map((row, i) => (
                  <tr key={i} className="border-b border-border last:border-b-0 odd:bg-slate-50/80">
                    <td className="py-4 px-4 align-top">
                      <div className="flex items-center gap-2">
                        {row.isNew && (
                          <Badge variant="success" className="text-[10px] uppercase tracking-wider">
                            New
                          </Badge>
                        )}
                        <span className={row.isNew ? "text-muted-foreground italic" : "text-foreground"}>{row.dim}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 align-top">
                      <div>
                        <span className={`font-heading ${row.color}`}>{row.module}</span>
                        <div className="text-muted-foreground text-xs mt-0.5 leading-relaxed">{row.moduleName}</div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-muted-foreground text-xs leading-relaxed align-top">{row.expansion}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Architectural Differences */}
        <motion.div variants={fadeUpVariant} className="mb-8">
          <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider mb-8">Key Architectural Differences</div>
          <div className="space-y-4">
            {differences.map((diff, i) => (
              <motion.div key={i} variants={fadeUpVariant}>
                <Card className="overflow-hidden gap-0 py-0">
                  <CardHeader className="border-b-2 border-border bg-background py-3 flex flex-row items-center gap-4 [--card-spacing:--spacing(6)]">
                    <span className="font-mono text-muted-foreground text-sm">{diff.num}</span>
                    <CardTitle className="text-sm text-black">{diff.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
                      {/* Left: 5-Dimension */}
                      <div className="p-6">
                        <div className="flex items-center gap-2 mb-3">
                          <XCircle className="w-4 h-4 text-muted-foreground shrink-0" aria-hidden />
                          <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">{diff.left.label}</span>
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed">{diff.left.text}</p>
                      </div>
                      {/* Right: UHBS v4.6.0 */}
                      <div className="p-6 bg-background/60">
                        <div className="flex items-center gap-2 mb-3">
                          <CheckCircle className="w-4 h-4 text-main shrink-0" aria-hidden />
                          <span className="font-mono text-xs text-main uppercase tracking-wider">{diff.right.label}</span>
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed">{diff.right.text}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Summary callout */}
        <motion.div variants={fadeUpVariant}>
          <Alert className="bg-background">
            <Shield className="text-black" />
            <AlertTitle className="font-mono text-sm uppercase tracking-wide text-black">
              Bottom Line for Security Leadership
            </AlertTitle>
            <AlertDescription>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Five-dimension proposals provide a useful conceptual lens for categorizing honeypot quality. UHBS v4.6.0 turns overlapping concerns into a machine-verifiable evaluation — adding a pre-deployment code audit plane (Module F), a non-linear safety gate that makes containment failures non-maskable, and explicit support for GenAI and OT/ICS decoy classes. See the{" "}
                <a href="mkdocs/mappings/related-frameworks/" className="text-main hover:underline">
                  evidence-based framework comparison
                </a>{" "}
                for CDMM, game-theoretic models, Honeyval, ICS research, and more.
              </p>
            </AlertDescription>
          </Alert>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Section 6: Scoring Methodology
