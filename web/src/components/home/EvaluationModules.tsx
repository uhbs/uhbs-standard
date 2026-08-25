import { motion } from "framer-motion";
import {
  Layers,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const EvaluationModules = () => {
  const modules = [
    {
      letter: "A", name: "Protocol & Syntax Fidelity", color: "text-cyan", border: "border-cyan/30",
      obj: "Measure protocol header parity and state machine correctness.",
      steps: ["FSM inspection", "Header parity comparison", "Statistical side-channel analysis"]
    },
    {
      letter: "B", name: "Behavioral & Stateful Realism", color: "text-blue-400", border: "border-blue-400/30",
      obj: "Evaluate how closely the decoy mimics persistent complex interactions.",
      steps: ["Cross-session state persistence", "Payload handling depth", "Input stress fuzzing"]
    },
    {
      letter: "C", name: "Telemetry Quality & Resilience", color: "text-indigo-400", border: "border-indigo-400/30",
      obj: "Ensure high-signal alert generation and pipeline integrity.",
      steps: ["STIX 2.1 / ECS schema conformance", "Log injection resistance", "Event correlation latency"]
    },
    {
      letter: "D", name: "Safety, Containment & Boundary", color: "text-danger", border: "border-danger",
      obj: "Verify isolation controls and prevent adversarial leverage.",
      steps: ["OOB egress sweeps", "Container escape / LPE checks", "GenAI prompt injection audit"],
      alert: "Critical Safety Gate"
    },
    {
      letter: "E", name: "Scalability & Latency Stress", color: "text-warning", border: "border-warning/30",
      obj: "Determine performance degradation under heavy adversarial probing.",
      steps: ["Connection saturation", "Resource exhaustion tests", "P95 Latency profiling (<150ms)"]
    },
    {
      letter: "F", name: "White-Box Static Code Audit", color: "text-success", border: "border-success/30",
      obj: "Identify intrinsic code flaws before deployment.",
      steps: ["SAST tool scanning (static analysis)", "Hardcoded key detection", "Code coverage & logic review"]
    }
  ];

  return (
    <section id="modules" className="py-24 border-t border-border/50 bg-[#0f1629]">
      <motion.div 
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4 flex items-center gap-3">
            <Layers className="text-primary w-8 h-8" />
            Six Evaluation Modules
          </h2>
          <p className="text-secondary-foreground">The modular assessment framework for computing the final UHQS score.</p>
        </motion.div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {modules.map((m, i) => (
            <motion.div key={i} variants={fadeUpVariant} className={`bg-background border ${m.border} p-6 flex flex-col h-full hover:-translate-y-1 transition-transform duration-300 relative`}>
              {m.alert && (
                <div className="absolute top-0 right-0 bg-danger text-danger-foreground text-xs font-bold px-3 py-1 uppercase tracking-wider font-mono">
                  {m.alert}
                </div>
              )}
              
              <div className="flex items-baseline gap-4 mb-4">
                <span className={`text-5xl font-bold font-mono opacity-20 ${m.color}`}>{m.letter}</span>
                <h3 className="text-lg font-bold leading-tight flex-1 pt-2">{m.name}</h3>
              </div>
              
              <p className="text-sm text-secondary-foreground mb-6 flex-1 min-h-[40px]">{m.obj}</p>
              
              <div className="space-y-2 mt-auto border-t border-border/50 pt-4">
                {m.steps.map((step, idx) => (
                  <div key={idx} className="flex gap-2 items-start text-xs font-mono text-muted-foreground">
                    <span className="text-primary opacity-50 mt-0.5">›</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

// Section 5: 5-Dimension Framework Comparison
