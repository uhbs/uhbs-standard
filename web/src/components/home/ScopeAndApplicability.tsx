import { motion } from "framer-motion";
import {
  Shield,
  Code,
  AlertTriangle,
  Server,
  Box,
  Globe,
  Cpu,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const ScopeAndApplicability = () => {
  return (
    <section id="scope" className="py-24 border-t-2 border-border relative bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          <motion.div variants={fadeUpVariant}>
            <h2 className="text-3xl font-heading mb-6 flex items-center gap-3">
              <Code className="text-main w-8 h-8" aria-hidden />
              Purpose & Scope
            </h2>
            <div className="text-lg text-muted-foreground font-base leading-relaxed space-y-4">
              <p>
                UHBS v5.0.0 defines a versioned lab method for evaluating selected technical
                properties of a declared deception asset and configuration.
              </p>
              <p>
                It combines protocol and behavioral checks, telemetry ground truth, fail-closed
                containment evidence, resilience observations, and static audit signals. It does not
                replace architecture review, vulnerability assessment, legal approval, or operational
                risk acceptance.
              </p>
            </div>

            <div className="mt-8 border-2 border-border bg-background p-6 shadow-shadow">
              <div className="flex items-start gap-4">
                <Shield className="w-6 h-6 text-black shrink-0 mt-1" aria-hidden />
                <div>
                  <h4 className="text-black font-heading font-mono mb-2 uppercase tracking-wide text-sm">
                    Vendor-Neutral Baseline
                  </h4>
                  <p className="text-muted-foreground text-sm">
                    UHBS v5.0.0 is an open-source evaluation framework for comparing and grading
                    honeypots by class and protocol. Results are reproducible only to the extent shown
                    by their evidence pack and assurance level.
                  </p>
                </div>
              </div>
            </div>

            <Alert className="mt-6 bg-secondary-background">
              <AlertTriangle className="text-warning" />
              <AlertTitle className="font-mono text-xs uppercase tracking-wider text-warning">
                Assessment outcome before grade
              </AlertTitle>
              <AlertDescription>
                Only <span className="text-foreground font-semibold">COMPLETE + GATE_PASSED</span>{" "}
                assessments receive UHQS and a letter grade. Incomplete or critical-control-failed
                assessments are Ungraded. Production-facing thresholds still require broader live
                calibration and independent technical review.
              </AlertDescription>
            </Alert>
          </motion.div>

          <motion.div variants={fadeUpVariant}>
            <h3 className="text-xl font-mono mb-8 text-foreground border-b-2 border-border pb-4">
              Target profile examples
            </h3>

            <div className="space-y-4">
              {[
                {
                  title: "Standard IT Services",
                  desc: "SSH, Telnet, HTTP/S, RDP, SMB, FTP, DB RPCs",
                  icon: Server,
                },
                {
                  title: "Industrial OT/ICS",
                  desc: "Modbus TCP, DNP3, EtherNet/IP, BACnet, S7comm",
                  icon: Cpu,
                },
                {
                  title: "Next-Gen AI & Generative Decoys",
                  desc: "LLM-backed shells, dynamic synthetic filesystems",
                  icon: Box,
                },
                {
                  title: "Cloud & SaaS Control Planes",
                  desc: "Public-cloud control-plane APIs, container orchestration, OAuth / identity",
                  icon: Globe,
                },
              ].map((cat) => (
                <Card key={cat.title} size="sm" className="flex-row items-center gap-4 py-4">
                  <CardContent className="flex items-center gap-4 p-0 px-(--card-spacing) w-full">
                    <div className="w-12 h-12 bg-page flex items-center justify-center border-2 border-border shrink-0">
                      <cat.icon className="w-5 h-5 text-main" aria-hidden />
                    </div>
                    <div>
                      <h4 className="font-heading text-foreground">{cat.title}</h4>
                      <p className="font-mono text-xs text-muted-foreground mt-1">{cat.desc}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <p className="mt-5 text-xs font-mono text-muted-foreground">
              Protocol support and check applicability vary by TPS and harness plugin; this list is
              not a claim of complete protocol coverage.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
};
