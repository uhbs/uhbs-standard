import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { mkdocsUrl } from "@/lib/urls";
import { fadeUpVariant, staggerContainer } from "./motion";

const ITEMS = [
  {
    title: "Five-dimension matrix",
    benefit: "Offline equal-weight experimental composite with missing-dimension honesty and leave-one-out sensitivity.",
    overview: mkdocsUrl("experimental/"),
    beginner: mkdocsUrl("experimental/tutorial-matrix-beginner/"),
    advanced: mkdocsUrl("experimental/tutorial-matrix-advanced/"),
    cli: mkdocsUrl("experimental/cli-matrix/"),
    hint: "uhbs matrix example beginner",
  },
  {
    title: "GenAI / MCP bench",
    benefit: "Replay-buffer CLR/SCR/TTFT metrics; tarpit-aware timing; live probes stay lab-gated and off MCP.",
    overview: mkdocsUrl("experimental/"),
    beginner: mkdocsUrl("experimental/tutorial-genai-beginner/"),
    advanced: mkdocsUrl("experimental/tutorial-genai-advanced/"),
    cli: mkdocsUrl("experimental/cli-genai-bench/"),
    hint: "uhbs genai-bench example beginner",
  },
  {
    title: "Host provenance",
    benefit: "Collector-neutral validate/summarize/attach with rate limits before hashing; CAP_BPF not required for offline paths.",
    overview: mkdocsUrl("experimental/"),
    beginner: mkdocsUrl("experimental/tutorial-provenance-beginner/"),
    advanced: mkdocsUrl("experimental/"),
    cli: mkdocsUrl("experimental/cli-provenance/"),
    hint: "uhbs provenance example beginner",
  },
] as const;

export const LatestChanges = () => {
  return (
    <section id="latest" className="py-24 border-t-2 border-border bg-secondary-background">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="max-w-3xl mb-10">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-7 h-7 text-main" aria-hidden />
            <h2 className="text-3xl font-heading">Latest changes</h2>
          </div>
          <p className="text-muted-foreground text-lg font-base leading-relaxed">
            Opt-in experimental benchmark surfaces. Labeled{" "}
            <span className="text-foreground font-mono text-sm">Experimental / does not change UHQS</span>
            . They do not alter v5 assessment eligibility, module weights, or letter bands.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {ITEMS.map((item) => (
            <motion.article
              key={item.title}
              variants={fadeUpVariant}
              className="border-2 border-border bg-page p-5 shadow-[2px_2px_0_0_#000]"
            >
              <div className="font-mono text-[10px] uppercase tracking-wider text-black bg-main inline-block px-2 py-0.5 border-2 border-border mb-3">
                Experimental · UHQS unchanged
              </div>
              <h3 className="font-heading text-xl mb-2">{item.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed mb-4">{item.benefit}</p>
              <ul className="font-mono text-xs space-y-1.5 text-muted-foreground mb-4">
                <li>
                  <a className="hover:text-foreground underline-offset-2 hover:underline" href={item.overview}>
                    Overview
                  </a>
                </li>
                <li>
                  <a className="hover:text-foreground underline-offset-2 hover:underline" href={item.beginner}>
                    Beginner tutorial
                  </a>
                </li>
                <li>
                  <a className="hover:text-foreground underline-offset-2 hover:underline" href={item.advanced}>
                    Advanced / index
                  </a>
                </li>
                <li>
                  <a className="hover:text-foreground underline-offset-2 hover:underline" href={item.cli}>
                    CLI reference
                  </a>
                </li>
                <li className="text-foreground/80">
                  <code>{item.hint}</code>
                </li>
              </ul>
            </motion.article>
          ))}
        </div>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4">
          <ButtonLink href={mkdocsUrl("experimental/")}>
            Experimental docs <ArrowRight />
          </ButtonLink>
          <ButtonLink href="https://github.com/uhbs/uhbs-standard/blob/main/CHANGELOG.md">
            CHANGELOG
          </ButtonLink>
        </motion.div>
      </motion.div>
    </section>
  );
};
