import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fadeUpVariant, staggerContainer } from "./motion";

export const LatestChanges = () => {
  const items = [
    {
      title: "MQTT honeypot scoring",
      body: "MQTT 3.1.1 fidelity probes now grade Modules A/B (FSM, CONNACK, PING, unsubscribe, pub/sub echo) so shallow always-CONNACK decoys no longer look perfect.",
      badge: "4.6.0",
      links: [
        { href: "mkdocs/scorecards/mqtt-decoy-b/", label: "MQTT decoy B scorecard" },
        { href: "mkdocs/scorecards/mqtt-decoy-a/", label: "MQTT decoy A scorecard" },
        { href: "mkdocs/plugin-authoring/", label: "Plugin authoring" },
      ],
    },
    {
      title: "Five-dimension matrix",
      body: "Equal-weight experimental scores with explicit missing dimensions and sensitivity analysis.",
      badge: "Experimental",
      links: [
        { href: "mkdocs/experimental/", label: "Overview" },
        { href: "mkdocs/experimental/tutorial-matrix-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-matrix/", label: "CLI" },
      ],
    },
    {
      title: "GenAI / MCP bench",
      body: "Deterministic replay metrics (CLR, SCR, TTFT). Tarpit-aware timing; not exposed via uhbs-mcp.",
      badge: "Experimental",
      links: [
        { href: "mkdocs/experimental/tutorial-genai-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-genai-bench/", label: "CLI" },
        { href: "mkdocs/architecture/experimental-benchmarks/", label: "Architecture" },
      ],
    },
    {
      title: "Host provenance",
      body: "Collector-neutral summaries with rate limits before hashing. Optional signed envelopes later.",
      badge: "Experimental",
      links: [
        { href: "mkdocs/experimental/tutorial-provenance-beginner/", label: "Beginner tutorial" },
        { href: "mkdocs/experimental/cli-provenance/", label: "CLI" },
      ],
    },
  ];

  return (
    <section id="latest" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-4 flex items-center gap-3">
          <div className="h-1 w-8 bg-main border border-border" />
          <Badge variant="mint" className="uppercase tracking-widest font-mono text-[10px]">
            Latest changes
          </Badge>
        </motion.div>
        <motion.div variants={fadeUpVariant} className="mb-10 max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-heading mb-4">UHBS 4.6.0</h2>
          <p className="text-muted-foreground leading-relaxed mb-3">
            MQTT decoys now participate in UHQS via Modules A/B fidelity probes.{" "}
            <span className="text-foreground font-medium">
              UHQS formula, weights, and Safety Gate δ<sub>C</sub> are unchanged
            </span>
            .
          </p>
          <p className="text-sm font-mono text-muted-foreground">
            Details:{" "}
            <a
              href="https://github.com/uhbs/uhbs-standard/blob/main/CHANGELOG.md"
              className="text-main hover:underline"
            >
              CHANGELOG
            </a>
            {" · "}
            <a href="mkdocs/scorecards/" className="text-main hover:underline">
              Scorecards
            </a>
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
          {items.map((item) => (
            <motion.div key={item.title} variants={fadeUpVariant}>
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-center gap-2 flex-wrap">
                    <CardTitle className="text-lg">{item.title}</CardTitle>
                    <Badge variant={item.badge === "Experimental" ? "warning" : "mint"}>
                      {item.badge}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-4">{item.body}</p>
                  <div className="flex flex-wrap gap-3 font-mono text-xs">
                    {item.links.map((link) => (
                      <a
                        key={link.href}
                        href={link.href}
                        className="inline-flex items-center gap-1 text-main hover:underline"
                      >
                        {link.label} <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};
