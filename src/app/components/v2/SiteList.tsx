import { MapPin, Zap, Battery } from 'lucide-react';

interface Site {
  id: string;
  name: string;
  location: string;
  status: 'online' | 'partial' | 'offline';
  pvCapacity: number;
  bessCapacity: number;
  currentSoc: number;
}

interface SiteListProps {
  sites: Site[];
}

export function SiteList({ sites }: SiteListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'status-healthy';
      case 'partial':
        return 'status-warning';
      case 'offline':
        return 'status-critical';
      default:
        return 'muted';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return '🟢';
      case 'partial':
        return '🟡';
      case 'offline':
        return '🔴';
      default:
        return '⚪';
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-muted-foreground" />
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Nairobi Map — Site Status</h3>
      </div>

      <div className="space-y-3">
        {sites.map((site) => {
          const statusColor = getStatusColor(site.status);
          const isLowSoc = site.currentSoc < 45;

          return (
            <div
              key={site.id}
              className={`flex items-center justify-between p-3 rounded-lg border ${
                site.status === 'online'
                  ? 'bg-status-healthy/5 border-status-healthy/30'
                  : site.status === 'partial'
                    ? 'bg-status-warning/5 border-status-warning/30'
                    : 'bg-status-critical/5 border-status-critical/30'
              }`}
            >
              <div className="flex items-center gap-3 flex-1">
                <div className="text-xl">{getStatusIcon(site.status)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono font-semibold">{site.name}</span>
                    <span className={`text-xs font-mono text-${statusColor} capitalize`}>{site.status}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      <span className="font-mono">{site.pvCapacity}kW PV</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Battery className="w-3 h-3" />
                      <span className="font-mono">{site.bessCapacity}kWh BESS</span>
                    </div>
                    <div className={`flex items-center gap-1 ${isLowSoc ? 'text-status-warning' : ''}`}>
                      <span className="font-mono font-semibold">{site.currentSoc}%</span>
                      {isLowSoc && <span className="text-status-warning">(low!)</span>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
