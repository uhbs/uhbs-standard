import { motion } from "framer-motion";
import { Zap, Code, ArrowRight, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const CoreArchitecture = () => {
  return (
    <section id="architecture" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-heading mb-4">Dual-Plane Audit Philosophy</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Evaluating deception technology requires orthogonal approaches: inspecting the static
            blueprint and attacking the running instance.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <motion.div variants={fadeUpVariant}>
            <Card className="h-full relative overflow-hidden">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-base bg-background border-2 border-border flex items-center justify-center font-mono text-sm text-black">
                    1
                  </div>
                  <CardTitle className="text-2xl">White-Box Static Audit</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <Code className="absolute top-4 right-4 w-28 h-28 text-main opacity-10" aria-hidden />
                <p className="text-muted-foreground mb-6">
                  Deep codebase and configuration analysis before deployment to identify intrinsic
                  vulnerabilities.
                </p>
                <ul className="space-y-3 font-mono text-sm">
                  {[
                    "Static Credentials Detection",
                    "State Machine Logic Flaws",
                    "GenAI Prompt Extraction Risks",
                    "Dependency Vulnerabilities",
                  ].map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" aria-hidden />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={fadeUpVariant}>
            <Card className="h-full relative overflow-hidden">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-base bg-danger text-black border-2 border-border flex items-center justify-center font-mono text-sm">
                    2
                  </div>
                  <CardTitle className="text-2xl">Dynamic Adversarial Probing</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <Zap className="absolute top-4 right-4 w-28 h-28 text-danger opacity-10" aria-hidden />
                <p className="text-muted-foreground mb-6">
                  Live-fire testing of the honeypot in an isolated sandbox simulating advanced
                  persistent threat behaviors.
                </p>
                <ul className="space-y-3 font-mono text-sm">
                  {[
                    "Network-Level Header Anomalies",
                    "Protocol-Level Stress Fuzzing",
                    "Execution-Level Escape Attempts",
                    "Out-of-Band Egress Sweeps",
                  ].map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <ArrowRight className="w-4 h-4 text-danger" aria-hidden />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </div>

      </motion.div>
    </section>
  );
};
