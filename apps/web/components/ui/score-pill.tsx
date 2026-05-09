import { cn } from "@/lib/utils";

type ScorePillProps = {
  score: number | null;
  label?: string;
  className?: string;
};

export function ScorePill({ className, label = "Score", score }: ScorePillProps) {
  const scoreLabel = score === null ? "Unknown" : `${Math.round(score)}`;

  return (
    <div
      className={cn(
        "inline-flex min-w-20 flex-col items-center rounded-md border border-primary/20 bg-primary/10 px-3 py-2 text-primary",
        className,
      )}
    >
      <span className="text-xs font-semibold uppercase tracking-[0.12em]">{label}</span>
      <span className="text-2xl font-bold leading-7 tracking-normal">{scoreLabel}</span>
    </div>
  );
}
