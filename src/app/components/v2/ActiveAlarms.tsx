import { AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

interface Alarm {
  id: string;
  message: string;
  severity: 'warning' | 'info' | 'success';
}

interface ActiveAlarmsProps {
  alarms: Alarm[];
}

export function ActiveAlarms({ alarms }: ActiveAlarmsProps) {
  const getIcon = (severity: string) => {
    switch (severity) {
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-status-warning" />;
      case 'info':
        return <Info className="w-4 h-4 text-status-info" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-status-healthy" />;
      default:
        return null;
    }
  };

  const getPrefix = (severity: string) => {
    switch (severity) {
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✅';
      default:
        return '';
    }
  };

  return (
    <WidgetCard title="Active Alarms" icon={AlertTriangle}>
      <div className="space-y-2">
        {alarms.map((alarm) => (
          <div
            key={alarm.id}
            className={`flex items-start gap-3 p-3 rounded-lg ${
              alarm.severity === 'warning'
                ? 'bg-status-warning/10 border border-status-warning/30'
                : alarm.severity === 'info'
                  ? 'bg-status-info/10 border border-status-info/30'
                  : 'bg-status-healthy/10 border border-status-healthy/30'
            }`}
          >
            <div className="flex-shrink-0 mt-0.5">{getIcon(alarm.severity)}</div>
            <div className="flex-1 text-sm font-mono">
              <span className="mr-1">{getPrefix(alarm.severity)}</span>
              {alarm.message}
            </div>
          </div>
        ))}
      </div>
    </WidgetCard>
  );
}
