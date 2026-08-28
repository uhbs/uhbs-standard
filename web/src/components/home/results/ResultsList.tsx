import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import type { LabResult } from "../../../data/labResults";
import type { SortDir, SortKey } from "./useResultsQuery";

type Props = {
  pageLabs: LabResult[];
  filteredCount: number;
  pageCount: number;
  safePage: number;
  pageSize: number;
  sortKey: SortKey | null;
  sortDir: SortDir;
  onToggleSort: (key: SortKey) => void;
  onPage: (updater: (p: number) => number) => void;
};

function SortIcon({
  column,
  sortKey,
  sortDir,
}: {
  column: SortKey;
  sortKey: SortKey | null;
  sortDir: SortDir;
}) {
  if (sortKey !== column) {
    return <ArrowUpDown className="w-3 h-3 opacity-50" aria-hidden />;
  }
  return sortDir === "desc" ? (
    <ArrowDown className="w-3 h-3 text-primary" aria-hidden />
  ) : (
    <ArrowUp className="w-3 h-3 text-primary" aria-hidden />
  );
}

export function ResultsList({
  pageLabs,
  filteredCount,
  pageCount,
  safePage,
  pageSize,
  sortKey,
  sortDir,
  onToggleSort,
  onPage,
}: Props) {
  return (
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
                  onClick={() => onToggleSort("uhqsQuick")}
                  className="inline-flex items-center gap-1.5 hover:text-primary transition-colors"
                  aria-label={`Sort by Quick UHQS${sortKey === "uhqsQuick" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                >
                  Quick
                  <SortIcon column="uhqsQuick" sortKey={sortKey} sortDir={sortDir} />
                </button>
              </th>
              <th className="py-3 px-4 font-normal">
                <button
                  type="button"
                  onClick={() => onToggleSort("uhqsFull")}
                  className="inline-flex items-center gap-1.5 hover:text-primary transition-colors"
                  aria-label={`Sort by Full UHQS${sortKey === "uhqsFull" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                >
                  Full
                  <SortIcon column="uhqsFull" sortKey={sortKey} sortDir={sortDir} />
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
            onClick={() => onPage((p) => Math.max(0, p - 1))}
            disabled={safePage <= 0}
            className="px-2 py-1 border border-border hover:border-primary/50 disabled:opacity-25"
            aria-label="Previous list page"
          >
            Prev
          </button>
          <span>
            {safePage + 1} / {pageCount} · {safePage * pageSize + 1}–{Math.min(filteredCount, (safePage + 1) * pageSize)} of {filteredCount}
          </span>
          <button
            type="button"
            onClick={() => onPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={safePage >= pageCount - 1}
            className="px-2 py-1 border border-border hover:border-primary/50 disabled:opacity-25"
            aria-label="Next list page"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
