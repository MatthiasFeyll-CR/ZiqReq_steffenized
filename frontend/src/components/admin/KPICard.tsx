interface KPICardProps {
  label: string;
  value: string | number;
}

export function KPICard({ label, value }: KPICardProps) {
  return (
    <div className="rounded-md border bg-card p-4" data-testid={`kpi-${label.toLowerCase().replace(/\s+/g, "-")}`}>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold text-foreground">{value}</p>
    </div>
  );
}
