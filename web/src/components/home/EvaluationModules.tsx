import { motion } from "framer-motion";
import { Info, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { InfoTip } from "./InfoTip";
import { fadeUpVariant, staggerContainer } from "./motion";

type ModuleStep = { label: string; tip: string };

type ModuleDef = {
  letter: string;
  name: string;
  nameTip: string;
  obj: string;
  steps: ModuleStep[];
  alert?: string;
};

const MODULES: ModuleDef[] = [
  {
    letter: "A",
    name: "Protocol & Syntax Fidelity",
    nameTip:
      "Checks whether the decoy “speaks” the network protocol the way a real service would — correct handshakes, headers, and conversation rules.",
    obj: "Measure protocol header parity and state machine correctness.",
    steps: [
      {
        label: "FSM inspection",
        tip: "FSM = finite state machine: the allowed sequence of steps in a connection (connect → login → command…). We check the decoy follows those rules instead of accepting anything.",
      },
      {
        label: "Header parity comparison",
        tip: "Compares response headers and banners to a real service so attackers don’t spot odd or missing fields that scream “honeypot.”",
      },
      {
        label: "Statistical side-channel analysis",
        tip: "Looks at timing and packet patterns. If replies are unnaturally fast, slow, or identical every time, skilled attackers can fingerprint the decoy.",
      },
    ],
  },
  {
    letter: "B",
    name: "Behavioral & Stateful Realism",
    nameTip:
      "Tests whether the decoy behaves like a real system over time — remembering sessions, handling messy input, and reacting believably.",
    obj: "Evaluate how closely the decoy mimics persistent complex interactions.",
    steps: [
      {
        label: "Cross-session state persistence",
        tip: "If you change something in one visit, does it still look changed next time? Real systems keep state; shallow decoys often reset everything.",
      },
      {
        label: "Payload handling depth",
        tip: "How well it processes real commands or data payloads — not just a canned “OK” for every request.",
      },
      {
        label: "Input stress fuzzing",
        tip: "Sends weird, broken, or oversized input on purpose. A solid decoy fails gracefully; a fragile one crashes or replies nonsensically.",
      },
    ],
  },
  {
    letter: "C",
    name: "Telemetry Quality & Resilience",
    nameTip:
      "Judges the alerts and logs the decoy produces: are they useful, correctly formatted, and hard for an attacker to poison?",
    obj: "Ensure high-signal alert generation and pipeline integrity.",
    steps: [
      {
        label: "STIX 2.1 / ECS schema conformance",
        tip: "STIX and ECS are common formats security tools expect. We check logs match those shapes so they plug into SIEMs without custom hacks.",
      },
      {
        label: "Log injection resistance",
        tip: "Attackers sometimes stuff fake text into logs to confuse analysts. We check the decoy doesn’t let that corrupt its records.",
      },
      {
        label: "Event correlation latency",
        tip: "How quickly useful events show up after activity. Slow or missing alerts reduce the value of running a honeypot.",
      },
    ],
  },
  {
    letter: "D",
    name: "Safety, Containment & Boundary",
    nameTip:
      "The safety gate: can the decoy be used to break out, reach other systems, or leak data? Failures here can zero the whole score.",
    obj: "Verify isolation controls and prevent adversarial leverage.",
    alert: "Critical Safety Gate",
    steps: [
      {
        label: "OOB egress sweeps",
        tip: "OOB = out-of-band: we check whether the decoy can open unexpected outbound connections (a classic sign of weak containment).",
      },
      {
        label: "Container escape / LPE checks",
        tip: "LPE = local privilege escalation. Tests whether an attacker inside the decoy can break the sandbox or become admin on the host.",
      },
      {
        label: "GenAI prompt injection audit",
        tip: "For AI-backed decoys: tries to trick the model into leaking its system prompt or ignoring safety rules.",
      },
    ],
  },
  {
    letter: "E",
    name: "Scalability & Latency Stress",
    nameTip:
      "Puts the decoy under load to see if it stays responsive or falls over when many connections hit it at once.",
    obj: "Determine performance degradation under heavy adversarial probing.",
    steps: [
      {
        label: "Connection saturation",
        tip: "Opens many connections at once to see if the decoy stays up or starts refusing / hanging.",
      },
      {
        label: "Resource exhaustion tests",
        tip: "Pushes memory and CPU hard. A production-worthy decoy should degrade gracefully, not melt the host.",
      },
      {
        label: "P95 Latency profiling (<150ms)",
        tip: "P95 means 95% of replies should be faster than this. UHBS targets under 150ms so the decoy still feels like a real service under load.",
      },
    ],
  },
  {
    letter: "F",
    name: "White-Box Static Code Audit",
    nameTip:
      "Reviews the decoy’s source and build before it runs — looking for baked-in secrets, weak defaults, and obvious code flaws.",
    obj: "Identify intrinsic code flaws before deployment.",
    steps: [
      {
        label: "SAST tool scanning (static analysis)",
        tip: "SAST = static application security testing: automated scanners that read code without running it to flag common bugs.",
      },
      {
        label: "Hardcoded key detection",
        tip: "Searches for passwords, SSH keys, or API tokens left in the code or config — a classic honeypot giveaway and a real risk.",
      },
      {
        label: "Code coverage & logic review",
        tip: "Checks how much of the intended behavior is actually implemented vs stubbed, and spot-checks critical logic paths.",
      },
    ],
  },
];

export const EvaluationModules = () => {
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
            The modular assessment framework for computing the final UHQS score. Hover the{" "}
            <Info className="inline size-3.5 align-text-bottom text-muted-foreground" aria-hidden />{" "}
            icons for plain-language explanations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {MODULES.map((m) => (
            <motion.div key={m.letter} variants={fadeUpVariant}>
              <Card className="h-full relative overflow-visible">
                {m.alert && (
                  <Badge
                    variant="danger"
                    className="absolute top-0 right-0 z-10 rounded-none rounded-tr-base rounded-bl-base border-t-0 border-r-0 uppercase tracking-wider"
                  >
                    {m.alert}
                  </Badge>
                )}
                <CardHeader>
                  <div className="flex items-baseline gap-4">
                    <span className="text-5xl font-heading font-mono text-main/30">{m.letter}</span>
                    <CardTitle className="text-lg leading-tight flex-1 pt-2 inline-flex items-start gap-1.5">
                      <span>{m.name}</span>
                      <InfoTip label={m.name} className="mt-1">
                        {m.nameTip}
                      </InfoTip>
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col flex-1 overflow-visible">
                  <p className="text-sm text-muted-foreground mb-6 flex-1">{m.obj}</p>
                  <div className="space-y-2 mt-auto border-t-2 border-border pt-4">
                    {m.steps.map((step) => (
                      <div
                        key={step.label}
                        className="flex gap-2 items-start text-xs font-mono text-muted-foreground"
                      >
                        <span className="text-main mt-0.5">›</span>
                        <span className="inline-flex items-start gap-1.5 flex-1 min-w-0">
                          <span>{step.label}</span>
                          <InfoTip label={step.label}>{step.tip}</InfoTip>
                        </span>
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
