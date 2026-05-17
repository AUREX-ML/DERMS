import { ArrowDown, ArrowUp } from 'lucide-react';

interface PowerFlowMeterProps {
  title: string;
  value: number;
  unit: string;
  max: number;
  type: 'active' | 'reactive';
}

export function PowerFlowMeter({ title, value, unit, max, type }: PowerFlowMeterProps) {
  const isExport = value < 0;
  const absValue = Math.abs(value);
  const percentage = Math.min((absValue / max) * 100, 100);

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-sm text-muted-foreground uppercase tracking-wide mb-4">{title}</h3>

      <div className="space-y-4">
        {/* Value Display */}
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-mono font-semibold">{absValue.toFixed(1)}</span>
          <span className="text-sm text-muted-foreground">{unit}</span>
        </div>

        {/* Direction Indicator */}
        <div className="flex items-center gap-2">
          {type === 'active' && (
            <>
              {isExport ? (
                <ArrowUp className="w-4 h-4 text-status-healthy" />
              ) : (
                <ArrowDown className="w-4 h-4 text-status-info" />
              )}
              <span className={`text-sm font-mono ${isExport ? 'text-status-healthy' : 'text-status-info'}`}>
                {isExport ? 'Export' : 'Import'}
              </span>
            </>
          )}
        </div>

        {/* Bar Meter */}
        <div className="space-y-2">
          <div className="h-3 bg-secondary rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                type === 'active'
                  ? isExport
                    ? 'bg-status-healthy'
                    : 'bg-status-info'
                  : 'bg-chart-3'
              }`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-muted-foreground font-mono">
            <span>0</span>
            <span>
              {max} {unit}
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="pt-3 border-t border-border grid grid-cols-2 gap-3 text-xs">
          <div>
            <div className="text-muted-foreground">Max Capacity</div>
            <div className="font-mono mt-1">
              {max} {unit}
            </div>
          </div>
          <div>
            <div className="text-muted-foreground">Utilization</div>
            <div className="font-mono mt-1">{percentage.toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
