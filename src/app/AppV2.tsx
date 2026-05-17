import { useState, useEffect } from 'react';
import { DashboardHeader } from './components/v2/DashboardHeader';
import { QuickStatsBar } from './components/v2/QuickStatsBar';
import { SiteList } from './components/v2/SiteList';
import { PowerFlowTrend } from './components/v2/PowerFlowTrend';
import { DispatchSchedule } from './components/v2/DispatchSchedule';
import { SavingsMetrics } from './components/v2/SavingsMetrics';
import { ActiveAlarms } from './components/v2/ActiveAlarms';
import { SustainabilityMetrics } from './components/v2/SustainabilityMetrics';
import { RaspberryPiGateways } from './components/v2/RaspberryPiGateways';

// Generate 24-hour power flow data
function generate24HourData() {
  const solarData = [];
  const bessData = [];
  const gridData = [];

  for (let i = 0; i < 24; i++) {
    // Solar: peak at midday
    const solarPower = Math.max(0, Math.sin(((i - 6) / 12) * Math.PI) * 800 + Math.random() * 100);
    solarData.push(solarPower);

    // BESS: discharge during peak hours, charge at night
    let bessPower = 0;
    if ((i >= 6 && i <= 9) || (i >= 17 && i <= 20)) {
      bessPower = 300 + Math.random() * 100; // Discharge during peak
    } else if (i >= 22 || i <= 4) {
      bessPower = 200 + Math.random() * 50; // Charge at night
    }
    bessData.push(bessPower);

    // Grid: import when solar is low
    const gridPower = solarPower < 200 ? 400 + Math.random() * 200 : Math.random() * 50;
    gridData.push(gridPower);
  }

  return { solarData, bessData, gridData };
}

export default function AppV2() {
  const [currentTime, setCurrentTime] = useState('14:47');
  const [frequency, setFrequency] = useState(50.02);
  const [totalOutput, setTotalOutput] = useState(1.24);
  const [portfolioSoc, setPortfolioSoc] = useState(68);

  // Determine tariff band based on time
  const getTariffBand = () => {
    const hour = parseInt(currentTime.split(':')[0]);
    if ((hour >= 6 && hour < 10) || (hour >= 18 && hour < 22)) {
      return { band: 'PEAK' as const, rate: 28.5 };
    } else if (hour >= 22 || hour < 6) {
      return { band: 'OFF-PEAK' as const, rate: 12.8 };
    }
    return { band: 'STANDARD' as const, rate: 18.4 };
  };

  const tariff = getTariffBand();

  // Site data
  const sites = [
    {
      id: '1',
      name: 'Westlands BP',
      location: 'Westlands, Nairobi',
      status: 'online' as const,
      pvCapacity: 150,
      bessCapacity: 200,
      currentSoc: 72,
    },
    {
      id: '2',
      name: 'Upper Hill',
      location: 'Upper Hill, Nairobi',
      status: 'online' as const,
      pvCapacity: 300,
      bessCapacity: 400,
      currentSoc: 65,
    },
    {
      id: '3',
      name: 'Karen BP',
      location: 'Karen, Nairobi',
      status: 'partial' as const,
      pvCapacity: 100,
      bessCapacity: 120,
      currentSoc: 41,
    },
    {
      id: '4',
      name: 'Mombasa Rd',
      location: 'Mombasa Road, Nairobi',
      status: 'online' as const,
      pvCapacity: 500,
      bessCapacity: 1000,
      currentSoc: 78,
    },
  ];

  // Power flow data
  const powerFlowData = generate24HourData();

  // Dispatch schedule
  const dispatchEvents = [
    { time: '06:30', action: 'BESS Discharge (Peak)', type: 'peak' as const },
    { time: '08:30', action: 'Solar self-consume', type: 'solar' as const },
    { time: '17:30', action: 'BESS Discharge (Peak)', type: 'peak' as const },
    { time: '22:00', action: 'BESS Charge (Off-peak)', type: 'charge' as const },
  ];

  // Alarms
  const alarms = [
    { id: '1', message: 'BESS_KN_001 SOC Low (41%)', severity: 'warning' as const },
    { id: '2', message: 'GENSET_UH_001 Service Due', severity: 'info' as const },
    { id: '3', message: 'PI_WB_001 Reconnected (4G)', severity: 'success' as const },
  ];

  // Raspberry Pi gateways
  const gateways = [
    { id: '1', name: 'PI_WB_001', connection: 'ETH' as const, status: 'online' as const, cpuUsage: 12, temperature: 48 },
    { id: '2', name: 'PI_UH_001', connection: 'ETH' as const, status: 'online' as const, cpuUsage: 9, temperature: 45 },
    { id: '3', name: 'PI_KN_001', connection: '4G' as const, status: 'degraded' as const, cpuUsage: 18, temperature: 52 },
    { id: '4', name: 'PI_MR_001', connection: 'ETH' as const, status: 'online' as const, cpuUsage: 11, temperature: 47 },
  ];

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Update time
      const now = new Date();
      setCurrentTime(now.toTimeString().slice(0, 5));

      // Update frequency
      setFrequency((prev) => {
        const delta = (Math.random() - 0.5) * 0.05;
        return Math.max(49.8, Math.min(50.3, prev + delta));
      });

      // Update total output
      setTotalOutput((prev) => {
        const delta = (Math.random() - 0.5) * 0.1;
        return Math.max(0.8, Math.min(1.5, prev + delta));
      });

      // Update portfolio SoC
      setPortfolioSoc((prev) => {
        const delta = (Math.random() - 0.5) * 0.5;
        return Math.max(50, Math.min(85, prev + delta));
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Apply dark mode
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <div className="min-h-screen bg-[#1a1f2e] text-foreground">
      {/* Header */}
      <DashboardHeader
        operator="Actis Energy Management"
        portfolioSize={4}
        currentTime={currentTime}
        isLive={true}
      />

      {/* Quick Stats Bar */}
      <QuickStatsBar
        totalOutput={totalOutput}
        gridFrequency={frequency}
        portfolioSoc={Math.round(portfolioSoc)}
        sitesCount={sites.length}
        tariffBand={tariff.band}
        tariffRate={tariff.rate}
      />

      {/* Main Content */}
      <main className="p-4 space-y-4">
        {/* Site List - Full Width */}
        <SiteList sites={sites} />

        {/* Widget Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <PowerFlowTrend
            solarData={powerFlowData.solarData}
            bessData={powerFlowData.bessData}
            gridData={powerFlowData.gridData}
          />
          <DispatchSchedule events={dispatchEvents} />
          <SavingsMetrics gridImportAvoided={2.1} costSaved={59850} demandChargeSaved={12000} />
        </div>

        {/* Widget Grid Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ActiveAlarms alarms={alarms} />
          <SustainabilityMetrics
            solarGenerated={3.8}
            co2Offset={1140}
            kcuEstimate={1.14}
            greenCertStatus="Pending EPRA"
          />
          <RaspberryPiGateways gateways={gateways} />
        </div>
      </main>
    </div>
  );
}
