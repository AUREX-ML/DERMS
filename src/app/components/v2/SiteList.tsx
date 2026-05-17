import { MapPin, Zap, Battery } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

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
    <WidgetCard title="Site Status Map" icon={MapPin}>
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
              <div className="flex items-start gap-3 flex-1">
                <div className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                  style={{
                    backgroundColor: site.status === 'online' ? 'rgba(16, 185, 129, 0.1)' :
                                   site.status === 'partial' ? 'rgba(245, 158, 11, 0.1)' :
                                   'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${site.status === 'online' ? 'rgba(16, 185, 129, 0.3)' :
                                       site.status === 'partial' ? 'rgba(245, 158, 11, 0.3)' :
                                       'rgba(239, 68, 68, 0.3)'}`
                  }}>
                  {getStatusIcon(site.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold text-sm">{site.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded text-${statusColor} capitalize bg-${statusColor}/10`}>
                      {site.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div>
                      <div className="text-muted-foreground mb-0.5">PV</div>
                      <div className="font-semibold flex items-center gap-1">
                        <Zap className="w-3 h-3 text-status-warning" />
                        {site.pvCapacity}kW
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-0.5">BESS</div>
                      <div className="font-semibold flex items-center gap-1">
                        <Battery className="w-3 h-3 text-primary" />
                        {site.bessCapacity}kWh
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-0.5">SoC</div>
                      <div className={`font-semibold ${isLowSoc ? 'text-status-warning' : 'text-status-healthy'}`}>
                        {site.currentSoc}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </WidgetCard>
  );
}
