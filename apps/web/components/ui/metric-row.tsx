type MetricRowProps = {
  label: string;
  value: string;
  detail?: string;
};

export function MetricRow({ detail, label, value }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between gap-4 text-sm">
      <div>
        <p className="font-medium text-foreground">{label}</p>
        {detail ? <p className="mt-0.5 text-xs text-muted-foreground">{detail}</p> : null}
      </div>
      <p className="shrink-0 font-semibold text-foreground">{value}</p>
    </div>
  );
}
