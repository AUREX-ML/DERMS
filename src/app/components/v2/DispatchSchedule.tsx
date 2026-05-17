import { Calendar } from 'lucide-react';
import { WidgetCard } from './WidgetCard';

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
    <WidgetCard title="Dispatch Schedule" icon={Calendar}>
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
    </WidgetCard>
  );
}
