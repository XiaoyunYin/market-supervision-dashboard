import axios from 'axios';

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const fetchStatistics = async () => {
  const response = await apiClient.get('/alerts/statistics/');
  return response.data;
};

export const fetchRiskTrends = async () => {
  const response = await apiClient.get('/alerts/risk_trends/');
  return response.data;
};

export const fetchTopCompanies = async () => {
  const response = await apiClient.get('/alerts/top_companies/');
  return response.data;
};

export const fetchAlerts = async (params = {}) => {
  const response = await apiClient.get('/alerts/', { params });
  return response.data;
};

export const batchProcessAlerts = async (alertIds) => {
  const response = await apiClient.post('/alerts/batch_process/', {
    alert_ids: alertIds
  });
  return response.data;
};
