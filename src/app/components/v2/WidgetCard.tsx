import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

interface WidgetCardProps {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
  actions?: ReactNode;
}

export function WidgetCard({ title, icon: Icon, children, actions }: WidgetCardProps) {
  return (
    <div className="bg-card rounded-lg border border-border shadow-lg overflow-hidden">
      {/* Widget Header */}
      <div className="bg-[#1e2433] border-b border-border px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4 text-primary" />}
          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">{title}</h3>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      {/* Widget Content */}
      <div className="p-4">{children}</div>
    </div>
  );
}
