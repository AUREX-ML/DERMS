import { TrendingUp, Activity, Battery, DollarSign } from 'lucide-react';

interface QuickStatsBarProps {
  totalOutput: number;
  gridFrequency: number;
  portfolioSoc: number;
  sitesCount: number;
  tariffBand: 'PEAK' | 'OFF-PEAK' | 'STANDARD';
  tariffRate: number;
}

export function QuickStatsBar({
  totalOutput,
  gridFrequency,
  portfolioSoc,
  sitesCount,
  tariffBand,
  tariffRate,
}: QuickStatsBarProps) {
  const isExporting = totalOutput > 0;
  const isFreqNormal = gridFrequency >= 49.5 && gridFrequency <= 50.5;

  return (
    <div className="grid grid-cols-4 gap-4 px-6 py-4 bg-secondary/30">
      {/* Total Output */}
      <div className="space-y-1">
        <div className="text-xs text-muted-foreground uppercase tracking-wide">Total Output</div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-mono font-semibold">{totalOutput.toFixed(2)}</span>
          <span className="text-sm text-muted-foreground">MW</span>
        </div>
        <div className="flex items-center gap-1 text-xs">
          <TrendingUp className={`w-3 h-3 ${isExporting ? 'text-status-healthy' : 'text-status-info'}`} />
          <span className={isExporting ? 'text-status-healthy' : 'text-status-info'}>
            {isExporting ? 'Exporting' : 'Importing'}
          </span>
        </div>
      </div>

      {/* Grid Frequency */}
      <div className="space-y-1">
        <div className="text-xs text-muted-foreground uppercase tracking-wide">Grid Freq</div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-mono font-semibold">{gridFrequency.toFixed(2)}</span>
          <span className="text-sm text-muted-foreground">Hz</span>
        </div>
        <div className="flex items-center gap-1 text-xs">
          <Activity className={`w-3 h-3 ${isFreqNormal ? 'text-status-healthy' : 'text-status-critical'}`} />
          <span className={isFreqNormal ? 'text-status-healthy' : 'text-status-critical'}>
            {isFreqNormal ? 'Normal' : 'Deviation'}
          </span>
        </div>
      </div>

      {/* Portfolio SoC */}
      <div className="space-y-1">
        <div className="text-xs text-muted-foreground uppercase tracking-wide">Portfolio SoC</div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-mono font-semibold">{portfolioSoc}</span>
          <span className="text-sm text-muted-foreground">%</span>
          <Battery className="w-5 h-5 text-status-info" />
        </div>
        <div className="text-xs text-muted-foreground">{sitesCount} sites</div>
      </div>

      {/* KPLC Tariff */}
      <div className="space-y-1">
        <div className="text-xs text-muted-foreground uppercase tracking-wide">KPLC Tariff Band</div>
        <div className="flex items-baseline gap-2">
          <span
            className={`text-lg font-mono font-semibold px-2 py-0.5 rounded ${
              tariffBand === 'PEAK'
                ? 'bg-status-warning/20 text-status-warning'
                : tariffBand === 'OFF-PEAK'
                  ? 'bg-status-healthy/20 text-status-healthy'
                  : 'bg-status-info/20 text-status-info'
            }`}
          >
            {tariffBand}
            {tariffBand === 'PEAK' && ' ⚠️'}
          </span>
        </div>
        <div className="text-xs font-mono text-muted-foreground">{tariffRate.toFixed(2)} KES/kWh</div>
      </div>
    </div>
  );
}
