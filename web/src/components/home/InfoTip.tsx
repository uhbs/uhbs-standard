import { Info } from "lucide-react";
import { cn } from "@/lib/utils";

/** Hover/focus info chip — plain-language tip for non-experts. */
export function InfoTip({
  label,
  children,
  className,
}: {
  label: string;
  children: string;
  className?: string;
}) {
  return (
    <span className={cn("relative inline-flex align-middle", className)}>
      <button
        type="button"
        className="peer inline-flex size-4 shrink-0 items-center justify-center rounded-full border border-border bg-secondary-background text-muted-foreground hover:bg-background hover:text-black focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-1"
        aria-label={`What is ${label}?`}
      >
        <Info className="size-2.5" aria-hidden />
      </button>
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-[calc(100%+6px)] left-1/2 z-50 w-56 -translate-x-1/2 rounded-base border-2 border-border bg-secondary-background px-2.5 py-2 text-left font-sans text-[11px] font-base leading-snug text-foreground shadow-shadow opacity-0 transition-opacity peer-hover:opacity-100 peer-focus-visible:opacity-100"
      >
        {children}
      </span>
    </span>
  );
}
