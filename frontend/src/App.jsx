import React, { useState, useEffect, Suspense, lazy } from 'react';
import { fetchStatistics, fetchRiskTrends, fetchTopCompanies, fetchAlerts } from './services/api';
import './App.css';

// Lazy load components for code splitting and faster initial load
const StatisticsCards = lazy(() => import('./components/StatisticsCards'));
const RiskTrendChart = lazy(() => import('./components/RiskTrendChart'));
const TopCompaniesChart = lazy(() => import('./components/TopCompaniesChart'));
const AlertsTable = lazy(() => import('./components/AlertsTable'));

function App() {
  const [statistics, setStatistics] = useState(null);
  const [riskTrends, setRiskTrends] = useState([]);
  const [topCompanies, setTopCompanies] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [statsData, trendsData, companiesData, alertsData] = await Promise.all([
        fetchStatistics(),
        fetchRiskTrends(),
        fetchTopCompanies(),
        fetchAlerts()
      ]);

      setStatistics(statsData);
      setRiskTrends(trendsData);
      setTopCompanies(companiesData);
      setAlerts(alertsData.results || alertsData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Market Supervision Dashboard</h1>
        <p className="subtitle">Real-time Risk Monitoring & Analytics</p>
      </header>

      <main className="dashboard-content">
        {/* Lazy loaded components with suspense fallback */}
        <Suspense fallback={<div className="component-loading">Loading statistics...</div>}>
          {statistics && <StatisticsCards data={statistics} />}
        </Suspense>

        <div className="charts-grid">
          <Suspense fallback={<div className="component-loading">Loading chart...</div>}>
            {riskTrends.length > 0 && <RiskTrendChart data={riskTrends} />}
          </Suspense>

          <Suspense fallback={<div className="component-loading">Loading chart...</div>}>
            {topCompanies.length > 0 && <TopCompaniesChart data={topCompanies} />}
          </Suspense>
        </div>

        <Suspense fallback={<div className="component-loading">Loading table...</div>}>
          {alerts.length > 0 && <AlertsTable data={alerts} />}
        </Suspense>
      </main>

      <footer className="app-footer">
        <p>Market Supervision System © 2024 | Data refreshes every 5 minutes</p>
      </footer>
    </div>
  );
}

export default App;
