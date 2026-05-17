import { Bell, ChevronDown, User } from 'lucide-react';

interface TopNavigationProps {
  selectedSite: string;
  onSiteChange: (site: string) => void;
  role: string;
  alarmCount: number;
}

export function TopNavigation({ selectedSite, onSiteChange, role, alarmCount }: TopNavigationProps) {
  const sites = ['site_NBI_001', 'site_NBI_002', 'site_MBA_001', 'site_KSM_001'];

  return (
    <nav className="h-16 bg-card border-b border-border px-6 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-status-info rounded flex items-center justify-center">
            <span className="text-white font-mono">VPP</span>
          </div>
          <span className="font-mono">DERMS Control</span>
        </div>

        {/* Site Selector */}
        <div className="relative">
          <select
            value={selectedSite}
            onChange={(e) => onSiteChange(e.target.value)}
            className="bg-secondary px-4 py-2 pr-10 rounded-lg border border-border appearance-none cursor-pointer font-mono"
          >
            {sites.map((site) => (
              <option key={site} value={site}>
                {site}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Role Badge */}
        <div className="px-3 py-1 bg-status-info/10 border border-status-info/30 rounded-full">
          <span className="text-status-info text-sm font-mono">{role}</span>
        </div>

        {/* Notification Bell */}
        <button className="relative p-2 hover:bg-accent rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          {alarmCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-status-critical rounded-full flex items-center justify-center text-white text-xs font-mono">
              {alarmCount}
            </span>
          )}
        </button>

        {/* User Avatar */}
        <button className="w-9 h-9 bg-accent rounded-full flex items-center justify-center hover:bg-accent/80 transition-colors">
          <User className="w-5 h-5" />
        </button>
      </div>
    </nav>
  );
}
