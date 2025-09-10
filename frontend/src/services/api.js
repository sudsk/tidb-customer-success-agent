// frontend/src/services/api.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const apiService = {
  // Core dashboard endpoints
  async getDashboardMetrics() {
    const response = await axios.get(`${API_BASE}/dashboard/metrics`);
    return response.data;
  },

  async getRecentActivities() {
    const response = await axios.get(`${API_BASE}/dashboard/activities`);
    return response.data;
  },

  async getAtRiskCustomers() {
    const response = await axios.get(`${API_BASE}/customers/at-risk`);
    return response.data;
  },

  // Analytics endpoints
  async getChurnAnalytics() {
    const response = await axios.get(`${API_BASE}/analytics/churn`);
    return response.data;
  },

  async getRealtimeFeed() {
    const response = await axios.get(`${API_BASE}/feed/realtime`);
    return response.data;
  },

  async getRecentInterventions() {
    const response = await axios.get(`${API_BASE}/interventions/recent`);
    return response.data;
  },

  // Single unified agent trigger
  async triggerAgent() {
    const response = await axios.post(`${API_BASE}/agent/trigger`);
    return response.data;
  },

  // Real-time data endpoints
  async getRealTimeActivities() {
    const response = await axios.get(`${API_BASE}/activities/real-time`);
    return response.data;
  },

  async getRealTimeStats() {
    const response = await axios.get(`${API_BASE}/realtime/stats`);
    return response.data;
  }
};
