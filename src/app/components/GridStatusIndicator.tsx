import { Zap, ZapOff } from 'lucide-react';

interface GridStatusIndicatorProps {
  isConnected: boolean;
  isLoadShedding: boolean;
}

export function GridStatusIndicator({ isConnected, isLoadShedding }: GridStatusIndicatorProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-sm text-muted-foreground uppercase tracking-wide mb-4">Grid Status</h3>

      <div className="space-y-3">
        {/* Connection Status */}
        <div
          className={`flex items-center gap-3 px-4 py-3 rounded-lg border-2 ${
            isConnected
              ? 'bg-status-healthy/10 border-status-healthy'
              : 'bg-status-critical/10 border-status-critical'
          }`}
        >
          {isConnected ? (
            <Zap className="w-6 h-6 text-status-healthy" />
          ) : (
            <ZapOff className="w-6 h-6 text-status-critical" />
          )}
          <div>
            <div className={`font-mono ${isConnected ? 'text-status-healthy' : 'text-status-critical'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-xs text-muted-foreground">
              {isConnected ? 'Grid operational' : 'Grid offline'}
            </div>
          </div>
        </div>

        {/* Load-Shedding Status */}
        {isLoadShedding && (
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg border-2 bg-status-warning/10 border-status-warning">
            <div className="w-6 h-6 flex items-center justify-center">
              <div className="w-4 h-4 rounded-full bg-status-warning animate-pulse"></div>
            </div>
            <div>
              <div className="font-mono text-status-warning">Load-Shedding Mode</div>
              <div className="text-xs text-muted-foreground">KPLC scheduled outage</div>
            </div>
          </div>
        )}

        {/* Grid Parameters */}
        <div className="mt-4 pt-4 border-t border-border space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Nominal Frequency</span>
            <span className="font-mono">50.0 Hz</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Nominal Voltage (1φ)</span>
            <span className="font-mono">240 V</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Grid Connection</span>
            <span className="font-mono">11 kV</span>
          </div>
        </div>
      </div>
    </div>
  );
}
