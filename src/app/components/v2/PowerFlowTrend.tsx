import { Activity } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

interface PowerFlowTrendProps {
  solarData: number[];
  bessData: number[];
  gridData: number[];
}

export function PowerFlowTrend({ solarData, bessData, gridData }: PowerFlowTrendProps) {
  const maxValue = Math.max(...solarData, ...bessData, ...gridData);

  return (
    <WidgetCard title="Power Flow (24h)" icon={Activity}>
      <div className="space-y-4">
        {/* Visual Bar Chart */}
        <div className="flex items-end gap-0.5 h-24">
          {solarData.map((value, i) => {
            const solarHeight = (value / maxValue) * 100;
            const bessHeight = (bessData[i] / maxValue) * 100;
            const gridHeight = (gridData[i] / maxValue) * 100;

            return (
              <div key={`bar-${i}`} className="flex-1 flex flex-col justify-end gap-0.5">
                {value > 0 && (
                  <div
                    className="bg-status-warning/70 rounded-t-sm"
                    style={{ height: `${solarHeight}%` }}
                    title={`Solar: ${value}kW`}
                  ></div>
                )}
                {bessData[i] > 0 && (
                  <div
                    className="bg-status-info/70"
                    style={{ height: `${bessHeight}%` }}
                    title={`BESS: ${bessData[i]}kW`}
                  ></div>
                )}
                {gridData[i] > 0 && (
                  <div
                    className="bg-muted/70"
                    style={{ height: `${gridHeight}%` }}
                    title={`Grid: ${gridData[i]}kW`}
                  ></div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-status-warning/70 rounded"></div>
            <span className="text-muted-foreground font-mono">Solar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-status-info/70 rounded"></div>
            <span className="text-muted-foreground font-mono">BESS</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-muted/70 rounded"></div>
            <span className="text-muted-foreground font-mono">Grid Import</span>
          </div>
        </div>
      </div>
    </WidgetCard>
  );
}
