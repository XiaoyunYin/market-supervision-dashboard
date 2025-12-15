import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const RiskTrendChart = ({ data }) => {
  const formattedData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    Critical: item.critical_alerts,
    High: item.high_alerts,
    Medium: item.medium_alerts,
    Low: item.low_alerts,
  }));

  return (
    <div className="chart-container">
      <h2 className="chart-title">Risk Alert Trends (30 Days)</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="Critical" stroke="#ef4444" strokeWidth={2} />
          <Line type="monotone" dataKey="High" stroke="#f59e0b" strokeWidth={2} />
          <Line type="monotone" dataKey="Medium" stroke="#3b82f6" strokeWidth={2} />
          <Line type="monotone" dataKey="Low" stroke="#10b981" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskTrendChart;
