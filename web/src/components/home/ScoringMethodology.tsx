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
            Assessment eligibility comes first; only complete, gate-passed evidence receives a score.
          </p>
        </motion.div>

        <motion.div variants={fadeUpVariant} className="max-w-4xl">
          <Card>
            <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
              <CardTitle className="font-mono text-main text-sm uppercase tracking-wider">
                The UHQS 5.0.0 Formula
              </CardTitle>
              <UhqsHumanExplainerTrigger />
            </CardHeader>
            <CardContent>
              <div className="uhqs-katex uhqs-katex-display space-y-4">
                <KatexMath
                  display
                  className="block"
                  label="For an eligible assessment, UHQS equals the weighted sum of modules A, B, C, E, and F"
                  tex={`\\mathrm{UHQS} = w_{A}S_{A}+w_{B}S_{B}+w_{C}S_{C}+w_{E}S_{E}+w_{F}S_{F}`}
                />
                <KatexMath
                  display
                  className="block uhqs-katex-danger"
                  label="UHQS is null unless the assessment is complete and critical controls pass"
                  tex={`\\mathrm{UHQS}=\\varnothing\\quad\\text{if INCOMPLETE or GATE\\_FAILED}`}
                />
              </div>

              <div className="mt-6 space-y-4 text-muted-foreground leading-relaxed">
                <p>
                  In plain terms: every applicable mandatory check must run and produce evidence.
                  An untested, errored, omitted, or unevidenced mandatory check makes the result{" "}
                  <span className="text-foreground font-medium">Ungraded</span>, not a low letter grade.
                </p>
                <p>
                  Module D is a critical-control eligibility gate. Every applicable containment control
                  must pass with evidence. A critical failure cannot be averaged away; the separate
                  defense-in-depth diagnostic remains visible but is not weighted into UHQS.
                </p>
                <p>
                  Different honeypot types also care about different strengths (an industrial PLC
                  decoy is not graded exactly like a fake SSH shell). Report outcome, scoring model,
                  assurance level, UHQS, and grade separately. None is certification or deployment
                  authorization.
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
