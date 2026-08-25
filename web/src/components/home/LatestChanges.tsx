import { motion } from "framer-motion";
import {
  ArrowRight,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const LatestChanges = () => {
  const items = [
    {
      title: "Five-dimension matrix",
      body: "Equal-weight experimental scores with explicit missing dimensions and sensitivity analysis.",
      links: [
        { href: "mkdocs/experimental/", label: "Overview" },
        { href: "mkdocs/experimental/tutorial-matrix-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-matrix/", label: "CLI" },
      ],
    },
    {
      title: "GenAI / MCP bench",
      body: "Deterministic replay metrics (CLR, SCR, TTFT). Tarpit-aware timing; not exposed via uhbs-mcp.",
      links: [
        { href: "mkdocs/experimental/tutorial-genai-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-genai-bench/", label: "CLI" },
        { href: "mkdocs/architecture/experimental-benchmarks/", label: "Architecture" },
      ],
    },
    {
      title: "Host provenance",
      body: "Collector-neutral summaries with rate limits before hashing. Optional signed envelopes later.",
      links: [
        { href: "mkdocs/experimental/tutorial-provenance-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-provenance/", label: "CLI" },
      ],
    },
    {
      title: "OT / ICS verification",
      body: "Hardened Modbus/S7 timeouts and expanding BACnet/MQTT/CoAP plugins (lab).",
      links: [
        { href: "mkdocs/experimental/", label: "Experimental hub" },
        { href: "mkdocs/plugin-authoring/", label: "Plugin authoring" },
        { href: "mkdocs/conformance/reports/conpot/TUTORIAL/", label: "Conpot tutorial" },
      ],
    },
  ];

  return (
    <section id="latest" className="py-24 border-t border-border/50 bg-[#0a0e1a]">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-4 flex items-center gap-3">
          <div className="h-px w-8 bg-primary"></div>
          <span className="font-mono text-primary uppercase tracking-widest text-xs">
            Latest changes
          </span>
        </motion.div>
        <motion.div variants={fadeUpVariant} className="mb-10 max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4">
            Experimental additions
          </h2>
          <p className="text-secondary-foreground leading-relaxed mb-3">
            New opt-in surfaces for research and high-assurance labs.{" "}
            <span className="text-foreground font-medium">They do not change UHQS</span>,
            weights, or the Safety Gate δ<sub>C</sub>.
          </p>
          <p className="text-sm font-mono text-muted-foreground">
            Details:{" "}
            <a
              href="https://github.com/uhbs/uhbs-standard/blob/main/CHANGELOG.md"
              className="text-primary hover:underline"
            >
              CHANGELOG
            </a>
            {" · "}
            <a href="mkdocs/rfcs/0002-experimental-benchmark-extensions/" className="text-primary hover:underline">
              RFC 0002
            </a>
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
          {items.map((item) => (
            <motion.div
              key={item.title}
              variants={fadeUpVariant}
              className="border border-border/60 bg-card/40 p-6"
            >
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-sans text-lg font-semibold">{item.title}</h3>
                <span className="text-[10px] uppercase tracking-wider font-mono text-warning border border-warning/40 px-1.5 py-0.5">
                  Experimental
                </span>
              </div>
              <p className="text-sm text-secondary-foreground leading-relaxed mb-4">{item.body}</p>
              <div className="flex flex-wrap gap-3 font-mono text-xs">
                {item.links.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    className="inline-flex items-center gap-1 text-primary hover:underline"
                  >
                    {link.label} <ArrowRight className="w-3 h-3" aria-hidden="true" />
                  </a>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

// Footer
