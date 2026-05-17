import { ChevronLeft, Activity, TrendingUp, TrendingDown } from 'lucide-react';
import { WidgetCard } from '../WidgetCard';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PowerFlowDetailViewProps {
  onBack: () => void;
}

export function PowerFlowDetailView({ onBack }: PowerFlowDetailViewProps) {
  // Generate 24-hour data
  const generateData = () => {
    const data = [];
    for (let i = 0; i < 24; i++) {
      const solar = Math.max(0, Math.sin(((i - 6) / 12) * Math.PI) * 800 + Math.random() * 100);
      const bess = (i >= 6 && i <= 9) || (i >= 17 && i <= 20) ? 300 + Math.random() * 100 : 0;
      const grid = solar < 200 ? 400 + Math.random() * 200 : Math.random() * 50;

      data.push({
        hour: `${i}:00`,
        solar: Math.round(solar),
        bess: Math.round(bess),
        grid: Math.round(grid),
        total: Math.round(solar + bess + grid),
      });
    }
    return data;
  };

  const data = generateData();
  const currentHour = new Date().getHours();
  const current = data[currentHour];

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
          <h2 className="text-xl font-semibold">Power Flow Analysis</h2>
          <p className="text-sm text-muted-foreground">24-hour power generation and consumption trends</p>
        </div>
      </div>

      {/* Current Stats */}
      <div className="grid grid-cols-4 gap-4">
        <WidgetCard title="Total Power" icon={Activity}>
          <div className="text-3xl font-semibold">{current.total}</div>
          <div className="text-sm text-muted-foreground">kW</div>
        </WidgetCard>

        <WidgetCard title="Solar Generation" icon={TrendingUp}>
          <div className="text-3xl font-semibold text-status-warning">{current.solar}</div>
          <div className="text-sm text-muted-foreground">kW</div>
        </WidgetCard>

        <WidgetCard title="BESS Output" icon={Activity}>
          <div className="text-3xl font-semibold text-status-info">{current.bess}</div>
          <div className="text-sm text-muted-foreground">kW</div>
        </WidgetCard>

        <WidgetCard title="Grid Import" icon={TrendingDown}>
          <div className="text-3xl font-semibold text-muted-foreground">{current.grid}</div>
          <div className="text-sm text-muted-foreground">kW</div>
        </WidgetCard>
      </div>

      {/* Main Chart */}
      <WidgetCard title="24-Hour Power Flow" icon={Activity}>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="solarGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="bessGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gridGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b92ab" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#8b92ab" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="hour"
                stroke="#8b92ab"
                tick={{ fill: '#8b92ab', fontSize: 12 }}
              />
              <YAxis stroke="#8b92ab" tick={{ fill: '#8b92ab', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#242b3d',
                  border: '1px solid #3a4159',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#e0e7ff' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="solar"
                stroke="#f59e0b"
                fill="url(#solarGrad)"
                name="Solar (kW)"
              />
              <Area
                type="monotone"
                dataKey="bess"
                stroke="#06b6d4"
                fill="url(#bessGrad)"
                name="BESS (kW)"
              />
              <Area
                type="monotone"
                dataKey="grid"
                stroke="#8b92ab"
                fill="url(#gridGrad)"
                name="Grid (kW)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </WidgetCard>
    </div>
  );
}
