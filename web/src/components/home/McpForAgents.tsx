import { motion } from "framer-motion";
import {
  Terminal,
  ArrowRight,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";

export const McpForAgents = () => {
  return (
    <section id="mcp" className="py-24 border-t border-border/50 bg-[#0f1629]/40">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="max-w-3xl mb-10">
          <div className="flex items-center gap-3 mb-4">
            <Terminal className="w-7 h-7 text-primary" />
            <h2 className="text-3xl font-bold font-sans">MCP for AI hosts</h2>
          </div>
          <p className="text-secondary-foreground text-lg font-light leading-relaxed">
            Optional local stdio server so Cursor, Claude Desktop, VS Code, and other
            MCP clients can validate scorecards and recompute UHQS without inventing math.
            Live Docker lab probes stay on the CLI.
          </p>
        </motion.div>

        <motion.div
          variants={fadeUpVariant}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10 font-mono text-sm"
        >
          {[
            { title: "Validate", body: "scorecard · profile · evidence schemas + UHQS integrity" },
            { title: "Score", body: "compute_uhqs / δ_C from uhqs_math — same as uhbs score" },
            { title: "Discover", body: "fixtures, lab report hubs, scoring-formula resource" },
          ].map((card) => (
            <div key={card.title} className="border border-border/60 bg-card/50 p-5">
              <div className="text-primary mb-2">{card.title}</div>
              <div className="text-muted-foreground text-xs leading-relaxed">{card.body}</div>
            </div>
          ))}
        </motion.div>

        <motion.pre
          variants={fadeUpVariant}
          className="bg-background border border-border/60 p-5 overflow-x-auto text-xs font-mono text-secondary-foreground mb-8"
        >{`pip install -e ".[mcp]"
# mcpServers.uhbs → python -m uhbs_mcp  (set UHBS_ROOT to checkout)`}</motion.pre>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4 font-mono text-sm">
          <a href="mkdocs/tooling/mcp/" className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 hover:opacity-90">
            MCP install guide <ArrowRight className="w-4 h-4" />
          </a>
          <a href="https://github.com/uhbs/uhbs-standard/blob/main/server.json" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50">
            server.json
          </a>
          <a href="llms.txt" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50">
            llms.txt
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Section: Latest experimental changes
