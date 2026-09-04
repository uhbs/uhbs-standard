import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { KatexMath } from "../KatexMath";
import { UhqsHumanExplainerTrigger } from "../UhqsHumanExplainer";
import { fadeUpVariant, staggerContainer } from "./motion";

export const ScoringMethodology = () => {
  return (
    <section id="scoring" className="py-24 border-t border-border/50">
      <motion.div 
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4 flex items-center gap-3">
            <Activity className="text-primary w-8 h-8" />
            Scoring Methodology
          </h2>
          <p className="text-secondary-foreground">Computing the Universal Honeypot Quality Score (UHQS).</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <motion.div variants={fadeUpVariant} className="lg:col-span-7 bg-card border border-border p-4 md:p-6">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4 px-2">
              <h3 className="font-mono text-primary text-sm uppercase tracking-wider">The UHQS 4.5.2 Formula</h3>
              <UhqsHumanExplainerTrigger />
            </div>
            <div className="uhqs-katex uhqs-katex-display space-y-4">
              <KatexMath
                display
                className="block"
                label="UHQS equals delta-C times the weighted sum of modules A, B, C, E, and F"
                tex={`\\mathrm{UHQS} = \\delta_{C}\\cdot\\bigl(w_{A}S_{A}+w_{B}S_{B}+w_{C}S_{C}+w_{E}S_{E}+w_{F}S_{F}\\bigr)`}
              />
              <KatexMath
                display
                className="block uhqs-katex-danger"
                label="Safety Gate: delta-C is 1 when Module D is at least 95, otherwise C over 100 squared"
                tex={`\\delta_{C} = \\begin{cases} 1 & \\text{if } C \\ge 95 \\\\ \\bigl(C/100\\bigr)^{2} & \\text{if } C < 95 \\end{cases}`}
              />
            </div>
            <p className="mt-4 px-2 text-xs text-muted-foreground font-mono leading-relaxed">
              Module D is missing from the parentheses on purpose: containment becomes{" "}
              <KatexMath className="uhqs-katex uhqs-katex-accent inline" tex={`\\delta_{C}`} />{" "}
              and multiplies the whole score. Typeset with{" "}
              <a href="https://katex.org/" className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">KaTeX</a>
              . Full normative detail:{" "}
              <a href="mkdocs/specification/scoring-formula/" className="text-primary hover:underline">scoring formula</a>.
            </p>

            <div className="grid grid-cols-2 gap-4 font-mono text-sm text-secondary-foreground mt-6 px-2">
              <div>
                <KatexMath className="uhqs-katex uhqs-katex-accent inline" tex={`\\delta_{C}`} /> : Safety Gate Multiplier (Module D)
              </div>
              <div>
                <KatexMath className="uhqs-katex inline" tex={`S_{x}`} /> : Score for Module X (0–100)
              </div>
              <div>
                <KatexMath className="uhqs-katex inline" tex={`w_{x}`} /> : Profile-Adaptive Weight
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-border/50">
              <h4 className="font-mono text-foreground mb-4">Profile-Adaptive Weights (w<sub>x</sub>)</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm font-mono border-collapse">
                  <thead>
                    <tr className="border-b border-border/50 text-muted-foreground">
                      <th className="py-2 font-normal">Target Profile</th>
                      <th className="py-2 font-normal text-right">w<sub>A</sub></th>
                      <th className="py-2 font-normal text-right">w<sub>B</sub></th>
                      <th className="py-2 font-normal text-right">w<sub>C</sub></th>
                      <th className="py-2 font-normal text-right">w<sub>E</sub></th>
                      <th className="py-2 font-normal text-right">w<sub>F</sub></th>
                    </tr>
                  </thead>
                  <tbody className="text-secondary-foreground divide-y divide-border/20">
                    <tr>
                      <td className="py-2 text-foreground">POSIX Shell</td>
                      <td className="py-2 text-right">0.20</td>
                      <td className="py-2 text-right text-primary">0.25</td>
                      <td className="py-2 text-right">0.20</td>
                      <td className="py-2 text-right">0.15</td>
                      <td className="py-2 text-right">0.20</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-foreground">Low-Interaction</td>
                      <td className="py-2 text-right text-primary">0.30</td>
                      <td className="py-2 text-right">0.15</td>
                      <td className="py-2 text-right">0.25</td>
                      <td className="py-2 text-right">0.10</td>
                      <td className="py-2 text-right">0.20</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-foreground">ICS-SCADA</td>
                      <td className="py-2 text-right text-primary">0.35</td>
                      <td className="py-2 text-right">0.20</td>
                      <td className="py-2 text-right">0.15</td>
                      <td className="py-2 text-right">0.10</td>
                      <td className="py-2 text-right">0.20</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-foreground">Web-API</td>
                      <td className="py-2 text-right text-primary">0.25</td>
                      <td className="py-2 text-right">0.20</td>
                      <td className="py-2 text-right">0.20</td>
                      <td className="py-2 text-right">0.15</td>
                      <td className="py-2 text-right">0.20</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
          
          <motion.div variants={fadeUpVariant} className="lg:col-span-5 bg-card border border-border p-8 flex flex-col">
            <h3 className="font-mono text-danger text-sm uppercase tracking-wider mb-6 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> Safety Gate Multiplier (δ<sub>C</sub>)
            </h3>
            <p className="text-sm text-secondary-foreground mb-6">
              A Module D score below 95 triggers exponential degradation of the entire UHQS score. A honeypot that leaks data or allows lateral movement is mathematically rendered useless regardless of realism.
            </p>
            
            <div className="flex-1 overflow-x-auto">
              <table className="w-full text-left font-mono border-collapse">
                <thead>
                  <tr className="border-b border-border/50 text-muted-foreground text-sm">
                    <th className="py-3 font-normal">Module D Score</th>
                    <th className="py-3 font-normal text-right">δ<sub>C</sub> Value</th>
                    <th className="py-3 font-normal text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20 text-sm">
                  <tr>
                    <td className="py-3 text-foreground">95 – 100</td>
                    <td className="py-3 text-right">1.00</td>
                    <td className="py-3 text-right text-success flex justify-end items-center gap-1"><CheckCircle className="w-3 h-3"/> PASS</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-foreground">90 – 94</td>
                    <td className="py-3 text-right">0.81 <span className="text-muted-foreground text-xs">(-19%)</span></td>
                    <td className="py-3 text-right text-warning">WARN</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-foreground">85 – 89</td>
                    <td className="py-3 text-right">0.72 <span className="text-muted-foreground text-xs">(-28%)</span></td>
                    <td className="py-3 text-right text-warning">WARN</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-foreground">75 – 84</td>
                    <td className="py-3 text-right">0.56 <span className="text-muted-foreground text-xs">(-44%)</span></td>
                    <td className="py-3 text-right text-danger">FAIL</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-danger">&lt; 75</td>
                    <td className="py-3 text-right text-danger">0.49 <span className="text-danger/50 text-xs">(-51%)</span></td>
                    <td className="py-3 text-right text-danger flex justify-end items-center gap-1"><XCircle className="w-3 h-3"/> CRIT</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
};

// Optional Advanced Evidence Profile (does not change UHQS) — lab evaluation only
