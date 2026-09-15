import { LayoutGrid, List, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
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
          <div
            className="flex flex-wrap gap-2"
            role="group"
            aria-label="Filter honeypot results by protocol"
          >
            {PROTOCOL_FILTERS.map((opt) => {
              const active = protocolFilter === opt.id;
              const count =
                opt.id === "all"
                  ? LAB_RESULTS.length
                  : LAB_RESULTS.filter((l) => l.protocol === opt.id).length;
              return (
                <Button
                  key={opt.id}
                  type="button"
                  size="xs"
                  variant={active ? "default" : "neutral"}
                  aria-pressed={active}
                  onClick={() => onFilter(opt.id)}
                  className={cn(active && "bg-background text-black")}
                >
                  {opt.label}
                  <span className="opacity-70">({count})</span>
                </Button>
              );
            })}
          </div>
        </div>

        <div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-3">
            View
          </div>
          <div
            className="inline-flex border-2 border-border shadow-shadow overflow-hidden rounded-base"
            role="group"
            aria-label="Results view mode"
          >
            <button
              type="button"
              onClick={() => onViewMode("cards")}
              aria-pressed={viewMode === "cards"}
              className={cn(
                "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 border-r-2 border-border transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2",
                viewMode === "cards"
                  ? "bg-background text-black"
                  : "bg-secondary-background text-muted-foreground hover:text-foreground",
              )}
            >
              <LayoutGrid className="w-3.5 h-3.5" aria-hidden />
              Cards
            </button>
            <button
              type="button"
              onClick={() => onViewMode("list")}
              aria-pressed={viewMode === "list"}
              className={cn(
                "inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2",
                viewMode === "list"
                  ? "bg-background text-black"
                  : "bg-secondary-background text-muted-foreground hover:text-foreground",
              )}
            >
              <List className="w-3.5 h-3.5" aria-hidden />
              List
            </button>
          </div>
        </div>
      </div>

      <label className="relative block max-w-md">
        <span className="sr-only">Search results by name or repository</span>
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground z-10"
          aria-hidden
        />
        <Input
          type="search"
          value={searchQuery}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search by name or repo…"
          className="pl-9 font-mono text-xs"
        />
      </label>
    </div>
  );
}
