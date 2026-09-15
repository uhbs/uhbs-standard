import { motion } from "framer-motion";
import {
  Shield,
  Activity,
  Globe,
  ArrowRight,
  Layers,
} from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { mkdocsUrl } from "@/lib/urls";
import { fadeUpVariant, staggerContainer } from "./motion";

export const Hero = () => {
  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-24 pb-16 overflow-hidden bg-page">
      <motion.div
        className="container mx-auto px-6 relative z-10"
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="flex items-center gap-3 mb-8">
          <div className="h-1 w-12 bg-main border border-border" />
          <Badge variant="mint" className="uppercase tracking-widest font-mono">
            Evaluation Framework
          </Badge>
        </motion.div>

        <motion.h1
          variants={fadeUpVariant}
          className="text-5xl md:text-7xl font-heading leading-tight mb-6 max-w-4xl text-foreground tracking-tight"
        >
          Universal Honeypot Benchmarking Standard <br className="hidden md:block" />
          <span className="text-muted-foreground font-mono text-4xl md:text-6xl tracking-tighter">
            (UHBS) v4.6.1 <span className="text-main">· 2026</span>
          </span>
        </motion.h1>

        <motion.p
          variants={fadeUpVariant}
          className="text-xl md:text-2xl text-muted-foreground max-w-3xl mb-8 font-base leading-relaxed"
        >
          An objective, repeatable, quantitative methodology for benchmarking honeypots, decoys, and
          deception technology — an open-source evaluation framework.
        </motion.p>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-3 mb-12">
          <ButtonLink href={mkdocsUrl()}>
            Open docs <ArrowRight />
          </ButtonLink>
          <ButtonLink variant="neutral" href="#results">
            Results
          </ButtonLink>
          <ButtonLink variant="neutral" href="#mcp">
            MCP
          </ButtonLink>
          <ButtonLink variant="neutral" href="https://github.com/uhbs/uhbs-standard">
            GitHub
          </ButtonLink>
        </motion.div>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-3 mt-2 mb-12">
          {[
            { label: "Protocol-Agnostic", icon: Globe },
            { label: "Quantitative Scoring 0–100", icon: Activity },
            { label: "Six Evaluation Modules", icon: Layers },
            { label: "Production Baseline", icon: Shield },
          ].map((badge) => (
            <Badge key={badge.label} variant="neutral" className="px-3 py-1.5 text-sm gap-2">
              <badge.icon className="size-4 text-main" aria-hidden />
              {badge.label}
            </Badge>
          ))}
        </motion.div>

        <motion.div variants={fadeUpVariant} className="max-w-4xl">
          <div className="flex items-center justify-between gap-4 mb-3">
            <p className="font-mono text-xs uppercase tracking-widest text-black bg-background border-2 border-border px-2 py-1">
              Demo · install + full UHQS
            </p>
            <a
              href="https://github.com/uhbs/uhbs-standard/blob/main/docs/assets/uhbs-lab-demo.cast"
              className="font-mono text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              asciinema cast →
            </a>
          </div>
          <Card className="overflow-hidden p-0 gap-0 py-0 shadow-shadow">
            <CardContent className="p-0">
              <img
                src={`${import.meta.env.BASE_URL}assets/uhbs-lab-demo.gif`}
                alt="UHBS lab demo: install Cowrie and Conpot, start decoys, full UHQS grades for Cowrie, Conpot, and HellPot"
                className="w-full h-auto block"
                loading="lazy"
              />
            </CardContent>
          </Card>
          <p className="mt-3 font-mono text-xs text-muted-foreground leading-relaxed max-w-3xl">
            Pip-install Cowrie &amp; Conpot, bring up live surfaces, then run full UHQS (modules A–F) —
            Cowrie SSH · Conpot Modbus · HellPot HTTP.
          </p>
        </motion.div>
      </motion.div>
    </section>
  );
};
