import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const TopCompaniesChart = ({ data }) => {
  const formattedData = data.slice(0, 10).map(item => ({
    company: item.company_name.length > 15 
      ? item.company_name.substring(0, 15) + '...' 
      : item.company_name,
    riskScore: parseFloat(item.risk_score.toFixed(1)),
    violations: item.total_violations
  }));

  return (
    <div className="chart-container">
      <h2 className="chart-title">Top 10 High-Risk Companies</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={formattedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="company" angle={-45} textAnchor="end" height={80} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="riskScore" fill="#ef4444" name="Risk Score" />
          <Bar dataKey="violations" fill="#f59e0b" name="Violations" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TopCompaniesChart;
