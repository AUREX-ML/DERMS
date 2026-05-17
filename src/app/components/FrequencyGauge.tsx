import { useEffect, useState } from 'react';

interface FrequencyGaugeProps {
  frequency: number;
  lastUpdated: Date;
}

export function FrequencyGauge({ frequency, lastUpdated }: FrequencyGaugeProps) {
  const [isStale, setIsStale] = useState(false);

  useEffect(() => {
    const checkStale = () => {
      const diff = Date.now() - lastUpdated.getTime();
      setIsStale(diff > 30000); // 30 seconds
    };

    checkStale();
    const interval = setInterval(checkStale, 1000);
    return () => clearInterval(interval);
  }, [lastUpdated]);

  const getStatusColor = () => {
    if (frequency >= 49.5 && frequency <= 50.5) return 'status-healthy';
    if ((frequency >= 49.0 && frequency < 49.5) || (frequency > 50.5 && frequency <= 51.0))
      return 'status-warning';
    return 'status-critical';
  };

  const statusColor = getStatusColor();
  const angle = ((frequency - 47) / 6) * 180 - 90; // Map 47-53 Hz to -90 to +90 degrees

  const getTimeAgo = () => {
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    return `${Math.floor(diff / 60)}m ago`;
  };

  return (
    <div className={`bg-card border border-border rounded-lg p-6 ${isStale ? 'opacity-60' : ''}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Grid Frequency</h3>
        <span className="text-xs text-muted-foreground font-mono">Updated {getTimeAgo()}</span>
      </div>

      {isStale && (
        <div className="mb-2 px-3 py-1 bg-status-warning/10 border border-status-warning/30 rounded text-xs text-status-warning">
          ⚠ Stale data (no update &gt;30s)
        </div>
      )}

      <div className="relative w-full aspect-square max-w-[280px] mx-auto">
        {/* Gauge Background */}
        <svg viewBox="0 0 200 120" className="w-full">
          {/* Critical zones (red) */}
          <path
            d="M 20 100 A 80 80 0 0 1 40 45"
            fill="none"
            stroke="rgb(239, 68, 68)"
            strokeWidth="12"
            opacity="0.3"
          />
          <path
            d="M 160 45 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="rgb(239, 68, 68)"
            strokeWidth="12"
            opacity="0.3"
          />
          {/* Warning zones (amber) */}
          <path
            d="M 40 45 A 80 80 0 0 1 70 25"
            fill="none"
            stroke="rgb(245, 158, 11)"
            strokeWidth="12"
            opacity="0.3"
          />
          <path
            d="M 130 25 A 80 80 0 0 1 160 45"
            fill="none"
            stroke="rgb(245, 158, 11)"
            strokeWidth="12"
            opacity="0.3"
          />
          {/* Healthy zone (green) */}
          <path
            d="M 70 25 A 80 80 0 0 1 130 25"
            fill="none"
            stroke="rgb(16, 185, 129)"
            strokeWidth="12"
            opacity="0.3"
          />

          {/* Tick marks */}
          {[47, 48, 49, 49.5, 50, 50.5, 51, 52, 53].map((hz) => {
            const tickAngle = ((hz - 47) / 6) * 180 - 90;
            const rad = (tickAngle * Math.PI) / 180;
            const x1 = 100 + 70 * Math.cos(rad);
            const y1 = 100 + 70 * Math.sin(rad);
            const x2 = 100 + 80 * Math.cos(rad);
            const y2 = 100 + 80 * Math.sin(rad);
            const isHalfTick = hz === 49.5 || hz === 50.5;

            return (
              <g key={`tick-${hz}`}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="currentColor"
                  strokeWidth={isHalfTick ? "1" : "2"}
                  opacity="0.5"
                />
                {!isHalfTick && (
                  <text
                    x={100 + 60 * Math.cos(rad)}
                    y={100 + 60 * Math.sin(rad)}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-[8px] fill-current opacity-70"
                  >
                    {hz}
                  </text>
                )}
              </g>
            );
          })}

          {/* Needle */}
          <g transform={`rotate(${angle} 100 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="35"
              stroke={`var(--color-${statusColor})`}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill={`var(--color-${statusColor})`} />
          </g>
        </svg>

        {/* Center Reading */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pt-8">
          <div className={`text-4xl font-mono font-semibold text-${statusColor}`}>
            {frequency.toFixed(2)}
          </div>
          <div className="text-sm text-muted-foreground">Hz</div>
        </div>
      </div>

      {/* Status Labels */}
      <div className="mt-4 grid grid-cols-3 gap-2 text-xs text-center">
        <div className="flex items-center justify-center gap-1">
          <div className="w-2 h-2 rounded-full bg-status-critical"></div>
          <span className="text-muted-foreground">&lt;49.0</span>
        </div>
        <div className="flex items-center justify-center gap-1">
          <div className="w-2 h-2 rounded-full bg-status-healthy"></div>
          <span className="text-muted-foreground">49.5-50.5</span>
        </div>
        <div className="flex items-center justify-center gap-1">
          <div className="w-2 h-2 rounded-full bg-status-critical"></div>
          <span className="text-muted-foreground">&gt;51.0</span>
        </div>
      </div>
    </div>
  );
}
