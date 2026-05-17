import { ChevronLeft, Battery, Zap, TrendingUp, AlertTriangle } from 'lucide-react';
import { WidgetCard } from '../WidgetCard';

interface BatteryDetailViewProps {
  onBack: () => void;
}

export function BatteryDetailView({ onBack }: BatteryDetailViewProps) {
  const batteries = [
    { id: '1', site: 'Westlands BP', capacity: 200, soc: 72, voltage: 385, current: 45, temp: 28, cycles: 342, health: 98 },
    { id: '2', site: 'Upper Hill', capacity: 400, soc: 65, voltage: 388, current: 82, temp: 31, cycles: 298, health: 99 },
    { id: '3', site: 'Karen BP', capacity: 120, soc: 41, voltage: 375, current: 28, temp: 35, cycles: 456, health: 94 },
    { id: '4', site: 'Mombasa Rd', capacity: 1000, soc: 78, voltage: 392, current: 125, temp: 29, cycles: 221, health: 99 },
  ];

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
          <h2 className="text-xl font-semibold">Battery Energy Storage Systems</h2>
          <p className="text-sm text-muted-foreground">Real-time BESS monitoring and diagnostics</p>
        </div>
      </div>

      {/* Battery Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {batteries.map((battery) => {
          const isLowSoc = battery.soc < 45;
          const isHighTemp = battery.temp > 32;

          return (
            <WidgetCard key={battery.id} title={battery.site} icon={Battery}>
              <div className="space-y-4">
                {/* SoC Display */}
                <div className="text-center pb-4 border-b border-border">
                  <div className="text-5xl font-semibold mb-2" style={{
                    color: isLowSoc ? 'var(--color-status-warning)' : 'var(--color-status-healthy)'
                  }}>
                    {battery.soc}%
                  </div>
                  <div className="text-sm text-muted-foreground">State of Charge</div>
                  <div className="mt-2 h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all"
                      style={{
                        width: `${battery.soc}%`,
                        backgroundColor: isLowSoc ? 'var(--color-status-warning)' : 'var(--color-status-healthy)'
                      }}
                    />
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Capacity</div>
                    <div className="font-semibold">{battery.capacity} kWh</div>
                  </div>
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Voltage</div>
                    <div className="font-semibold">{battery.voltage} V</div>
                  </div>
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Current</div>
                    <div className="font-semibold">{battery.current} A</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Temperature</div>
                    <div className={`font-semibold ${isHighTemp ? 'text-status-warning' : ''}`}>
                      {battery.temp}°C
                    </div>
                  </div>
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Cycles</div>
                    <div className="font-semibold">{battery.cycles}</div>
                  </div>
                  <div className="bg-secondary/30 rounded-lg p-2">
                    <div className="text-muted-foreground text-xs mb-1">Health</div>
                    <div className="font-semibold text-status-healthy">{battery.health}%</div>
                  </div>
                </div>

                {/* Warnings */}
                {(isLowSoc || isHighTemp) && (
                  <div className="space-y-2">
                    {isLowSoc && (
                      <div className="flex items-center gap-2 p-2 bg-status-warning/10 border border-status-warning/30 rounded text-xs text-status-warning">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Low SoC - Schedule charging</span>
                      </div>
                    )}
                    {isHighTemp && (
                      <div className="flex items-center gap-2 p-2 bg-status-warning/10 border border-status-warning/30 rounded text-xs text-status-warning">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Elevated temperature detected</span>
                      </div>
                    )}
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
