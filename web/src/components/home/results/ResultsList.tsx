import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { LabResult } from "../../../data/labResults";
import { GradeBadge } from "../GradeBadge";
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
    <ArrowDown className="w-3 h-3 text-main" aria-hidden />
  ) : (
    <ArrowUp className="w-3 h-3 text-main" aria-hidden />
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
      <div className="overflow-x-auto border-2 border-border rounded-base shadow-shadow bg-secondary-background">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-border bg-page hover:bg-page">
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Target
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Protocol
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Project
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Tutorial
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                <button
                  type="button"
                  onClick={() => onToggleSort("uhqsQuick")}
                  className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"
                  aria-label={`Sort by Quick UHQS${sortKey === "uhqsQuick" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                >
                  Quick
                  <SortIcon column="uhqsQuick" sortKey={sortKey} sortDir={sortDir} />
                </button>
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                <button
                  type="button"
                  onClick={() => onToggleSort("uhqsFull")}
                  className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"
                  aria-label={`Sort by Full UHQS${sortKey === "uhqsFull" ? `, currently ${sortDir === "desc" ? "high to low" : "low to high"}` : ""}`}
                >
                  Full
                  <SortIcon column="uhqsFull" sortKey={sortKey} sortDir={sortDir} />
                </button>
              </TableHead>
              <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Scorecard
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pageLabs.map((lab) => (
              <TableRow key={`row-${lab.name}`} className="odd:bg-slate-50/80 border-border/60">
                <TableCell className="font-semibold">
                  <a href={lab.hub} className="hover:text-main">
                    {lab.name}
                  </a>
                  <div className="text-[10px] text-muted-foreground font-normal mt-0.5">
                    {lab.classLabel}
                  </div>
                </TableCell>
                <TableCell className="text-muted-foreground font-mono text-xs">
                  {lab.protocolLabel}
                </TableCell>
                <TableCell>
                  <a
                    href={lab.repo}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-main hover:underline font-mono text-xs"
                  >
                    GitHub
                  </a>
                  <div className="text-[10px] text-muted-foreground mt-0.5">
                    Updated {lab.repoUpdated}
                  </div>
                </TableCell>
                <TableCell>
                  <a href={lab.tutorial} className="text-main hover:underline font-mono text-xs">
                    Open
                  </a>
                </TableCell>
                <TableCell>
                  <a href={lab.quickCard} className="inline-flex flex-col gap-1 hover:opacity-90">
                    <span className="font-mono text-xs">
                      {lab.uhqsQuick == null ? "—" : lab.uhqsQuick.toFixed(2)}
                    </span>
                    <GradeBadge grade={lab.gradeQuick} />
                  </a>
                </TableCell>
                <TableCell>
                  <a href={lab.fullCard} className="inline-flex flex-col gap-1 hover:opacity-90">
                    <span className="font-mono text-xs">
                      {lab.uhqsFull == null ? "—" : lab.uhqsFull.toFixed(2)}
                    </span>
                    <GradeBadge grade={lab.gradeFull} />
                  </a>
                </TableCell>
                <TableCell>
                  <a href={lab.scorecard} className="text-main hover:underline font-mono text-xs">
                    Page
                  </a>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {pageCount > 1 && (
        <div className="mt-4 flex items-center justify-center gap-3 font-mono text-[10px] text-muted-foreground tracking-wide">
          <Button
            type="button"
            size="xs"
            variant="neutral"
            onClick={() => onPage((p) => Math.max(0, p - 1))}
            disabled={safePage <= 0}
            aria-label="Previous list page"
          >
            Prev
          </Button>
          <span>
            {safePage + 1} / {pageCount} · {safePage * pageSize + 1}–
            {Math.min(filteredCount, (safePage + 1) * pageSize)} of {filteredCount}
          </span>
          <Button
            type="button"
            size="xs"
            variant="neutral"
            onClick={() => onPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={safePage >= pageCount - 1}
            aria-label="Next list page"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
