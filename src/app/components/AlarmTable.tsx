import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface Alarm {
  id: string;
  name: string;
  site: string;
  severity: 'critical' | 'warning';
  triggeredAt: Date;
  status: 'active' | 'cleared';
}

interface AlarmTableProps {
  alarms: Alarm[];
  onAcknowledge: (alarmId: string) => void;
}

export function AlarmTable({ alarms, onAcknowledge }: AlarmTableProps) {
  const activeAlarms = alarms.filter((a) => a.status === 'active');

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Active Alarms</h3>
        <div className="flex items-center gap-2">
          {activeAlarms.length > 0 ? (
            <span className="px-2 py-1 bg-status-critical/10 text-status-critical text-xs font-mono rounded">
              {activeAlarms.length} Active
            </span>
          ) : (
            <span className="px-2 py-1 bg-status-healthy/10 text-status-healthy text-xs font-mono rounded">
              All Clear
            </span>
          )}
        </div>
      </div>

      {activeAlarms.length === 0 ? (
        <div className="text-center py-12">
          <CheckCircle className="w-12 h-12 text-status-healthy mx-auto mb-3" />
          <div className="text-lg">No active alarms ✅</div>
          <div className="text-sm text-muted-foreground mt-1">All systems operating normally</div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 text-muted-foreground font-normal">Severity</th>
                <th className="text-left py-3 px-2 text-muted-foreground font-normal">Alarm Name</th>
                <th className="text-left py-3 px-2 text-muted-foreground font-normal">Site</th>
                <th className="text-left py-3 px-2 text-muted-foreground font-normal">Triggered At</th>
                <th className="text-left py-3 px-2 text-muted-foreground font-normal">Action</th>
              </tr>
            </thead>
            <tbody>
              {activeAlarms.map((alarm) => (
                <tr
                  key={alarm.id}
                  className={`border-b border-border hover:bg-accent/50 ${
                    alarm.severity === 'critical' ? 'bg-status-critical/5' : 'bg-status-warning/5'
                  }`}
                >
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-2">
                      {alarm.severity === 'critical' ? (
                        <>
                          <XCircle className="w-4 h-4 text-status-critical" />
                          <span className="font-mono text-status-critical">Critical</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-4 h-4 text-status-warning" />
                          <span className="font-mono text-status-warning">Warning</span>
                        </>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-2 font-mono">{alarm.name}</td>
                  <td className="py-3 px-2 font-mono text-muted-foreground">{alarm.site}</td>
                  <td className="py-3 px-2 font-mono text-muted-foreground">
                    {formatTime(alarm.triggeredAt)}
                  </td>
                  <td className="py-3 px-2">
                    <button
                      onClick={() => onAcknowledge(alarm.id)}
                      className="px-3 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-xs"
                    >
                      Acknowledge
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
