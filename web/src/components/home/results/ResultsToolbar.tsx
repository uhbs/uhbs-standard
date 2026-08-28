import { LayoutGrid, List, Search } from "lucide-react";
import { LAB_RESULTS, PROTOCOL_FILTERS } from "../../../data/labResults";
import type { ViewMode } from "./useResultsQuery";

type Props = {
  protocolFilter: string;
  searchQuery: string;
  viewMode: ViewMode;
  onFilter: (id: string) => void;
  onSearch: (value: string) => void;
  onViewMode: (mode: ViewMode) => void;
};

export function ResultsToolbar({
  protocolFilter,
  searchQuery,
  viewMode,
  onFilter,
  onSearch,
  onViewMode,
}: Props) {
  return (
    <div className="mb-6 flex flex-col gap-4">
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
                  onClick={() => onFilter(opt.id)}
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
              onClick={() => onViewMode("cards")}
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
              onClick={() => onViewMode("list")}
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
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search by name or repo…"
          className="w-full bg-background border border-border pl-9 pr-3 py-2 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
        />
      </label>
    </div>
  );
}
