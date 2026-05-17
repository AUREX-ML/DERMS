import { Battery, BatteryWarning, AlertTriangle } from 'lucide-react';

interface BESSStateOfChargeProps {
  soc: number; // 0-100
  lastUpdated: Date;
}

export function BESSStateOfCharge({ soc, lastUpdated }: BESSStateOfChargeProps) {
  const getStatusColor = () => {
    if (soc >= 50) return 'status-healthy';
    if (soc >= 20) return 'status-warning';
    return 'status-critical';
  };

  const statusColor = getStatusColor();
  const circumference = 2 * Math.PI * 70; // radius = 70
  const offset = circumference - (soc / 100) * circumference;

  const getTimeAgo = () => {
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    return `${Math.floor(diff / 60)}m ago`;
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">BESS State of Charge</h3>
        <span className="text-xs text-muted-foreground font-mono">Updated {getTimeAgo()}</span>
      </div>

      {/* Warning Banner */}
      {soc < 20 && (
        <div
          className={`mb-4 px-3 py-2 rounded-lg border flex items-center gap-2 ${
            soc < 10
              ? 'bg-status-critical/10 border-status-critical text-status-critical'
              : 'bg-status-warning/10 border-status-warning text-status-warning'
          }`}
        >
          {soc < 10 ? (
            <AlertTriangle className="w-4 h-4" />
          ) : (
            <BatteryWarning className="w-4 h-4" />
          )}
          <span className="text-sm font-mono">
            {soc < 10 ? 'CRITICAL: Low SoC' : 'WARNING: Low SoC'}
          </span>
        </div>
      )}

      {/* Donut Chart */}
      <div className="relative w-full aspect-square max-w-[220px] mx-auto">
        <svg viewBox="0 0 160 160" className="w-full -rotate-90">
          {/* Background circle */}
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="currentColor"
            strokeWidth="16"
            opacity="0.1"
          />
          {/* Progress circle */}
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke={`var(--color-${statusColor})`}
            strokeWidth="16"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Battery className={`w-8 h-8 mb-2 text-${statusColor}`} />
          <div className={`text-4xl font-mono font-semibold text-${statusColor}`}>
            {soc.toFixed(0)}%
          </div>
          <div className="text-xs text-muted-foreground mt-1">State of Charge</div>
        </div>
      </div>

      {/* Color Bands Legend */}
      <div className="mt-6 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-status-healthy"></div>
            <span className="text-muted-foreground">Healthy</span>
          </div>
          <span className="font-mono text-muted-foreground">&gt;50%</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-status-warning"></div>
            <span className="text-muted-foreground">Warning</span>
          </div>
          <span className="font-mono text-muted-foreground">20-50%</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-status-critical"></div>
            <span className="text-muted-foreground">Critical</span>
          </div>
          <span className="font-mono text-muted-foreground">&lt;20%</span>
        </div>
      </div>
    </div>
  );
}
