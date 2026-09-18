import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { fadeUpVariant, staggerContainer } from "./motion";
import { ResultsCards } from "./results/ResultsCards";
import { ResultsList } from "./results/ResultsList";
import { ResultsToolbar } from "./results/ResultsToolbar";
import { useResultsQuery } from "./results/useResultsQuery";
import { mkdocsUrl } from "@/lib/urls";

export const Results = () => {
  const q = useResultsQuery();

  return (
    <section id="results" className="py-24 border-t-2 border-border bg-page">
      <motion.div
        className="container mx-auto px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={staggerContainer}
      >
        <motion.div variants={fadeUpVariant} className="mb-8">
          <h2 className="text-3xl md:text-4xl font-heading mb-4 flex items-center gap-3">
            <Terminal className="text-main w-8 h-8" aria-hidden />
            Results
          </h2>
          <p className="text-muted-foreground max-w-3xl">
            Published UHBS-Lab Docker runs — tutorials, quick + full scorecards, and methodology.
            Evaluation proof only (not endorsements). Prefer{" "}
            <span className="text-foreground font-mono text-sm">full/</span> for claim-grade numbers.
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
            No published labs for this protocol filter
            {q.searchQuery.trim() ? " / search" : ""}.
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

        <motion.div variants={fadeUpVariant} className="flex flex-wrap gap-4">
          <ButtonLink variant="neutral" href={mkdocsUrl("conformance/reports/")}>
            All lab reports <ArrowRight />
          </ButtonLink>
          <ButtonLink variant="neutral" href={mkdocsUrl("scorecards/")}>
            All scorecards <ArrowRight />
          </ButtonLink>
          <ButtonLink variant="neutral" href={mkdocsUrl("tooling/cli/")}>
            Docker / CLI guide <ArrowRight />
          </ButtonLink>
          <ButtonLink variant="neutral" href={mkdocsUrl("tooling/mcp/")}>
            MCP for AI hosts <ArrowRight />
          </ButtonLink>
        </motion.div>
      </motion.div>
    </section>
  );
};
