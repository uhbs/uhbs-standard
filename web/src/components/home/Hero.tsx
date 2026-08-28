import { motion } from "framer-motion";
import {
  Shield,
  Activity,
  Globe,
  ArrowRight,
  Layers,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const Hero = () => {
  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-24 pb-16 overflow-hidden">
      {/* Decorative background grid elements handled by global CSS background */}
      
      <motion.div 
        className="container mx-auto px-6 relative z-10"
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="flex items-center gap-3 mb-8">
          <div className="h-px w-12 bg-primary"></div>
          <span className="font-mono text-primary uppercase tracking-widest text-sm font-semibold">Evaluation Framework</span>
        </motion.div>
        
        <motion.h1 variants={fadeUpVariant} className="text-5xl md:text-7xl font-bold leading-tight mb-6 max-w-4xl text-foreground font-sans tracking-tight">
          Universal Honeypot Benchmarking Standard <br className="hidden md:block"/>
          <span className="text-muted-foreground font-mono text-4xl md:text-6xl tracking-tighter">(UHBS) v4.5.1 <span className="text-primary/70">· 2026</span></span>
        </motion.h1>
        
        <motion.p variants={fadeUpVariant} className="text-xl md:text-2xl text-secondary-foreground max-w-3xl mb-8 font-light leading-relaxed">
          An objective, repeatable, quantitative methodology for benchmarking honeypots, decoys, and deception technology — an open-source evaluation framework (not a consortium standard).
        </motion.p>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-3 mb-12">
          <a href="mkdocs/" className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 font-mono text-sm font-semibold hover:opacity-90 transition-opacity">
            Open docs <ArrowRight className="w-4 h-4" />
          </a>
          <a href="#results" className="inline-flex items-center gap-2 bg-card border border-border px-5 py-2.5 font-mono text-sm hover:border-primary/50 transition-colors">
            Results
          </a>
          <a href="#mcp" className="inline-flex items-center gap-2 bg-card border border-border px-5 py-2.5 font-mono text-sm hover:border-primary/50 transition-colors">
            MCP
          </a>
          <a href="https://github.com/uhbs/uhbs-standard" className="inline-flex items-center gap-2 bg-card border border-border px-5 py-2.5 font-mono text-sm hover:border-primary/50 transition-colors">
            GitHub
          </a>
        </motion.div>
        
        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4 mt-2 mb-12">
          {[
            { label: "Protocol-Agnostic", icon: Globe },
            { label: "Quantitative Scoring 0–100", icon: Activity },
            { label: "Six Evaluation Modules", icon: Layers },
            { label: "Production Baseline", icon: Shield }
          ].map((badge, i) => (
            <div key={i} className="flex items-center gap-2 bg-card border border-border px-4 py-2.5 rounded-sm terminal-card">
              <badge.icon className="w-4 h-4 text-primary" />
              <span className="font-mono text-sm text-foreground">{badge.label}</span>
            </div>
          ))}
        </motion.div>

        <motion.div variants={fadeUpVariant} className="max-w-4xl">
          <div className="flex items-center justify-between gap-4 mb-3">
            <p className="font-mono text-xs uppercase tracking-widest text-primary">
              Demo · install + full UHQS
            </p>
            <a
              href="https://github.com/uhbs/uhbs-standard/blob/main/docs/assets/uhbs-lab-demo.cast"
              className="font-mono text-xs text-secondary-foreground hover:text-primary transition-colors"
            >
              asciinema cast →
            </a>
          </div>
          <div className="border border-border bg-card/40 overflow-hidden terminal-card">
            <img
              src={`${import.meta.env.BASE_URL}assets/uhbs-lab-demo.gif`}
              alt="UHBS lab demo: install Cowrie and Conpot, start decoys, full UHQS grades for Cowrie, Conpot, and HellPot"
              className="w-full h-auto block"
              loading="lazy"
            />
          </div>
          <p className="mt-3 font-mono text-xs text-secondary-foreground leading-relaxed max-w-3xl">
            Pip-install Cowrie &amp; Conpot, bring up live surfaces, then run full
            UHQS (modules A–F) — Cowrie SSH · Conpot Modbus · HellPot HTTP.
          </p>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Section 2: Scope & Applicability
