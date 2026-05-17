import { ChevronLeft, ChevronRight, Filter, MapPin } from 'lucide-react';
import { useState } from 'react';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const [selectedCounty, setSelectedCounty] = useState<string>('all');
  const [selectedClass, setSelectedClass] = useState<string>('all');

  const counties = ['All Counties', 'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru'];
  const siteClasses = ['All Classes', 'Industrial', 'Commercial', 'Residential'];

  return (
    <aside
      className={`h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Toggle Button */}
      <div className="h-16 flex items-center justify-end px-4 border-b border-sidebar-border">
        <button
          onClick={onToggle}
          className="p-2 hover:bg-sidebar-accent rounded-lg transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {!isCollapsed && (
        <div className="p-4 space-y-6">
          {/* Site Navigation */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-muted-foreground" />
              <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Sites</h3>
            </div>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 hover:bg-sidebar-accent rounded-lg transition-colors">
                <span className="font-mono text-sm">All Sites</span>
                <span className="float-right text-muted-foreground text-sm">12</span>
              </button>
              <button className="w-full text-left px-3 py-2 hover:bg-sidebar-accent rounded-lg transition-colors">
                <span className="font-mono text-sm">Active</span>
                <span className="float-right text-status-healthy text-sm">11</span>
              </button>
              <button className="w-full text-left px-3 py-2 hover:bg-sidebar-accent rounded-lg transition-colors">
                <span className="font-mono text-sm">Offline</span>
                <span className="float-right text-muted-foreground text-sm">1</span>
              </button>
            </div>
          </div>

          {/* Quick Filters */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Filters</h3>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">County</label>
                <select
                  value={selectedCounty}
                  onChange={(e) => setSelectedCounty(e.target.value)}
                  className="w-full bg-sidebar-accent border border-sidebar-border rounded-lg px-3 py-2 text-sm"
                >
                  {counties.map((county) => (
                    <option key={county} value={county.toLowerCase().replace(' ', '-')}>
                      {county}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Site Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full bg-sidebar-accent border border-sidebar-border rounded-lg px-3 py-2 text-sm"
                >
                  {siteClasses.map((siteClass) => (
                    <option key={siteClass} value={siteClass.toLowerCase().replace(' ', '-')}>
                      {siteClass}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Utility Filter */}
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">Grid Utility</label>
            <select className="w-full bg-sidebar-accent border border-sidebar-border rounded-lg px-3 py-2 text-sm">
              <option value="kplc">KPLC</option>
              <option value="ketraco">KETRACO</option>
            </select>
          </div>
        </div>
      )}
    </aside>
  );
}
