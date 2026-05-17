import { TrendingDown, DollarSign } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

interface SavingsMetricsProps {
  gridImportAvoided: number;
  costSaved: number;
  demandChargeSaved: number;
}

export function SavingsMetrics({ gridImportAvoided, costSaved, demandChargeSaved }: SavingsMetricsProps) {
  return (
    <WidgetCard title="Today's Savings" icon={TrendingDown}>
      <div className="space-y-4">
        <div>
          <div className="text-xs text-muted-foreground mb-1">Grid Import Avoided</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-mono font-semibold text-status-healthy">
              {gridImportAvoided.toFixed(1)}
            </span>
            <span className="text-sm text-muted-foreground">MWh</span>
          </div>
        </div>

        <div>
          <div className="text-xs text-muted-foreground mb-1">Cost Saved</div>
          <div className="flex items-baseline gap-2">
            <DollarSign className="w-5 h-5 text-status-healthy" />
            <span className="text-2xl font-mono font-semibold text-status-healthy">
              KES {costSaved.toLocaleString()}
            </span>
          </div>
        </div>

        <div>
          <div className="text-xs text-muted-foreground mb-1">Demand Charge Saved</div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-mono font-semibold text-status-healthy">
              KES {(demandChargeSaved / 1000).toFixed(0)}k
            </span>
          </div>
        </div>
      </div>
    </WidgetCard>
  );
}
