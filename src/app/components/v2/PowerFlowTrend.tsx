import { Activity } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

interface PowerFlowTrendProps {
  solarData: number[];
  bessData: number[];
  gridData: number[];
}

export function PowerFlowTrend({ solarData, bessData, gridData }: PowerFlowTrendProps) {
  const maxValue = Math.max(...solarData, ...bessData, ...gridData, 100); // Ensure minimum scale

  // Current values (latest in the arrays)
  const currentSolar = solarData[solarData.length - 1] || 0;
  const currentBess = bessData[bessData.length - 1] || 0;
  const currentGrid = gridData[gridData.length - 1] || 0;

  return (
    <WidgetCard title="Power Flow (24h)" icon={Activity}>
      <div className="space-y-4">
        {/* Current Values */}
        <div className="grid grid-cols-3 gap-3 pb-3 border-b border-border">
          <div>
            <div className="text-xs text-muted-foreground mb-1">Solar</div>
            <div className="text-xl font-semibold text-status-warning">{currentSolar.toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">kW</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">BESS</div>
            <div className="text-xl font-semibold text-status-info">{currentBess.toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">kW</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">Grid</div>
            <div className="text-xl font-semibold text-muted-foreground">{currentGrid.toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">kW</div>
          </div>
        </div>

        {/* Visual Bar Chart */}
        <div className="flex items-end gap-0.5 h-32 bg-secondary/20 rounded p-2">
          {solarData.map((value, i) => {
            const solarHeight = Math.max((value / maxValue) * 100, value > 0 ? 3 : 0);
            const bessHeight = Math.max((bessData[i] / maxValue) * 100, bessData[i] > 0 ? 3 : 0);
            const gridHeight = Math.max((gridData[i] / maxValue) * 100, gridData[i] > 0 ? 3 : 0);

            return (
              <div key={`bar-${i}`} className="flex-1 flex flex-col-reverse gap-0.5">
                {value > 0 && (
                  <div
                    className="bg-status-warning rounded-t transition-all hover:opacity-80"
                    style={{ height: `${solarHeight}%` }}
                    title={`Hour ${i}: Solar ${value.toFixed(0)}kW`}
                  ></div>
                )}
                {bessData[i] > 0 && (
                  <div
                    className="bg-status-info rounded-t transition-all hover:opacity-80"
                    style={{ height: `${bessHeight}%` }}
                    title={`Hour ${i}: BESS ${bessData[i].toFixed(0)}kW`}
                  ></div>
                )}
                {gridData[i] > 0 && (
                  <div
                    className="bg-muted rounded-t transition-all hover:opacity-80"
                    style={{ height: `${gridHeight}%` }}
                    title={`Hour ${i}: Grid ${gridData[i].toFixed(0)}kW`}
                  ></div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-status-warning rounded"></div>
            <span className="text-muted-foreground">Solar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-status-info rounded"></div>
            <span className="text-muted-foreground">BESS</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-muted rounded"></div>
            <span className="text-muted-foreground">Grid</span>
          </div>
        </div>
      </div>
    </WidgetCard>
  );
}
