import { motion } from "framer-motion";
import { Activity, ArrowRight } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { KatexMath } from "../KatexMath";
import { UhqsHumanExplainerTrigger } from "../UhqsHumanExplainer";
import { mkdocsUrl } from "@/lib/urls";
import { fadeUpVariant, staggerContainer } from "./motion";

export const ScoringMethodology = () => {
  return (
    <section id="scoring" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-16">
          <h2 className="text-3xl md:text-4xl font-heading mb-4 flex items-center gap-3">
            <Activity className="text-main w-8 h-8" aria-hidden />
            Scoring Methodology
          </h2>
          <p className="text-muted-foreground">
            How UHBS turns six evaluation modules into one quality score from 0 to 100.
          </p>
        </motion.div>

        <motion.div variants={fadeUpVariant} className="max-w-4xl">
          <Card>
            <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
              <CardTitle className="font-mono text-main text-sm uppercase tracking-wider">
                The UHQS 4.6.1 Formula
              </CardTitle>
              <UhqsHumanExplainerTrigger />
            </CardHeader>
            <CardContent>
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

              <div className="mt-6 space-y-4 text-muted-foreground leading-relaxed">
                <p>
                  In plain terms: each module gets a score from 0 to 100. UHBS mixes those scores
                  together (with different emphasis depending on the decoy type), then multiplies the
                  result by a <span className="text-foreground font-medium">safety factor</span>.
                </p>
                <p>
                  That safety factor comes from containment (Module D). If the decoy is well isolated,
                  the factor is 1 and the quality score stands. If containment is weak — for example
                  the decoy can leak data or reach other systems — the factor drops sharply and the
                  whole score falls with it. Looking realistic is not enough when safety fails.
                </p>
                <p>
                  Different honeypot types also care about different strengths (an industrial PLC
                  decoy is not graded exactly like a fake SSH shell). The full weight tables, safety
                  thresholds, and letter grades live in the specification.
                </p>
              </div>

              <div className="mt-8">
                <ButtonLink href={mkdocsUrl("specification/scoring-formula/")}>
                  Full scoring formula in the docs <ArrowRight />
                </ButtonLink>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </section>
  );
};
