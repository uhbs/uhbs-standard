import { motion } from "framer-motion";
import { Terminal, ArrowRight } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { mkdocsUrl, siteUrl } from "@/lib/urls";
import { fadeUpVariant, staggerContainer } from "./motion";

export const McpForAgents = () => {
  return (
    <section id="mcp" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="max-w-3xl mb-10">
          <div className="flex items-center gap-3 mb-4">
            <Terminal className="w-7 h-7 text-main" aria-hidden />
            <h2 className="text-3xl font-heading">MCP for AI hosts</h2>
          </div>
          <p className="text-muted-foreground text-lg font-base leading-relaxed">
            Optional local stdio server so Cursor, Claude Desktop, VS Code, and other MCP clients can
            validate scorecards and recompute UHQS without inventing math. Live Docker lab probes stay
            on the CLI.
          </p>
        </motion.div>

        <motion.div
          variants={fadeUpVariant}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10 font-mono text-sm"
        >
          {[
            { title: "Validate", body: "scorecard · profile · evidence schemas + UHQS integrity" },
            { title: "Score", body: "compute_uhqs eligibility + weighted sum from the shared uhqs_math source" },
            { title: "Discover", body: "fixtures, lab report hubs, scoring-formula resource" },
          ].map((card) => (
            <Card key={card.title} size="sm">
              <CardContent>
                <div className="text-black bg-background inline-block px-2 py-0.5 border-2 border-border mb-2 text-xs uppercase tracking-wider">
                  {card.title}
                </div>
                <div className="text-muted-foreground text-xs leading-relaxed">{card.body}</div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        <motion.pre
          variants={fadeUpVariant}
          className="bg-slate-50 border-2 border-border p-5 overflow-x-auto text-xs font-mono text-foreground mb-8 shadow-[2px_2px_0_0_#000]"
        >{`pip install -e ".[mcp]"
# mcpServers.uhbs → python -m uhbs_mcp  (set UHBS_ROOT to checkout)`}</motion.pre>

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4">
          <ButtonLink href={mkdocsUrl("tooling/mcp/")}>
            MCP install guide <ArrowRight />
          </ButtonLink>
          <ButtonLink
            variant="neutral"
            href="https://github.com/uhbs/uhbs-standard/blob/main/server.json"
          >
            server.json
          </ButtonLink>
          <ButtonLink variant="neutral" href={siteUrl("llms.txt")}>
            llms.txt
          </ButtonLink>
        </motion.div>
      </motion.div>
    </section>
  );
};
