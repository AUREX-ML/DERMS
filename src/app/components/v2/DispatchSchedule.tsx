import { Calendar } from 'lucide-react';

interface DispatchEvent {
  time: string;
  action: string;
  type: 'peak' | 'solar' | 'charge';
}

interface DispatchScheduleProps {
  events: DispatchEvent[];
}

export function DispatchSchedule({ events }: DispatchScheduleProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-muted-foreground" />
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Dispatch Schedule</h3>
      </div>

      <div className="space-y-3">
        {events.map((event, index) => (
          <div key={`event-${index}`} className="flex items-center gap-3 p-3 bg-secondary rounded-lg">
            <div className="flex-shrink-0 w-12 text-center">
              <div className="font-mono text-sm font-semibold">{event.time}</div>
            </div>
            <div className="flex-shrink-0 text-muted-foreground">─</div>
            <div className="flex-1">
              <span className="text-sm font-mono">{event.action}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
