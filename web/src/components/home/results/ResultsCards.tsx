import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { LabResult } from "../../../data/labResults";

type Props = {
  pageLabs: LabResult[];
  filteredCount: number;
  pageCount: number;
  safePage: number;
  pageSize: number;
  onPage: (updater: (p: number) => number) => void;
};

export function ResultsCards({
  pageLabs,
  filteredCount,
  pageCount,
  safePage,
  pageSize,
  onPage,
}: Props) {
  return (
    <div className="mb-12">
      <div className="flex items-stretch gap-2 sm:gap-3">
        <button
          type="button"
          onClick={() => onPage((p) => Math.max(0, Math.min(p, pageCount - 1) - 1))}
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
          onClick={() => onPage((p) => Math.min(pageCount - 1, Math.min(p, pageCount - 1) + 1))}
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
            {safePage * pageSize + 1}–{Math.min(filteredCount, (safePage + 1) * pageSize)} of {filteredCount}
          </span>
        </div>
      )}
    </div>
  );
}
