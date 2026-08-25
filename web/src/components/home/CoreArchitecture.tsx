import { motion } from "framer-motion";
import {
  Zap,
  Code,
  ArrowRight,
  Check,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const CoreArchitecture = () => {
  return (
    <section id="architecture" className="py-24 border-t border-border/50">
      <motion.div 
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4">Dual-Plane Audit Philosophy</h2>
          <p className="text-secondary-foreground max-w-2xl mx-auto">Evaluating deception technology requires orthogonal approaches: inspecting the static blueprint and attacking the running instance.</p>
        </motion.div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <motion.div variants={fadeUpVariant} className="bg-card border border-border p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Code className="w-32 h-32 text-primary" />
            </div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 text-primary font-mono text-sm">1</div>
              <h3 className="text-2xl font-bold">White-Box Static Audit</h3>
            </div>
            <p className="text-secondary-foreground mb-6 h-20">Deep codebase and configuration analysis before deployment to identify intrinsic vulnerabilities.</p>
            <ul className="space-y-3 font-mono text-sm text-foreground/80">
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-success" /> Static Credentials Detection</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-success" /> State Machine Logic Flaws</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-success" /> GenAI Prompt Extraction Risks</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-success" /> Dependency Vulnerabilities</li>
            </ul>
          </motion.div>
          
          <motion.div variants={fadeUpVariant} className="bg-card border border-border p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Zap className="w-32 h-32 text-danger" />
            </div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-danger/20 flex items-center justify-center border border-danger/30 text-danger font-mono text-sm">2</div>
              <h3 className="text-2xl font-bold">Dynamic Adversarial Probing</h3>
            </div>
            <p className="text-secondary-foreground mb-6 h-20">Live-fire testing of the honeypot in an isolated sandbox simulating advanced persistent threat behaviors.</p>
            <ul className="space-y-3 font-mono text-sm text-foreground/80">
              <li className="flex items-center gap-2"><ArrowRight className="w-4 h-4 text-danger" /> Network-Level Header Anomalies</li>
              <li className="flex items-center gap-2"><ArrowRight className="w-4 h-4 text-danger" /> Protocol-Level Stress Fuzzing</li>
              <li className="flex items-center gap-2"><ArrowRight className="w-4 h-4 text-danger" /> Execution-Level Escape Attempts</li>
              <li className="flex items-center gap-2"><ArrowRight className="w-4 h-4 text-danger" /> Out-of-Band Egress Sweeps</li>
            </ul>
          </motion.div>
        </div>
        
        <motion.div variants={fadeUpVariant} className="border border-border/50 bg-background p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <span className="font-mono text-sm text-muted-foreground uppercase tracking-wider">Prerequisite Environments</span>
          <div className="flex flex-wrap gap-4">
            <span className="px-3 py-1 bg-secondary text-secondary-foreground text-xs font-mono border border-border/50">Air-Gapped Sandbox</span>
            <span className="px-3 py-1 bg-secondary text-secondary-foreground text-xs font-mono border border-border/50">Gold Baseline System</span>
            <span className="px-3 py-1 bg-secondary text-secondary-foreground text-xs font-mono border border-border/50">Target Profile Specification (TPS)</span>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Section 4: Six Evaluation Modules
