import { Calendar, Clock } from 'lucide-react';

interface LoadSheddingEvent {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  duration: string;
  status: 'scheduled' | 'active' | 'completed';
}

interface LoadSheddingCalendarProps {
  events: LoadSheddingEvent[];
}

export function LoadSheddingCalendar({ events }: LoadSheddingCalendarProps) {
  const today = new Date().toISOString().split('T')[0];
  const upcomingEvents = events.filter((e) => e.date >= today && e.status !== 'completed');

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-sm text-muted-foreground uppercase tracking-wide">
            KPLC Load-Shedding Schedule
          </h3>
        </div>
        {upcomingEvents.length > 0 && (
          <span className="px-2 py-1 bg-status-warning/10 text-status-warning text-xs font-mono rounded">
            {upcomingEvents.length} Scheduled
          </span>
        )}
      </div>

      {upcomingEvents.length === 0 ? (
        <div className="text-center py-8">
          <Calendar className="w-10 h-10 text-muted-foreground/30 mx-auto mb-3" />
          <div className="text-sm text-muted-foreground">No scheduled load-shedding events</div>
        </div>
      ) : (
        <div className="space-y-3">
          {upcomingEvents.slice(0, 5).map((event) => (
            <div
              key={event.id}
              className={`flex items-start gap-3 p-3 rounded-lg border ${
                event.status === 'active'
                  ? 'bg-status-warning/10 border-status-warning'
                  : 'bg-secondary border-border'
              }`}
            >
              <div className="flex-shrink-0 mt-0.5">
                <Clock
                  className={`w-5 h-5 ${
                    event.status === 'active' ? 'text-status-warning' : 'text-muted-foreground'
                  }`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-mono text-sm">
                    {new Date(event.date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                  {event.status === 'active' && (
                    <span className="px-2 py-0.5 bg-status-warning text-xs font-mono rounded animate-pulse">
                      ACTIVE
                    </span>
                  )}
                </div>
                <div className="text-sm text-muted-foreground">
                  <span className="font-mono">
                    {event.startTime} - {event.endTime}
                  </span>
                  <span className="mx-2">•</span>
                  <span>{event.duration}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {upcomingEvents.length > 5 && (
        <button className="w-full mt-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          View all {upcomingEvents.length} events →
        </button>
      )}
    </div>
  );
}
