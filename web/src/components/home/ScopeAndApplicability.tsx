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
import { fadeUpVariant, staggerContainer } from "./motion";

export const ScopeAndApplicability = () => {
  return (
    <section id="scope" className="py-24 border-t border-border/50 relative bg-background/50">
      <motion.div 
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          <motion.div variants={fadeUpVariant}>
            <h2 className="text-3xl font-bold mb-6 font-sans flex items-center gap-3">
              <Code className="text-primary w-8 h-8" />
              Purpose & Scope
            </h2>
            <div className="prose prose-invert prose-lg text-secondary-foreground font-light leading-relaxed">
              <p>
                The UHBS v4.5.1 framework provides a rigorous technical foundation for evaluating the efficacy, safety, and realism of deception assets prior to deployment.
              </p>
              <p className="mt-4">
                Historically, deception technology has been evaluated subjectively. UHBS introduces a verifiable, deterministic mathematical model designed to expose flaws in protocol state machines, containment boundaries, and behavioral realism.
              </p>
            </div>
            
            <div className="mt-8 bg-primary/5 border-l-4 border-primary/50 p-6">
              <div className="flex items-start gap-4">
                <Shield className="w-6 h-6 text-primary shrink-0 mt-1" />
                <div>
                  <h4 className="text-primary font-semibold font-mono mb-2 uppercase tracking-wide text-sm">Vendor-Neutral Baseline</h4>
                  <p className="text-secondary-foreground text-sm">
                    UHBS v4.5.1 is an open-source evaluation framework for comparing and grading honeypots by class and protocol — mathematically reproducible, not a consortium or adopted industry standard.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 border border-warning/40 bg-warning/5 p-5 flex gap-4 items-start">
              <AlertTriangle className="w-6 h-6 text-warning shrink-0 mt-0.5" />
              <div>
                <h4 className="font-mono text-warning text-xs uppercase tracking-wider mb-2">Production Baseline</h4>
                <p className="text-sm text-secondary-foreground leading-relaxed">
                  Organizations <span className="text-foreground font-semibold">MAY</span> use UHBS as an internal gate. It is <span className="text-foreground font-semibold">RECOMMENDED</span> that active decoys meet <span className="text-foreground font-semibold">UHQS &gt; 80</span> with a passing Safety Gate before production deployment. See the docs for status and limitations.
                </p>
              </div>
            </div>
          </motion.div>
          
          <motion.div variants={fadeUpVariant}>
            <h3 className="text-xl font-mono mb-8 text-foreground/80 border-b border-border pb-4">Universal Applicability Matrix</h3>
            
            <div className="space-y-6">
              {[
                { title: "Standard IT Services", desc: "SSH, Telnet, HTTP/S, RDP, SMB, FTP, DB RPCs", icon: Server },
                { title: "Industrial OT/ICS", desc: "Modbus TCP, DNP3, EtherNet/IP, BACnet, S7comm", icon: Cpu },
                { title: "Next-Gen AI & Generative Decoys", desc: "LLM-backed shells, dynamic synthetic filesystems", icon: Box },
                { title: "Cloud & SaaS Control Planes", desc: "Public-cloud control-plane APIs, container orchestration, OAuth / identity", icon: Globe }
              ].map((cat, i) => (
                <div key={i} className="flex gap-4 items-center bg-card p-4 border border-border/50 hover:border-primary/50 transition-colors group">
                  <div className="w-12 h-12 bg-background flex items-center justify-center border border-border group-hover:border-primary transition-colors">
                    <cat.icon className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{cat.title}</h4>
                    <p className="font-mono text-xs text-muted-foreground mt-1">{cat.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
};

// Section 3: Core Architecture
