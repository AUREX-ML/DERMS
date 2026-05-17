import { MapPin, Zap, Battery, TrendingUp, AlertCircle, ChevronLeft } from 'lucide-react';
import { WidgetCard } from '../WidgetCard';

interface Site {
  id: string;
  name: string;
  location: string;
  status: 'online' | 'partial' | 'offline';
  pvCapacity: number;
  bessCapacity: number;
  currentSoc: number;
  currentPower: number;
  todayEnergy: number;
  lastUpdate: string;
}

interface SitesDetailViewProps {
  onBack: () => void;
}

export function SitesDetailView({ onBack }: SitesDetailViewProps) {
  const sites: Site[] = [
    {
      id: '1',
      name: 'Westlands BP',
      location: 'Westlands, Nairobi',
      status: 'online',
      pvCapacity: 150,
      bessCapacity: 200,
      currentSoc: 72,
      currentPower: 128,
      todayEnergy: 845,
      lastUpdate: '2 mins ago',
    },
    {
      id: '2',
      name: 'Upper Hill',
      location: 'Upper Hill, Nairobi',
      status: 'online',
      pvCapacity: 300,
      bessCapacity: 400,
      currentSoc: 65,
      currentPower: 245,
      todayEnergy: 1650,
      lastUpdate: '1 min ago',
    },
    {
      id: '3',
      name: 'Karen BP',
      location: 'Karen, Nairobi',
      status: 'partial',
      pvCapacity: 100,
      bessCapacity: 120,
      currentSoc: 41,
      currentPower: 45,
      todayEnergy: 320,
      lastUpdate: '5 mins ago',
    },
    {
      id: '4',
      name: 'Mombasa Rd',
      location: 'Mombasa Road, Nairobi',
      status: 'online',
      pvCapacity: 500,
      bessCapacity: 1000,
      currentSoc: 78,
      currentPower: 432,
      todayEnergy: 3200,
      lastUpdate: '1 min ago',
    },
  ];

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

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={onBack}
          className="w-10 h-10 bg-secondary rounded-lg flex items-center justify-center hover:bg-secondary/80 transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-xl font-semibold">Site Management</h2>
          <p className="text-sm text-muted-foreground">Monitor and manage all VPP sites</p>
        </div>
      </div>

      {/* Sites Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {sites.map((site) => {
          const statusColor = getStatusColor(site.status);
          const isLowSoc = site.currentSoc < 45;

          return (
            <WidgetCard key={site.id} title={site.name} icon={MapPin}>
              <div className="space-y-4">
                {/* Status Bar */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full bg-${statusColor}`}
                      style={{
                        boxShadow: `0 0 8px var(--color-${statusColor})`,
                      }}
                    />
                    <span className={`text-sm font-medium text-${statusColor} capitalize`}>
                      {site.status}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">{site.lastUpdate}</span>
                </div>

                {/* Location */}
                <div className="text-sm text-muted-foreground">{site.location}</div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-secondary/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-4 h-4 text-status-warning" />
                      <span className="text-xs text-muted-foreground">Current Power</span>
                    </div>
                    <div className="text-2xl font-semibold">{site.currentPower}</div>
                    <div className="text-xs text-muted-foreground">kW</div>
                  </div>

                  <div className="bg-secondary/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Battery
                        className={`w-4 h-4 ${isLowSoc ? 'text-status-warning' : 'text-status-healthy'}`}
                      />
                      <span className="text-xs text-muted-foreground">Battery SoC</span>
                    </div>
                    <div className={`text-2xl font-semibold ${isLowSoc ? 'text-status-warning' : ''}`}>
                      {site.currentSoc}
                    </div>
                    <div className="text-xs text-muted-foreground">%</div>
                  </div>
                </div>

                {/* Capacity Info */}
                <div className="grid grid-cols-3 gap-3 pt-3 border-t border-border text-xs">
                  <div>
                    <div className="text-muted-foreground mb-1">PV Capacity</div>
                    <div className="font-semibold">{site.pvCapacity} kW</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">BESS Capacity</div>
                    <div className="font-semibold">{site.bessCapacity} kWh</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground mb-1">Today's Energy</div>
                    <div className="font-semibold text-status-healthy">{site.todayEnergy} kWh</div>
                  </div>
                </div>

                {/* Warnings */}
                {isLowSoc && (
                  <div className="flex items-center gap-2 p-2 bg-status-warning/10 border border-status-warning/30 rounded text-xs text-status-warning">
                    <AlertCircle className="w-4 h-4" />
                    <span>Low battery - Consider charging</span>
                  </div>
                )}
              </div>
            </WidgetCard>
          );
        })}
      </div>
    </div>
  );
}
