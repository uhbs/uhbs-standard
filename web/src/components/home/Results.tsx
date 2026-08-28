import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";
import { ResultsCards } from "./results/ResultsCards";
import { ResultsList } from "./results/ResultsList";
import { ResultsToolbar } from "./results/ResultsToolbar";
import { useResultsQuery } from "./results/useResultsQuery";

export const Results = () => {
  const q = useResultsQuery();

  return (
    <section id="results" className="py-24 border-t border-border/50">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-8">
          <h2 className="text-3xl md:text-4xl font-bold font-sans mb-4 flex items-center gap-3">
            <Terminal className="text-primary w-8 h-8" />
            Results
          </h2>
          <p className="text-secondary-foreground max-w-3xl">
            Published UHBS-Lab Docker runs — tutorials, quick + full scorecards, and methodology.
            Evaluation proof only (not endorsements). Prefer <span className="text-foreground font-mono text-sm">full/</span> for claim-grade numbers.
          </p>
        </motion.div>

        <motion.div variants={fadeUpVariant}>
          <ResultsToolbar
            protocolFilter={q.protocolFilter}
            searchQuery={q.searchQuery}
            viewMode={q.viewMode}
            onFilter={q.setFilter}
            onSearch={(value) => {
              q.setSearchQuery(value);
              q.setPage(0);
            }}
            onViewMode={(mode) => {
              q.setViewMode(mode);
              q.setPage(0);
            }}
          />
        </motion.div>

        {q.filteredLabs.length === 0 && (
          <p className="font-mono text-sm text-muted-foreground mb-10">
            No published labs for this protocol filter{q.searchQuery.trim() ? " / search" : ""}.
          </p>
        )}

        {q.viewMode === "cards" && q.filteredLabs.length > 0 && (
          <ResultsCards
            pageLabs={q.pageLabs}
            filteredCount={q.filteredLabs.length}
            pageCount={q.pageCount}
            safePage={q.safePage}
            pageSize={q.pageSize}
            onPage={q.setPage}
          />
        )}

        {q.viewMode === "list" && q.filteredLabs.length > 0 && (
          <ResultsList
            pageLabs={q.pageLabs}
            filteredCount={q.filteredLabs.length}
            pageCount={q.pageCount}
            safePage={q.safePage}
            pageSize={q.pageSize}
            sortKey={q.sortKey}
            sortDir={q.sortDir}
            onToggleSort={q.toggleSort}
            onPage={q.setPage}
          />
        )}

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4 font-mono text-sm">
          <a href="mkdocs/conformance/reports/" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50 transition-colors">
            All lab reports <ArrowRight className="w-4 h-4 text-primary" />
          </a>
          <a href="mkdocs/scorecards/" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50 transition-colors">
            All scorecards <ArrowRight className="w-4 h-4 text-primary" />
          </a>
          <a href="mkdocs/tooling/cli/" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50 transition-colors">
            Docker / CLI guide <ArrowRight className="w-4 h-4 text-primary" />
          </a>
          <a href="mkdocs/tooling/mcp/" className="inline-flex items-center gap-2 border border-border px-4 py-2 hover:border-primary/50 transition-colors">
            MCP for AI hosts <ArrowRight className="w-4 h-4 text-primary" />
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
};
