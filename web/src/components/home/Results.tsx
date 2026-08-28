import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Terminal,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  List,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  Search,
} from "lucide-react";
import { fadeUpVariant, staggerContainer } from "./motion";
import { LAB_RESULTS, PROTOCOL_FILTERS } from "../../data/labResults";

export const Results = () => {
  const [protocolFilter, setProtocolFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"cards" | "list">("cards");
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<"uhqsQuick" | "uhqsFull" | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const pageSize = viewMode === "cards" ? 3 : 12;

  const filteredLabs = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    let base =
      protocolFilter === "all"
        ? LAB_RESULTS
        : LAB_RESULTS.filter((lab) => lab.protocol === protocolFilter);
    if (q) {
      base = base.filter(
        (lab) =>
          lab.name.toLowerCase().includes(q) ||
          lab.repo.toLowerCase().includes(q) ||
          lab.protocolLabel.toLowerCase().includes(q) ||
          lab.classLabel.toLowerCase().includes(q),
      );
    }
    if (!sortKey) return base;
    return [...base].sort((a, b) => {
      const av = a[sortKey] ?? -1;
      const bv = b[sortKey] ?? -1;
      return sortDir === "asc" ? av - bv : bv - av;
    });
  }, [protocolFilter, searchQuery, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(filteredLabs.length / pageSize));
  const safePage = Math.min(page, pageCount - 1);
  const pageLabs = filteredLabs.slice(safePage * pageSize, safePage * pageSize + pageSize);

  useEffect(() => {
    if (page !== safePage) setPage(safePage);
  }, [page, safePage]);

  const setFilter = (id: string) => {
    setProtocolFilter(id);
    setPage(0);
  };

  const toggleSort = (key: "uhqsQuick" | "uhqsFull") => {
    if (sortKey !== key) {
      setSortKey(key);
      setSortDir("desc");
    } else if (sortDir === "desc") {
      setSortDir("asc");
    } else {
      setSortKey(null);
      setSortDir("desc");
    }
  };

  const SortIcon = ({ column }: { column: "uhqsQuick" | "uhqsFull" }) => {
    if (sortKey !== column) {
      return <ArrowUpDown className="w-3 h-3 opacity-50" aria-hidden />;
    }
    return sortDir === "desc" ? (
      <ArrowDown className="w-3 h-3 text-primary" aria-hidden />
    ) : (
      <ArrowUp className="w-3 h-3 text-primary" aria-hidden />
    );
  };

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

        <motion.div variants={fadeUpVariant} className="mb-6 flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-3">
              Filter by protocol
            </div>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Filter honeypot results by protocol">
              {PROTOCOL_FILTERS.map((opt) => {
                const active = protocolFilter === opt.id;
                const count =
                  opt.id === "all"
                    ? LAB_RESULTS.length
                    : LAB_RESULTS.filter((l) => l.protocol === opt.id).length;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setFilter(opt.id)}
                    aria-pressed={active}
                    className={
                      active
                        ? "font-mono text-xs px-3 py-1.5 border border-primary bg-primary/15 text-primary"
                        : "font-mono text-xs px-3 py-1.5 border border-border text-secondary-foreground hover:border-primary/50 hover:text-primary transition-colors"
                    }
                  >
                    {opt.label}
                    <span className="ml-1.5 text-muted-foreground">({count})</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-3">
              View
            </div>
            <div className="inline-flex border border-border" role="group" aria-label="Results view mode">
              <button
                type="button"
                onClick={() => {
                  setViewMode("cards");
                  setPage(0);
                }}
                aria-pressed={viewMode === "cards"}
                className={
                  viewMode === "cards"
                    ? "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 bg-primary/15 text-primary border-r border-border"
                    : "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 text-secondary-foreground hover:text-primary border-r border-border"
                }
              >
                <LayoutGrid className="w-3.5 h-3.5" aria-hidden />
                Cards
              </button>
              <button
                type="button"
                onClick={() => {
                  setViewMode("list");
                  setPage(0);
                }}
                aria-pressed={viewMode === "list"}
                className={
                  viewMode === "list"
                    ? "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 bg-primary/15 text-primary"
                    : "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 text-secondary-foreground hover:text-primary"
                }
              >
                <List className="w-3.5 h-3.5" aria-hidden />
                List
              </button>
            </div>
          </div>
          </div>

          <label className="relative block max-w-md">
            <span className="sr-only">Search results by name or repository</span>
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" aria-hidden />
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(0);
              }}
              placeholder="Search by name or repo…"
              className="w-full bg-background border border-border pl-9 pr-3 py-2 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
            />
          </label>
        </motion.div>

        {filteredLabs.length === 0 && (
          <p className="font-mono text-sm text-muted-foreground mb-10">
            No published labs for this protocol filter{searchQuery.trim() ? " / search" : ""}.
          </p>
        )}

        {viewMode === "cards" && filteredLabs.length > 0 && (
          <div className="mb-12">
            <div className="flex items-stretch gap-2 sm:gap-3">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, Math.min(p, pageCount - 1) - 1))}
                disabled={safePage <= 0}
                aria-label="Previous three results"
                className="shrink-0 self-center w-10 h-10 flex items-center justify-center border border-border text-secondary-foreground hover:border-primary/50 hover:text-primary disabled:opacity-25 disabled:hover:border-border disabled:hover:text-secondary-foreground transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 flex-1 min-w-0">
                {pageLabs.map((lab) => (
                  <div
                    key={lab.name}
                    className="bg-card border border-border p-6 terminal-card flex flex-col"
                  >
                    <div className="font-mono text-xs text-primary uppercase tracking-wider mb-2">{lab.classLabel}</div>
                    <h3 className="text-xl font-bold mb-1">
                      <a href={lab.hub} className="hover:text-primary transition-colors">{lab.name}</a>
                    </h3>
                    <a
                      href={lab.repo}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-mono text-xs text-secondary-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
                    >
                      Original project <ArrowRight className="w-3 h-3" />
                    </a>
                    <div className="font-mono text-[10px] text-muted-foreground mb-4 mt-1">
                      GitHub last push {lab.repoUpdated}
                    </div>

                    <div className="grid grid-cols-2 gap-3 mb-6 font-mono text-sm">
                      <div className="border border-border/60 p-3">
                        <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Quick</div>
                        <div className="text-primary font-bold text-lg">{lab.uhqsQuick == null ? "—" : lab.uhqsQuick.toFixed(2)}</div>
                        <div className="text-xs text-secondary-foreground">Grade {lab.gradeQuick}</div>
                      </div>
                      <div className="border border-primary/30 bg-primary/5 p-3">
                        <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Full</div>
                        <div className="text-primary font-bold text-lg">{lab.uhqsFull == null ? "—" : lab.uhqsFull.toFixed(2)}</div>
                        <div className="text-xs text-secondary-foreground">Grade {lab.gradeFull}</div>
                      </div>
                    </div>

                    <div className="mt-auto space-y-4 font-mono text-xs">
                      <div>
                        <div className="text-muted-foreground uppercase tracking-wider text-[10px] mb-2">Guides</div>
                        <div className="flex flex-col gap-1.5">
                          <a href={lab.tutorial} className="text-primary hover:underline flex items-center gap-1">
                            Tutorial <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.methodology} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Methodology <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.hub} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Report hub <ArrowRight className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground uppercase tracking-wider text-[10px] mb-2">Runs & scorecards</div>
                        <div className="flex flex-col gap-1.5">
                          <a href={lab.scorecard} className="text-primary hover:underline flex items-center gap-1">
                            Published scorecard page <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.full} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Full run artifacts <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.fullCard} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Full SCORECARD.txt <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.quick} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Quick run artifacts <ArrowRight className="w-3 h-3" />
                          </a>
                          <a href={lab.quickCard} className="text-secondary-foreground hover:text-primary transition-colors flex items-center gap-1">
                            Quick SCORECARD.txt <ArrowRight className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                type="button"
                onClick={() => setPage((p) => Math.min(pageCount - 1, Math.min(p, pageCount - 1) + 1))}
                disabled={safePage >= pageCount - 1}
                aria-label="Next three results"
                className="shrink-0 self-center w-10 h-10 flex items-center justify-center border border-border text-secondary-foreground hover:border-primary/50 hover:text-primary disabled:opacity-25 disabled:hover:border-border disabled:hover:text-secondary-foreground transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {pageCount > 1 && (
              <div className="mt-4 flex items-center justify-center gap-2 font-mono text-[10px] text-muted-foreground tracking-wide">
                <span>
                  {safePage + 1} / {pageCount}
                </span>
                <span className="text-border">·</span>
                <span>
                  {safePage * pageSize + 1}–{Math.min(filteredLabs.length, (safePage + 1) * pageSize)} of {filteredLabs.length}
                </span>
              </div>
            )}
          </div>
        )}

        {viewMode === "list" && filteredLabs.length > 0 && (
          <div className="mb-12">
          <div className="overflow-x-auto border border-border">
            <table className="w-full text-left text-sm font-mono">
              <thead>
                <tr className="border-b border-border bg-card text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="py-3 px-4 font-normal">Target</th>
                  <th className="py-3 px-4 font-normal">Protocol</th>
                  <th className="py-3 px-4 font-normal">Project</th>
                  <th className="py-3 px-4 font-normal">Tutorial</th>
                  <th className="py-3 px-4 font-normal">
                    <button
                      type="button"
                      onClick={() => toggleSort("uhqsQuick")}
                      className="inline-flex items-center gap-1.5 hover:text-primary transition-colors"
                      aria-label={`Sort by Quick UHQS${sortKey === "uhqsQuick" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                    >
                      Quick
                      <SortIcon column="uhqsQuick" />
                    </button>
                  </th>
                  <th className="py-3 px-4 font-normal">
                    <button
                      type="button"
                      onClick={() => toggleSort("uhqsFull")}
                      className="inline-flex items-center gap-1.5 hover:text-primary transition-colors"
                      aria-label={`Sort by Full UHQS${sortKey === "uhqsFull" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                    >
                      Full
                      <SortIcon column="uhqsFull" />
                    </button>
                  </th>
                  <th className="py-3 px-4 font-normal">Scorecard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {pageLabs.map((lab) => (
                  <tr key={`row-${lab.name}`} className="hover:bg-card/80">
                    <td className="py-3 px-4 text-foreground font-semibold">
                      <a href={lab.hub} className="hover:text-primary">{lab.name}</a>
                      <div className="text-[10px] text-muted-foreground font-normal mt-0.5">{lab.classLabel}</div>
                    </td>
                    <td className="py-3 px-4 text-secondary-foreground">{lab.protocolLabel}</td>
                    <td className="py-3 px-4">
                      <a href={lab.repo} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">GitHub</a>
                      <div className="text-[10px] text-muted-foreground mt-0.5">Updated {lab.repoUpdated}</div>
                    </td>
                    <td className="py-3 px-4">
                      <a href={lab.tutorial} className="text-primary hover:underline">Open</a>
                    </td>
                    <td className="py-3 px-4">
                      <a href={lab.quickCard} className="text-secondary-foreground hover:text-primary">{lab.uhqsQuick == null ? "—" : `${lab.uhqsQuick.toFixed(2)} / ${lab.gradeQuick}`}</a>
                    </td>
                    <td className="py-3 px-4">
                      <a href={lab.fullCard} className="text-secondary-foreground hover:text-primary">{lab.uhqsFull == null ? "—" : `${lab.uhqsFull.toFixed(2)} / ${lab.gradeFull}`}</a>
                    </td>
                    <td className="py-3 px-4">
                      <a href={lab.scorecard} className="text-primary hover:underline">Page</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {pageCount > 1 && (
            <div className="mt-4 flex items-center justify-center gap-3 font-mono text-[10px] text-muted-foreground tracking-wide">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={safePage <= 0}
                className="px-2 py-1 border border-border hover:border-primary/50 disabled:opacity-25"
                aria-label="Previous list page"
              >
                Prev
              </button>
              <span>
                {safePage + 1} / {pageCount} · {safePage * pageSize + 1}–{Math.min(filteredLabs.length, (safePage + 1) * pageSize)} of {filteredLabs.length}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
                disabled={safePage >= pageCount - 1}
                className="px-2 py-1 border border-border hover:border-primary/50 disabled:opacity-25"
                aria-label="Next list page"
              >
                Next
              </button>
            </div>
          )}
          </div>
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

// Section: MCP for AI hosts (AEO / agent tooling)
