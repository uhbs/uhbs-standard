import { motion } from "framer-motion";
import {
  CheckCircle,
  ArrowRight,
  Layers,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const AdvancedEvidenceProfile = () => {
  const values = [
    "Compare lab decoy behavior with a matched lab reference.",
    "Measure engagement and distinguishability with uncertainty.",
    "Analyze local evidence offline—never launch attacks.",
  ];

  const credits = [
    {
      cite: "Zhu (2019)",
      title: "Game Theory for Cyber Deception: A Tutorial",
      href: "https://doi.org/10.1145/3314058.3314067",
      note: "Signaling / dynamic-game vocabulary",
    },
    {
      cite: "Collins, Xu & Brown (2024)",
      title: "Game-Theoretic Cybersecurity…",
      href: "https://arxiv.org/abs/2401.13815",
      note: "Uncertainty & practicality discipline (preprint)",
    },
    {
      cite: "Ersok et al. (2022)",
      title: "Measuring Honeypots based on CTF game",
      href: "https://doi.org/10.1109/ICCC202255925.2022.9922853",
      note: "Controlled CTF / log validation patterns",
    },
    {
      cite: "Li et al. (2020)",
      title: "Anti-Honeypot Enabled Optimal Attack Strategy…",
      href: "https://doi.org/10.1109/OJCS.2020.3030825",
      note: "Attacker threat-model tiers (not a defender grade)",
    },
  ];

  return (
    <section id="advanced-evidence" className="py-24 border-t border-border/50 bg-[#0a0e1a]">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-4 flex items-center gap-3">
          <div className="h-px w-8 bg-primary"></div>
          <span className="font-mono text-primary uppercase tracking-widest text-xs">Optional Lab Evidence Layer</span>
        </motion.div>
        <motion.div variants={fadeUpVariant} className="mb-8">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4 flex items-center gap-3">
            <Layers className="text-primary w-8 h-8" />
            Advanced Evidence Profile (optional)
          </h2>
          <p className="text-secondary-foreground max-w-3xl mb-4">
            UHQS remains the normative implementation-quality and safety grade from{" "}
            <span className="text-foreground font-medium">laboratory evaluation</span>. The optional Advanced Evidence
            Profile adds controlled lab evidence about adversarial perception, engagement, distinguishability, and cost
            under declared experimental conditions.{" "}
            <span className="text-foreground font-medium">AEP does not change UHQS.</span>
          </p>
          <p className="text-sm text-warning/90 max-w-3xl border border-warning/30 bg-warning/5 px-4 py-3 font-mono leading-relaxed">
            Lab / sandbox only — not real-world production testing. UHBS and AEP must not be aimed at production systems,
            customer environments, or unauthorized targets. A UHQS &gt; 80 “production baseline” is an internal gate{" "}
            <em>after</em> lab grading, not permission to test in the wild.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-10">
          <motion.div variants={fadeUpVariant} className="lg:col-span-5 border border-border bg-card p-6">
            <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-wider mb-3">Core UHBS (lab)</h3>
            <p className="text-sm text-secondary-foreground leading-relaxed mb-4">
              Modules A–F, profile-adaptive weights, Safety Gate δ<sub>C</sub>, and a reproducible UHQS scorecard from
              isolated lab runs.
            </p>
            <ul className="text-sm font-mono text-foreground space-y-2">
              <li>UHQS 0–100 + letter grade</li>
              <li>Normative for UHBS-Core / UHBS-Lab</li>
              <li>Lab release / conformance gate</li>
            </ul>
          </motion.div>
          <motion.div variants={fadeUpVariant} className="lg:col-span-2 flex items-center justify-center">
            <ArrowRight className="w-8 h-8 text-primary rotate-90 lg:rotate-0" aria-hidden="true" />
          </motion.div>
          <motion.div variants={fadeUpVariant} className="lg:col-span-5 border border-primary/30 bg-primary/5 p-6">
            <h3 className="font-mono text-xs text-primary uppercase tracking-wider mb-3">Optional AEP (lab)</h3>
            <p className="text-sm text-secondary-foreground leading-relaxed mb-4">
              Controlled lab decoy vs matched lab reference (+ evaluator control). Status:{" "}
              <span className="font-mono text-foreground">valid | inconclusive | control_failed</span> — not grades.
            </p>
            <ul className="text-sm font-mono text-foreground space-y-2">
              <li>VoD · FSV · DTDR · EER</li>
              <li>Uncertainty + sample / censoring counts</li>
              <li>Separate ADVANCED-EVIDENCE addendum</li>
            </ul>
          </motion.div>
        </div>

        <motion.div variants={fadeUpVariant} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          {values.map((text) => (
            <div key={text} className="border border-border/50 bg-card/50 p-5 flex gap-3 items-start">
              <CheckCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" aria-hidden="true" />
              <p className="text-sm text-secondary-foreground leading-relaxed">{text}</p>
            </div>
          ))}
        </motion.div>

        <motion.div variants={fadeUpVariant} className="mb-10 border border-border/50 bg-card/40 p-6">
          <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-wider mb-3">
            Academic foundations (credited)
          </h3>
          <p className="text-sm text-secondary-foreground mb-4 max-w-3xl leading-relaxed">
            AEP’s experimental vocabulary and measurement discipline draw on published research. We credit these authors
            and venues; citation does <span className="text-foreground">not</span> mean they endorse UHBS or that UHBS
            implements their full models.
          </p>
          <ul className="space-y-3">
            {credits.map((c) => (
              <li key={c.href} className="text-sm leading-relaxed">
                <a
                  href={c.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
                >
                  {c.cite}
                </a>
                <span className="text-secondary-foreground">
                  {" "}
                  — {c.title} · {c.note}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs font-mono text-muted-foreground">
            Full ledger:{" "}
            <a href="mkdocs/advanced-evidence/research-foundations/" className="text-primary hover:underline">
              Research foundations &amp; credits
            </a>
          </p>
        </motion.div>

        <motion.div
          variants={fadeUpVariant}
          id="aep-slm-alpha"
          className="mb-10 border border-border/60 bg-card/50 p-6"
        >
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <span className="font-mono text-[10px] uppercase tracking-widest px-2 py-1 border border-warning/40 text-warning/90">
              Alpha · off by default
            </span>
            <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              Optional AEP SLM evaluator
            </h3>
          </div>
          <p className="text-sm text-secondary-foreground max-w-3xl leading-relaxed mb-4">
            An opt-in helper for labs that want a small / local language model (or a deterministic{" "}
            <span className="font-mono text-foreground">mock</span>) to draft{" "}
            <span className="text-foreground font-medium">AEP trial JSONL</span> for offline{" "}
            <span className="font-mono text-foreground">uhbs aep analyze</span>. Installing UHBS does{" "}
            <span className="text-foreground font-medium">not</span> turn it on — you must edit a local{" "}
            <span className="font-mono text-foreground">aep-slm.yaml</span> (enable flag, unlock phrase, and
            attestations). It never changes UHQS, never launches probes, and is not exposed over the AI-host MCP
            server.
          </p>
          <ul className="text-sm font-mono text-foreground space-y-2 mb-5">
            <li>
              <span className="text-primary">pip install &apos;uhbs[aep-slm]&apos;</span> →{" "}
              <span className="text-secondary-foreground">uhbs aep slm init|validate|status|generate</span>
            </li>
            <li>
              Providers: <span className="text-secondary-foreground">mock</span> (offline) ·{" "}
              <span className="text-secondary-foreground">recorded</span> · loopback-only{" "}
              <span className="text-secondary-foreground">openai_compatible</span>
            </li>
            <li className="text-secondary-foreground">
              Purpose: experiment dry-runs / local replay — not certification, not production testing
            </li>
          </ul>
          <div className="flex flex-wrap gap-3">
            <a
              href="mkdocs/advanced-evidence/slm-alpha/"
              className="inline-flex items-center gap-2 px-4 py-2 border border-primary/40 bg-primary/10 text-primary font-mono text-xs hover:bg-primary/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              How to use SLM (alpha) <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
            </a>
            <a
              href="mkdocs/advanced-evidence/cli/#aep-slm"
              className="inline-flex items-center gap-2 px-4 py-2 border border-border text-secondary-foreground font-mono text-xs hover:border-primary/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              CLI reference
            </a>
          </div>
        </motion.div>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4">
          <a
            href="mkdocs/advanced-evidence/"
            className="inline-flex items-center gap-2 px-5 py-3 border border-primary/40 bg-primary/10 text-primary font-mono text-sm hover:bg-primary/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            AEP overview <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </a>
          <a
            href="mkdocs/advanced-evidence/slm-alpha/"
            className="inline-flex items-center gap-2 px-5 py-3 border border-border text-secondary-foreground font-mono text-sm hover:border-primary/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            SLM evaluator (alpha)
          </a>
          <a
            href="mkdocs/advanced-evidence/research-foundations/"
            className="inline-flex items-center gap-2 px-5 py-3 border border-border text-secondary-foreground font-mono text-sm hover:border-primary/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            Research credits
          </a>
          <a
            href="mkdocs/advanced-evidence/runbook/"
            className="inline-flex items-center gap-2 px-5 py-3 border border-border text-secondary-foreground font-mono text-sm hover:border-primary/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            Runbook
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Section 6: Audit Workflow
