import { Leaf } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

interface SustainabilityMetricsProps {
  solarGenerated: number;
  co2Offset: number;
  kcuEstimate: number;
  greenCertStatus: string;
}

export function SustainabilityMetrics({
  solarGenerated,
  co2Offset,
  kcuEstimate,
  greenCertStatus,
}: SustainabilityMetricsProps) {
  return (
    <WidgetCard title="Sustainability" icon={Leaf}>
      <div className="space-y-3">
        <div className="flex justify-between items-baseline">
          <span className="text-xs text-muted-foreground">Solar Generated</span>
          <span className="font-mono font-semibold">{solarGenerated.toFixed(1)} MWh</span>
        </div>

        <div className="flex justify-between items-baseline">
          <span className="text-xs text-muted-foreground">CO₂ Offset</span>
          <span className="font-mono font-semibold text-status-healthy">{co2Offset.toLocaleString()} kg</span>
        </div>

        <div className="flex justify-between items-baseline">
          <span className="text-xs text-muted-foreground">KCU Estimate</span>
          <span className="font-mono font-semibold">{kcuEstimate.toFixed(2)} units</span>
        </div>

        <div className="pt-3 border-t border-border">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">Green Cert</span>
            <span className="text-xs font-mono px-2 py-1 bg-status-warning/20 text-status-warning rounded">
              {greenCertStatus}
            </span>
          </div>
        </div>
      </div>
    </WidgetCard>
  );
}
