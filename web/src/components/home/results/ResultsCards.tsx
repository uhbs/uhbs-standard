import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LabResult } from "../../../data/labResults";
import { GradeBadge } from "../GradeBadge";

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
        <Button
          type="button"
          size="icon"
          variant="neutral"
          onClick={() => onPage((p) => Math.max(0, Math.min(p, pageCount - 1) - 1))}
          disabled={safePage <= 0}
          aria-label="Previous three results"
          className="shrink-0 self-center"
        >
          <ChevronLeft />
        </Button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 flex-1 min-w-0">
          {pageLabs.map((lab) => (
            <Card key={lab.name} className="h-full">
              <CardHeader>
                <div className="font-mono text-xs text-main uppercase tracking-wider mb-1">
                  {lab.classLabel}
                </div>
                <CardTitle className="text-xl">
                  <a href={lab.hub} className="hover:text-main transition-colors">
                    {lab.name}
                  </a>
                </CardTitle>
                <a
                  href={lab.repo}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-mono text-xs text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
                >
                  Original project <ArrowRight className="w-3 h-3" aria-hidden />
                </a>
                <div className="font-mono text-[10px] text-muted-foreground mt-1">
                  GitHub last push {lab.repoUpdated}
                </div>
              </CardHeader>
              <CardContent className="flex flex-col flex-1">
                <div className="grid grid-cols-2 gap-3 mb-6 font-mono text-sm">
                  <div className="border border-border p-3 rounded-base bg-page">
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                      Quick
                    </div>
                    <div className="text-main font-heading text-lg">
                      {lab.uhqsQuick == null ? "—" : lab.uhqsQuick.toFixed(2)}
                    </div>
                    <div className="mt-1">
                      <GradeBadge grade={lab.gradeQuick} />
                    </div>
                  </div>
                  <div className="border-2 border-border p-3 rounded-base bg-background">
                    <div className="text-[10px] uppercase tracking-wider text-black mb-1">Full</div>
                    <div className="text-black font-heading text-lg">
                      {lab.uhqsFull == null ? "—" : lab.uhqsFull.toFixed(2)}
                    </div>
                    <div className="mt-1">
                      <GradeBadge grade={lab.gradeFull} />
                    </div>
                  </div>
                </div>

                <div className="mt-auto space-y-4 font-mono text-xs">
                  <div>
                    <div className="text-muted-foreground uppercase tracking-wider text-[10px] mb-2">
                      Guides
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <a href={lab.tutorial} className="text-main hover:underline flex items-center gap-1">
                        Tutorial <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.methodology}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Methodology <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.hub}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Report hub <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground uppercase tracking-wider text-[10px] mb-2">
                      Runs & scorecards
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <a href={lab.scorecard} className="text-main hover:underline flex items-center gap-1">
                        Published scorecard page <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.full}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Full run artifacts <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.fullCard}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Full SCORECARD.txt <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.quick}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Quick run artifacts <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                      <a
                        href={lab.quickCard}
                        className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                      >
                        Quick SCORECARD.txt <ArrowRight className="w-3 h-3" aria-hidden />
                      </a>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Button
          type="button"
          size="icon"
          variant="neutral"
          onClick={() => onPage((p) => Math.min(pageCount - 1, Math.min(p, pageCount - 1) + 1))}
          disabled={safePage >= pageCount - 1}
          aria-label="Next three results"
          className="shrink-0 self-center"
        >
          <ChevronRight />
        </Button>
      </div>

      {pageCount > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2 font-mono text-[10px] text-muted-foreground tracking-wide">
          <span>
            {safePage + 1} / {pageCount}
          </span>
          <span>·</span>
          <span>
            {safePage * pageSize + 1}–{Math.min(filteredCount, (safePage + 1) * pageSize)} of{" "}
            {filteredCount}
          </span>
        </div>
      )}
    </div>
  );
}
