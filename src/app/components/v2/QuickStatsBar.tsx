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
    <div className="grid grid-cols-4 gap-4 px-6 py-4 bg-[#1a1f2e] border-b border-border">
      {/* Total Output */}
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center border border-primary/20">
          <TrendingUp className="w-6 h-6 text-primary" />
        </div>
        <div className="space-y-0.5">
          <div className="text-xs text-muted-foreground uppercase tracking-wide">Total Output</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-semibold">{totalOutput.toFixed(2)}</span>
            <span className="text-sm text-muted-foreground">MW</span>
          </div>
          <div className={`text-xs font-medium ${isExporting ? 'text-status-healthy' : 'text-status-info'}`}>
            {isExporting ? '↑ Exporting' : '↓ Importing'}
          </div>
        </div>
      </div>

      {/* Grid Frequency */}
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-status-info/10 rounded-lg flex items-center justify-center border border-status-info/20">
          <Activity className="w-6 h-6 text-status-info" />
        </div>
        <div className="space-y-0.5">
          <div className="text-xs text-muted-foreground uppercase tracking-wide">Grid Freq</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-semibold">{gridFrequency.toFixed(2)}</span>
            <span className="text-sm text-muted-foreground">Hz</span>
          </div>
          <div className={`text-xs font-medium ${isFreqNormal ? 'text-status-healthy' : 'text-status-critical'}`}>
            {isFreqNormal ? '✓ Normal' : '⚠ Deviation'}
          </div>
        </div>
      </div>

      {/* Portfolio SoC */}
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-status-healthy/10 rounded-lg flex items-center justify-center border border-status-healthy/20">
          <Battery className="w-6 h-6 text-status-healthy" />
        </div>
        <div className="space-y-0.5">
          <div className="text-xs text-muted-foreground uppercase tracking-wide">Portfolio SoC</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-semibold">{portfolioSoc}</span>
            <span className="text-sm text-muted-foreground">%</span>
          </div>
          <div className="text-xs text-muted-foreground">{sitesCount} sites active</div>
        </div>
      </div>

      {/* KPLC Tariff */}
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center border ${
          tariffBand === 'PEAK'
            ? 'bg-status-warning/10 border-status-warning/20'
            : tariffBand === 'OFF-PEAK'
              ? 'bg-status-healthy/10 border-status-healthy/20'
              : 'bg-status-info/10 border-status-info/20'
        }`}>
          <DollarSign className={`w-6 h-6 ${
            tariffBand === 'PEAK'
              ? 'text-status-warning'
              : tariffBand === 'OFF-PEAK'
                ? 'text-status-healthy'
                : 'text-status-info'
          }`} />
        </div>
        <div className="space-y-0.5">
          <div className="text-xs text-muted-foreground uppercase tracking-wide">KPLC Tariff</div>
          <div className="flex items-baseline gap-2">
            <span className={`text-lg font-semibold ${
              tariffBand === 'PEAK'
                ? 'text-status-warning'
                : tariffBand === 'OFF-PEAK'
                  ? 'text-status-healthy'
                  : 'text-status-info'
            }`}>
              {tariffBand}
            </span>
          </div>
          <div className="text-xs text-muted-foreground">{tariffRate.toFixed(2)} KES/kWh</div>
        </div>
      </div>
    </div>
  );
}
