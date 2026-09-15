import { motion } from "framer-motion";
import { Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const EvaluationModules = () => {
  const modules = [
    {
      letter: "A",
      name: "Protocol & Syntax Fidelity",
      obj: "Measure protocol header parity and state machine correctness.",
      steps: ["FSM inspection", "Header parity comparison", "Statistical side-channel analysis"],
    },
    {
      letter: "B",
      name: "Behavioral & Stateful Realism",
      obj: "Evaluate how closely the decoy mimics persistent complex interactions.",
      steps: ["Cross-session state persistence", "Payload handling depth", "Input stress fuzzing"],
    },
    {
      letter: "C",
      name: "Telemetry Quality & Resilience",
      obj: "Ensure high-signal alert generation and pipeline integrity.",
      steps: ["STIX 2.1 / ECS schema conformance", "Log injection resistance", "Event correlation latency"],
    },
    {
      letter: "D",
      name: "Safety, Containment & Boundary",
      obj: "Verify isolation controls and prevent adversarial leverage.",
      steps: ["OOB egress sweeps", "Container escape / LPE checks", "GenAI prompt injection audit"],
      alert: "Critical Safety Gate",
    },
    {
      letter: "E",
      name: "Scalability & Latency Stress",
      obj: "Determine performance degradation under heavy adversarial probing.",
      steps: ["Connection saturation", "Resource exhaustion tests", "P95 Latency profiling (<150ms)"],
    },
    {
      letter: "F",
      name: "White-Box Static Code Audit",
      obj: "Identify intrinsic code flaws before deployment.",
      steps: ["SAST tool scanning (static analysis)", "Hardcoded key detection", "Code coverage & logic review"],
    },
  ];

  return (
    <section id="modules" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-heading mb-4 flex items-center gap-3">
            <Layers className="text-main w-8 h-8" aria-hidden />
            Six Evaluation Modules
          </h2>
          <p className="text-muted-foreground">
            The modular assessment framework for computing the final UHQS score.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {modules.map((m) => (
            <motion.div key={m.letter} variants={fadeUpVariant}>
              <Card className="h-full relative">
                {m.alert && (
                  <Badge
                    variant="danger"
                    className="absolute top-0 right-0 rounded-none rounded-tr-base rounded-bl-base border-t-0 border-r-0 uppercase tracking-wider"
                  >
                    {m.alert}
                  </Badge>
                )}
                <CardHeader>
                  <div className="flex items-baseline gap-4">
                    <span className="text-5xl font-heading font-mono text-main/30">{m.letter}</span>
                    <CardTitle className="text-lg leading-tight flex-1 pt-2">{m.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col flex-1">
                  <p className="text-sm text-muted-foreground mb-6 flex-1">{m.obj}</p>
                  <div className="space-y-2 mt-auto border-t-2 border-border pt-4">
                    {m.steps.map((step) => (
                      <div
                        key={step}
                        className="flex gap-2 items-start text-xs font-mono text-muted-foreground"
                      >
                        <span className="text-main mt-0.5">›</span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};
