import { Cpu, Thermometer, Wifi, Cable } from 'lucide-react';

interface Gateway {
  id: string;
  name: string;
  connection: 'ETH' | '4G' | 'WiFi';
  status: 'online' | 'degraded' | 'offline';
  cpuUsage: number;
  temperature: number;
}

interface RaspberryPiGatewaysProps {
  gateways: Gateway[];
}

export function RaspberryPiGateways({ gateways }: RaspberryPiGatewaysProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return '🟢';
      case 'degraded':
        return '🟡';
      case 'offline':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const getConnectionIcon = (connection: string) => {
    switch (connection) {
      case 'ETH':
        return <Cable className="w-3 h-3" />;
      case '4G':
        return <Wifi className="w-3 h-3" />;
      case 'WiFi':
        return <Wifi className="w-3 h-3" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Cpu className="w-5 h-5 text-muted-foreground" />
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Raspberry Pi Gateway Status</h3>
      </div>

      <div className="space-y-2">
        {gateways.map((gateway) => {
          const isTempHigh = gateway.temperature > 50;
          const isCpuHigh = gateway.cpuUsage > 80;

          return (
            <div
              key={gateway.id}
              className="flex items-center justify-between p-3 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1">
                <span className="text-base">{getStatusIcon(gateway.status)}</span>
                <span className="font-mono text-sm font-semibold">{gateway.name}</span>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1">
                  {getConnectionIcon(gateway.connection)}
                  <span className="font-mono">{gateway.connection}</span>
                </div>

                <div className="flex items-center gap-1">
                  <Cpu className={`w-3 h-3 ${isCpuHigh ? 'text-status-warning' : 'text-muted-foreground'}`} />
                  <span className={`font-mono ${isCpuHigh ? 'text-status-warning' : ''}`}>
                    CPU {gateway.cpuUsage}%
                  </span>
                </div>

                <div className="flex items-center gap-1">
                  <Thermometer
                    className={`w-3 h-3 ${isTempHigh ? 'text-status-warning' : 'text-muted-foreground'}`}
                  />
                  <span className={`font-mono ${isTempHigh ? 'text-status-warning' : ''}`}>
                    {gateway.temperature}°C
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
