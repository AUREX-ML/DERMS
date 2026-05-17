import { Zap, Clock } from 'lucide-react';

interface DashboardHeaderProps {
  operator: string;
  portfolioSize: number;
  currentTime: string;
  isLive: boolean;
}

export function DashboardHeader({ operator, portfolioSize, currentTime, isLive }: DashboardHeaderProps) {
  return (
    <div className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-status-warning" />
            <div>
              <h1 className="font-mono font-semibold">KENYA COMMERCIAL REAL ESTATE VPP</h1>
              <div className="text-xs text-muted-foreground mt-0.5">
                Operated by: {operator} | Portfolio: {portfolioSize} Sites
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {isLive && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-status-healthy/10 border border-status-healthy rounded">
              <div className="w-2 h-2 rounded-full bg-status-healthy animate-pulse"></div>
              <span className="text-status-healthy font-mono text-sm">LIVE</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-sm font-mono">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span>{currentTime} EAT</span>
          </div>
        </div>
      </div>
    </div>
  );
}
