import React from 'react';

const AlertsTable = ({ data }) => {
  const getSeverityBadge = (severity) => {
    const colors = {
      CRITICAL: '#ef4444',
      HIGH: '#f59e0b',
      MEDIUM: '#3b82f6',
      LOW: '#10b981'
    };
    return {
      backgroundColor: colors[severity] || '#6b7280',
      color: 'white',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 'bold'
    };
  };

  const getStatusBadge = (status) => {
    const colors = {
      PENDING: '#f59e0b',
      REVIEWING: '#3b82f6',
      RESOLVED: '#10b981'
    };
    return {
      backgroundColor: colors[status] || '#6b7280',
      color: 'white',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px'
    };
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="table-container">
      <h2 className="table-title">Recent Risk Alerts</h2>
      <div className="table-wrapper">
        <table className="alerts-table">
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Company</th>
              <th>Violation Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Amount</th>
              <th>Region</th>
              <th>Detected At</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 20).map((alert) => (
              <tr key={alert.id}>
                <td className="alert-id">{alert.alert_id}</td>
                <td>{alert.company_name}</td>
                <td>{alert.violation_type}</td>
                <td>
                  <span style={getSeverityBadge(alert.severity)}>
                    {alert.severity}
                  </span>
                </td>
                <td>
                  <span style={getStatusBadge(alert.status)}>
                    {alert.status}
                  </span>
                </td>
                <td className="amount">{formatCurrency(alert.amount)}</td>
                <td>{alert.region}</td>
                <td className="date">{formatDate(alert.detected_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AlertsTable;
