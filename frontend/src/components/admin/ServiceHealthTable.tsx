import type { ServiceHealth } from "@/api/admin";

interface ServiceHealthTableProps {
  health: Record<string, ServiceHealth>;
}

export function ServiceHealthTable({ health }: ServiceHealthTableProps) {
  const services = Object.entries(health);

  return (
    <div className="overflow-x-auto rounded-md border">
      <table className="w-full text-sm" data-testid="service-health-table">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="px-4 py-3 text-left font-medium">Service</th>
            <th className="px-4 py-3 text-left font-medium">Status</th>
            <th className="px-4 py-3 text-left font-medium">Last Check</th>
          </tr>
        </thead>
        <tbody>
          {services.map(([name, info]) => (
            <tr key={name} className="border-b last:border-b-0">
              <td className="px-4 py-3 capitalize">{name}</td>
              <td className="px-4 py-3">
                <span className="flex items-center gap-2">
                  <span
                    className={`inline-block h-2.5 w-2.5 rounded-full ${
                      info.status === "healthy" ? "bg-green-500" : "bg-red-500"
                    }`}
                    data-testid={`health-dot-${name}`}
                  />
                  {info.status}
                </span>
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {info.last_check ? new Date(info.last_check).toLocaleString() : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
