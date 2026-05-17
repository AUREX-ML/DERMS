import { Sun } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface SolarPVOutputProps {
  data: Array<{ time: string; power: number }>;
  currentOutput: number;
}

export function SolarPVOutput({ data, currentOutput }: SolarPVOutputProps) {
  const maxOutput = Math.max(...data.map((d) => d.power), 100);

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Solar PV Output</h3>
        <Sun className="w-5 h-5 text-status-warning" />
      </div>

      {/* Current Output */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-mono font-semibold text-status-warning">
            {currentOutput.toFixed(1)}
          </span>
          <span className="text-sm text-muted-foreground">kW</span>
        </div>
        <div className="text-xs text-muted-foreground mt-1">Last 30 minutes</div>
      </div>

      {/* Sparkline Chart */}
      <div className="h-24 min-h-24">
        <ResponsiveContainer width="100%" height="100%" minHeight={96}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="solarGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgb(245, 158, 11)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="rgb(245, 158, 11)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              tick={{ fontSize: 10, fill: 'currentColor', opacity: 0.5 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis hide domain={[0, maxOutput * 1.1]} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-card)',
                border: '1px solid var(--color-border)',
                borderRadius: '0.5rem',
                fontSize: '0.75rem',
              }}
              labelStyle={{ color: 'var(--color-foreground)' }}
            />
            <Area
              type="monotone"
              dataKey="power"
              stroke="rgb(245, 158, 11)"
              strokeWidth={2}
              fill="url(#solarGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="mt-4 pt-4 border-t border-border grid grid-cols-3 gap-3 text-xs">
        <div>
          <div className="text-muted-foreground">Peak Today</div>
          <div className="font-mono mt-1">{Math.max(...data.map((d) => d.power)).toFixed(1)} kW</div>
        </div>
        <div>
          <div className="text-muted-foreground">Average</div>
          <div className="font-mono mt-1">
            {(data.reduce((sum, d) => sum + d.power, 0) / data.length).toFixed(1)} kW
          </div>
        </div>
        <div>
          <div className="text-muted-foreground">Capacity</div>
          <div className="font-mono mt-1">150.0 kW</div>
        </div>
      </div>
    </div>
  );
}
