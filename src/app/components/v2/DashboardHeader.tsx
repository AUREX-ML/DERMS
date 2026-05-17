import { Zap, Clock } from 'lucide-react';

interface DashboardHeaderProps {
  operator: string;
  portfolioSize: number;
  currentTime: string;
  isLive: boolean;
}

export function DashboardHeader({ operator, portfolioSize, currentTime, isLive }: DashboardHeaderProps) {
  return (
    <div className="bg-[#1e2433] border-b border-border px-6 py-3 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Kenya Commercial VPP</h1>
              <div className="text-xs text-muted-foreground">
                {operator} • {portfolioSize} Sites
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {isLive && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-status-healthy/20 rounded border border-status-healthy/40">
              <div className="w-2 h-2 rounded-full bg-status-healthy animate-pulse"></div>
              <span className="text-status-healthy text-sm font-medium">LIVE</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span>{currentTime} EAT</span>
          </div>
        </div>
      </div>
    </div>
  );
}
