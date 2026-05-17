import { useState } from 'react';
import {
  Menu,
  X,
  LayoutDashboard,
  MapPin,
  Activity,
  Battery,
  TrendingDown,
  Leaf,
  Cpu,
  Calendar,
  AlertTriangle
} from 'lucide-react';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

interface BurgerMenuProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

export function BurgerMenu({ currentView, onNavigate }: BurgerMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  const menuItems: MenuItem[] = [
    { id: 'overview', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'sites', label: 'Site Management', icon: MapPin },
    { id: 'power', label: 'Power Flow', icon: Activity },
    { id: 'battery', label: 'Battery Systems', icon: Battery },
    { id: 'savings', label: 'Savings & Analytics', icon: TrendingDown },
    { id: 'sustainability', label: 'Sustainability', icon: Leaf },
    { id: 'gateways', label: 'IoT Gateways', icon: Cpu },
    { id: 'schedule', label: 'Dispatch Schedule', icon: Calendar },
    { id: 'alarms', label: 'Alarms & Events', icon: AlertTriangle, badge: 3 },
  ];

  return (
    <>
      {/* Burger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-lg hover:bg-primary/90 transition-colors"
      >
        {isOpen ? <X className="w-5 h-5 text-white" /> : <Menu className="w-5 h-5 text-white" />}
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-[#1e2433] border-r border-border z-40 shadow-2xl transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="h-16 border-b border-border px-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">VPP Control</div>
            <div className="text-xs text-muted-foreground">Navigation</div>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium flex-1 text-left">{item.label}</span>
                {item.badge && (
                  <span className="px-2 py-0.5 bg-status-critical rounded-full text-xs text-white">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
          <div className="text-xs text-muted-foreground">
            <div>Actis Energy Management</div>
            <div className="mt-1">4 Sites • 1.05 MW Capacity</div>
          </div>
        </div>
      </div>
    </>
  );
}
