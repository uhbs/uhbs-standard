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
                The UHBS v4.6.1 framework provides a rigorous technical foundation for evaluating the
                efficacy, safety, and realism of deception assets prior to deployment.
              </p>
              <p>
                Historically, deception technology has been evaluated subjectively. UHBS introduces a
                verifiable, deterministic mathematical model designed to expose flaws in protocol state
                machines, containment boundaries, and behavioral realism.
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
                    UHBS v4.6.1 is an open-source evaluation framework for comparing and grading
                    honeypots by class and protocol — mathematically reproducible.
                  </p>
                </div>
              </div>
            </div>

            <Alert className="mt-6 bg-secondary-background">
              <AlertTriangle className="text-warning" />
              <AlertTitle className="font-mono text-xs uppercase tracking-wider text-warning">
                Production Baseline
              </AlertTitle>
              <AlertDescription>
                Organizations <span className="text-foreground font-semibold">MAY</span> use UHBS as an
                internal gate. It is <span className="text-foreground font-semibold">RECOMMENDED</span>{" "}
                that active decoys meet{" "}
                <span className="text-foreground font-semibold">UHQS &gt; 80</span> with a passing Safety
                Gate before production deployment. See the docs for status and limitations.
              </AlertDescription>
            </Alert>
          </motion.div>

          <motion.div variants={fadeUpVariant}>
            <h3 className="text-xl font-mono mb-8 text-foreground border-b-2 border-border pb-4">
              Universal Applicability Matrix
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
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
};
