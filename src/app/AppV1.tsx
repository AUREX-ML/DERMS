import { useState, useEffect } from 'react';
import { TopNavigation } from './components/TopNavigation';
import { Sidebar } from './components/Sidebar';
import { FrequencyGauge } from './components/FrequencyGauge';
import { GridStatusIndicator } from './components/GridStatusIndicator';
import { PowerFlowMeter } from './components/PowerFlowMeter';
import { BESSStateOfCharge } from './components/BESSStateOfCharge';
import { SolarPVOutput } from './components/SolarPVOutput';
import { SiteMap } from './components/SiteMap';
import { AlarmTable } from './components/AlarmTable';
import { KPICards } from './components/KPICards';
import { LoadSheddingCalendar } from './components/LoadSheddingCalendar';
import { AlertTriangle } from 'lucide-react';

// Mock data generation functions
function generateSolarData() {
  const data = [];
  const now = new Date();
  for (let i = 29; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60000);
    const hour = time.getHours();
    // Simulate solar curve (peak at midday)
    const basePower = Math.max(0, Math.sin(((hour - 6) / 12) * Math.PI) * 120);
    const variance = Math.random() * 15 - 7.5;
    data.push({
      time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      power: Math.max(0, basePower + variance),
    });
  }
  return data;
}

export default function AppV1() {
  const [selectedSite, setSelectedSite] = useState('site_NBI_001');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Real-time telemetry state
  const [frequency, setFrequency] = useState(49.95);
  const [frequencyUpdated, setFrequencyUpdated] = useState(new Date());
  const [isGridConnected, setIsGridConnected] = useState(true);
  const [isLoadShedding, setIsLoadShedding] = useState(false);
  const [activePower, setActivePower] = useState(45.3);
  const [reactivePower, setReactivePower] = useState(12.8);
  const [bessSoc, setBessSoc] = useState(68);
  const [bessUpdated, setBessUpdated] = useState(new Date());
  const [solarData, setSolarData] = useState(generateSolarData());

  // Site data
  const sites = [
    { id: '1', name: 'site_NBI_001', lat: -1.286389, lng: 36.817223, status: 'healthy' as const, county: 'Nairobi' },
    { id: '2', name: 'site_NBI_002', lat: -1.2921, lng: 36.8219, status: 'healthy' as const, county: 'Nairobi' },
    { id: '3', name: 'site_MBA_001', lat: -4.0435, lng: 39.6682, status: 'warning' as const, county: 'Mombasa' },
    { id: '4', name: 'site_KSM_001', lat: -0.0917, lng: 34.7680, status: 'healthy' as const, county: 'Kisumu' },
    { id: '5', name: 'site_NKR_001', lat: -0.3031, lng: 36.0800, status: 'alarm' as const, county: 'Nakuru' },
  ];

  // Alarm data
  const [alarms, setAlarms] = useState([
    {
      id: '1',
      name: 'Frequency Deviation',
      site: 'site_NKR_001',
      severity: 'critical' as const,
      triggeredAt: new Date(Date.now() - 300000),
      status: 'active' as const,
    },
    {
      id: '2',
      name: 'Low BESS SoC',
      site: 'site_MBA_001',
      severity: 'warning' as const,
      triggeredAt: new Date(Date.now() - 120000),
      status: 'active' as const,
    },
  ]);

  // Load-shedding schedule
  const loadSheddingEvents = [
    {
      id: '1',
      date: '2026-05-11',
      startTime: '14:00',
      endTime: '18:00',
      duration: '4 hours',
      status: 'scheduled' as const,
    },
    {
      id: '2',
      date: '2026-05-12',
      startTime: '10:00',
      endTime: '14:00',
      duration: '4 hours',
      status: 'scheduled' as const,
    },
    {
      id: '3',
      date: '2026-05-13',
      startTime: '18:00',
      endTime: '22:00',
      duration: '4 hours',
      status: 'scheduled' as const,
    },
  ];

  // Simulate real-time updates (5-second refresh)
  useEffect(() => {
    const interval = setInterval(() => {
      // Update frequency with realistic variation
      setFrequency((prev) => {
        const delta = (Math.random() - 0.5) * 0.15;
        return Math.max(48.5, Math.min(51.5, prev + delta));
      });
      setFrequencyUpdated(new Date());

      // Update power values
      setActivePower((prev) => Math.max(0, Math.min(150, prev + (Math.random() - 0.5) * 5)));
      setReactivePower((prev) => Math.max(-50, Math.min(50, prev + (Math.random() - 0.5) * 3)));

      // Update BESS SoC (slow discharge/charge)
      setBessSoc((prev) => {
        const change = (Math.random() - 0.5) * 0.5;
        return Math.max(0, Math.min(100, prev + change));
      });
      setBessUpdated(new Date());

      // Regenerate solar data every minute
      if (Math.random() > 0.9) {
        setSolarData(generateSolarData());
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Apply dark mode
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleAcknowledgeAlarm = (alarmId: string) => {
    setAlarms((prev) => prev.filter((a) => a.id !== alarmId));
  };

  const activeAlarms = alarms.filter((a) => a.status === 'active');
  const currentSolarOutput = solarData[solarData.length - 1]?.power || 0;

  // Check for frequency deviation alarm
  const hasFrequencyAlarm = frequency < 49.5 || frequency > 50.5;

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {hasFrequencyAlarm && (
        <div className="bg-status-critical px-6 py-3 flex items-center gap-3 animate-pulse">
          <AlertTriangle className="w-5 h-5 text-white" />
          <span className="text-white font-mono">
            ⚠️ CRITICAL: Grid frequency deviation detected ({frequency.toFixed(2)} Hz)
          </span>
        </div>
      )}

      <TopNavigation
        selectedSite={selectedSite}
        onSiteChange={setSelectedSite}
        role="VPP Operator"
        alarmCount={activeAlarms.length}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar isCollapsed={isSidebarCollapsed} onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)} />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <KPICards
            totalCapacity={1250}
            totalActivePower={activePower * sites.length}
            fleetAvgSoc={bessSoc}
            sitesOnline={sites.filter((s) => s.status === 'healthy').length}
            totalSites={sites.length}
          />

          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 lg:col-span-4 space-y-6">
              <FrequencyGauge frequency={frequency} lastUpdated={frequencyUpdated} />
              <GridStatusIndicator isConnected={isGridConnected} isLoadShedding={isLoadShedding} />
            </div>

            <div className="col-span-12 lg:col-span-4 space-y-6">
              <PowerFlowMeter
                title="Active Power Flow"
                value={activePower}
                unit="kW"
                max={150}
                type="active"
              />
              <PowerFlowMeter
                title="Reactive Power"
                value={reactivePower}
                unit="kVAR"
                max={75}
                type="reactive"
              />
            </div>

            <div className="col-span-12 lg:col-span-4 space-y-6">
              <BESSStateOfCharge soc={bessSoc} lastUpdated={bessUpdated} />
              <SolarPVOutput data={solarData} currentOutput={currentSolarOutput} />
            </div>

            <div className="col-span-12 lg:col-span-7">
              <SiteMap sites={sites} onSiteSelect={(id) => console.log('Selected site:', id)} />
            </div>

            <div className="col-span-12 lg:col-span-5">
              <LoadSheddingCalendar events={loadSheddingEvents} />
            </div>

            <div className="col-span-12">
              <AlarmTable alarms={alarms} onAcknowledge={handleAcknowledgeAlarm} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
