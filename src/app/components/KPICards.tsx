import { Zap, Battery, Server, Activity } from 'lucide-react';

interface KPICardsProps {
  totalCapacity: number;
  totalActivePower: number;
  fleetAvgSoc: number;
  sitesOnline: number;
  totalSites: number;
}

export function KPICards({
  totalCapacity,
  totalActivePower,
  fleetAvgSoc,
  sitesOnline,
  totalSites,
}: KPICardsProps) {
  const kpiData = [
    {
      icon: Zap,
      label: 'Total Fleet Capacity',
      value: totalCapacity.toFixed(1),
      unit: 'kW',
      color: 'status-info',
    },
    {
      icon: Activity,
      label: 'Total Active Power',
      value: totalActivePower.toFixed(1),
      unit: 'kW',
      color: 'status-healthy',
    },
    {
      icon: Battery,
      label: 'Fleet Average SoC',
      value: fleetAvgSoc.toFixed(0),
      unit: '%',
      color: fleetAvgSoc >= 50 ? 'status-healthy' : fleetAvgSoc >= 20 ? 'status-warning' : 'status-critical',
    },
    {
      icon: Server,
      label: 'Sites Online',
      value: `${sitesOnline}/${totalSites}`,
      unit: '',
      color: sitesOnline === totalSites ? 'status-healthy' : 'status-warning',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiData.map((kpi, index) => (
        <div key={index} className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-start justify-between mb-3">
            <kpi.icon className={`w-6 h-6 text-${kpi.color}`} />
          </div>
          <div className="space-y-1">
            <div className="flex items-baseline gap-2">
              <span className={`text-3xl font-mono font-semibold text-${kpi.color}`}>
                {kpi.value}
              </span>
              {kpi.unit && <span className="text-sm text-muted-foreground">{kpi.unit}</span>}
            </div>
            <div className="text-sm text-muted-foreground">{kpi.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
