import { Leaf } from 'lucide-react';

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
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Leaf className="w-5 h-5 text-status-healthy" />
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Sustainability</h3>
      </div>

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
    </div>
  );
}
