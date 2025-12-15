import React from 'react';

const StatisticsCards = ({ data }) => {
  const formatCurrency = (value) => {
    if (!value) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const cards = [
    {
      title: 'Total Alerts',
      value: data.total || 0,
      icon: '🔔',
      color: '#3b82f6'
    },
    {
      title: 'Critical Alerts',
      value: data.critical || 0,
      icon: '⚠️',
      color: '#ef4444'
    },
    {
      title: 'High Priority',
      value: data.high || 0,
      icon: '🔴',
      color: '#f59e0b'
    },
    {
      title: 'Pending Review',
      value: data.pending || 0,
      icon: '⏳',
      color: '#8b5cf6'
    },
    {
      title: 'Total Amount',
      value: formatCurrency(data.total_amount),
      icon: '💰',
      color: '#10b981'
    }
  ];

  return (
    <div className="statistics-container">
      {cards.map((card, index) => (
        <div key={index} className="stat-card" style={{ borderLeftColor: card.color }}>
          <div className="stat-icon">{card.icon}</div>
          <div className="stat-content">
            <h3 className="stat-title">{card.title}</h3>
            <p className="stat-value">{card.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatisticsCards;
