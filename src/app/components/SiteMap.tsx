import { MapPin, ZoomIn, ZoomOut } from 'lucide-react';
import { useState } from 'react';

interface Site {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: 'healthy' | 'warning' | 'alarm';
  county: string;
}

interface SiteMapProps {
  sites: Site[];
  onSiteSelect: (siteId: string) => void;
}

export function SiteMap({ sites, onSiteSelect }: SiteMapProps) {
  const [selectedSite, setSelectedSite] = useState<string | null>(null);

  // Kenya approximate bounds
  const bounds = {
    minLat: -4.7,
    maxLat: 5.0,
    minLng: 33.9,
    maxLng: 41.9,
  };

  const latToY = (lat: number) => {
    return ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * 100;
  };

  const lngToX = (lng: number) => {
    return ((lng - bounds.minLng) / (bounds.maxLng - bounds.minLng)) * 100;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'status-healthy';
      case 'warning':
        return 'status-warning';
      case 'alarm':
        return 'status-critical';
      default:
        return 'muted';
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-wide">Site Map</h3>
        <div className="flex gap-1">
          <button className="p-1 hover:bg-accent rounded">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button className="p-1 hover:bg-accent rounded">
            <ZoomOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative w-full h-64 bg-secondary rounded-lg border border-border overflow-hidden">
        {/* Simplified Kenya outline */}
        <svg
          viewBox="0 0 100 100"
          className="absolute inset-0 w-full h-full opacity-20"
          preserveAspectRatio="none"
        >
          <path
            d="M 20,10 L 80,10 L 85,30 L 80,50 L 70,80 L 50,90 L 30,85 L 20,60 Z"
            fill="none"
            stroke="currentColor"
            strokeWidth="0.5"
          />
        </svg>

        {/* Site Pins */}
        {sites.map((site) => {
          const x = lngToX(site.lng);
          const y = latToY(site.lat);
          const statusColor = getStatusColor(site.status);

          return (
            <div
              key={site.id}
              className="absolute -translate-x-1/2 -translate-y-full cursor-pointer group"
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => {
                setSelectedSite(site.id);
                onSiteSelect(site.id);
              }}
            >
              <div className="relative">
                {/* Pulse effect for alarms */}
                {site.status === 'alarm' && (
                  <div className={`absolute inset-0 bg-${statusColor} rounded-full animate-ping`}></div>
                )}

                {/* Pin */}
                <MapPin
                  className={`w-6 h-6 text-${statusColor} relative z-10 drop-shadow-lg`}
                  fill={`var(--color-${statusColor})`}
                />
              </div>

              {/* Tooltip */}
              <div
                className={`absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-3 py-2 bg-card border border-border rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20 ${
                  selectedSite === site.id ? 'opacity-100' : ''
                }`}
              >
                <div className="text-xs font-mono font-semibold">{site.name}</div>
                <div className="text-xs text-muted-foreground">{site.county}</div>
                <div className={`text-xs text-${statusColor} mt-1 capitalize`}>{site.status}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <MapPin className="w-4 h-4 text-status-healthy" fill="var(--color-status-healthy)" />
          <span className="text-muted-foreground">Healthy</span>
        </div>
        <div className="flex items-center gap-1">
          <MapPin className="w-4 h-4 text-status-warning" fill="var(--color-status-warning)" />
          <span className="text-muted-foreground">Warning</span>
        </div>
        <div className="flex items-center gap-1">
          <MapPin className="w-4 h-4 text-status-critical" fill="var(--color-status-critical)" />
          <span className="text-muted-foreground">Alarm</span>
        </div>
      </div>
    </div>
  );
}
