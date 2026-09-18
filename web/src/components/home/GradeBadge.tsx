import { CircleCheck, Minus, TriangleAlert, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Grade = string | null | undefined;

function glyphFor(grade: Grade) {
  if (!grade || grade === "—") {
    return { Icon: Minus, variant: "neutral" as const };
  }
  const g = grade.toUpperCase();
  if (g === "A" || g === "B") {
    return { Icon: CircleCheck, variant: "success" as const };
  }
  if (g === "C" || g === "D") {
    return { Icon: TriangleAlert, variant: "warning" as const };
  }
  return { Icon: XCircle, variant: "danger" as const };
}

export function GradeBadge({
  grade,
  className,
}: {
  grade: Grade;
  className?: string;
}) {
  const label = !grade || grade === "—" ? "—" : grade;
  const { Icon, variant } = glyphFor(grade);
  return (
    <Badge variant={variant} className={cn("font-mono", className)}>
      <Icon aria-hidden className="size-3" />
      {label}
    </Badge>
  );
}
