import { motion } from "framer-motion";
import { Shield, GitCommit } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { mkdocsUrl } from "@/lib/urls";
import { fadeUpVariant, staggerContainer } from "./motion";

export const FiveDimensionComparison = () => {
  const mappingRows = [
    {
      dim: "Fingerprinting Resistance",
      module: "Module A",
      moduleName: "Protocol & Syntax Fidelity",
      color: "text-main",
      expansion:
        "Adds statistical Inter-Arrival Time (IAT) side-channel testing via Kolmogorov-Smirnov distribution test and strict finite state machine (FSM) validation.",
    },
    {
      dim: "Interaction",
      module: "Module B",
      moduleName: "Behavioral & Stateful Realism",
      color: "text-main",
      expansion:
        "Evaluates dynamic cross-session state persistence (100% state modification retention) and non-UTF8 binary fuzzing.",
    },
    {
      dim: "Data Quality",
      module: "Module C",
      moduleName: "Telemetry Quality & Pipeline Resilience",
      color: "text-main",
      expansion:
        "Validates only declared native/export formats, tests sink-side injection resilience, and measures required observables, completeness, and timeliness against ground truth.",
    },
    {
      dim: "Stealth & Containment",
      module: "Module D",
      moduleName: "Safety, Containment & Boundary Controls",
      color: "text-danger",
      expansion:
        "Separates a fail-closed critical-control verdict from diagnostic hardening. Failure or missing evidence is Ungraded and cannot be averaged away.",
    },
    {
      dim: "Resource Efficiency",
      module: "Module E",
      moduleName: "Scalability, Latency & Stress Performance",
      color: "text-warning",
      expansion:
        "Compares response percentiles with TPS-specific thresholds and records behavior under bounded, authorized lab load.",
    },
    {
      dim: "— Not Covered —",
      module: "Module F",
      moduleName: "White-Box Static Code Audit",
      color: "text-success",
      expansion:
        "Module F (white-box): Scans repository code, container build manifests, and system prompts for SAST flaws, default keys, and unhandled command stubs.",
      isNew: true,
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
          <div className="h-0.5 w-8 bg-main" />
          <span className="font-mono text-main uppercase tracking-widest text-xs">
            Framework Analysis
          </span>
        </motion.div>
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-heading mb-4 flex items-center gap-3">
            <GitCommit className="text-main w-8 h-8" aria-hidden />
            UHBS v5.0.0 vs. 5-Dimension Framework
          </h2>
          <p className="text-muted-foreground max-w-3xl leading-relaxed">
            UHBS turns common honeypot quality ideas into a practical grading system: it checks both
            the code and the live decoy, applies a hard safety gate when containment fails, and covers
            newer decoy types such as AI and industrial systems. For a deeper side-by-side with other
            approaches, see the{" "}
            <a href={mkdocsUrl("mappings/related-frameworks/")} className="text-main hover:underline">
              related frameworks
            </a>{" "}
            page.
          </p>
        </motion.div>

        <motion.div variants={fadeUpVariant} className="mb-16">
          <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider mb-4">
            Direct Dimension Mapping
          </div>
          <div className="border-2 border-border rounded-base shadow-shadow bg-secondary-background overflow-x-auto">
            <table className="w-full text-left text-sm font-mono">
              <thead>
                <tr className="border-b border-border text-muted-foreground bg-page">
                  <th className="py-3 px-4 font-normal w-1/4">5-Dimension Metric</th>
                  <th className="py-3 px-4 font-normal w-1/5">UHBS v5.0.0 Module</th>
                  <th className="py-3 px-4 font-normal">Key Expansion in UHBS v5.0.0</th>
                </tr>
              </thead>
              <tbody>
                {mappingRows.map((row, i) => (
                  <tr
                    key={i}
                    className="border-b border-border last:border-b-0 odd:bg-slate-50/80"
                  >
                    <td className="py-4 px-4 align-top">
                      <div className="flex items-center gap-2">
                        {row.isNew && (
                          <Badge variant="success" className="text-[10px] uppercase tracking-wider">
                            New
                          </Badge>
                        )}
                        <span
                          className={
                            row.isNew ? "text-muted-foreground italic" : "text-foreground"
                          }
                        >
                          {row.dim}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-4 align-top">
                      <div>
                        <span className={`font-heading ${row.color}`}>{row.module}</span>
                        <div className="text-muted-foreground text-xs mt-0.5 leading-relaxed">
                          {row.moduleName}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-muted-foreground text-xs leading-relaxed align-top">
                      {row.expansion}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        <motion.div variants={fadeUpVariant}>
          <Alert className="bg-background">
            <Shield className="text-black" />
            <AlertTitle className="font-mono text-sm uppercase tracking-wide text-black">
              Bottom Line for Security Leadership
            </AlertTitle>
            <AlertDescription>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Five-dimension proposals provide a useful conceptual lens for categorizing honeypot
                quality. UHBS v5.0.0 operationalizes overlapping concerns with versioned checks and
                evidence — adding a static audit plane (Module F), a fail-closed critical-control
                verdict, and target profiles for GenAI and OT/ICS decoy classes. This remains an
                experimental framework, not independent certification. See the{" "}
                <a href={mkdocsUrl("mappings/related-frameworks/")} className="text-main hover:underline">
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
