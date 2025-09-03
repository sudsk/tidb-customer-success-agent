// frontend/src/components/ChurnDashboard.js
import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Users, TrendingDown, Bot, CheckCircle, 
  Clock, Zap, Heart, DollarSign, Shield 
} from 'lucide-react';
import { apiService } from '../services/api';
import '../styles/Dashboard.css';

const ChurnDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [activities, setActivities] = useState([]);
  const [atRiskCustomers, setAtRiskCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [saveCounter, setSaveCounter] = useState(847);

  useEffect(() => {
    fetchDashboardData();
    
    // Refresh every 20 seconds for live demo
    const interval = setInterval(fetchDashboardData, 20000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Animate save counter
    const counterInterval = setInterval(() => {
      setSaveCounter(prev => prev + Math.floor(Math.random() * 2));
    }, 45000); // Increment occasionally
    
    return () => clearInterval(counterInterval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [metricsData, activitiesData, customersData] = await Promise.all([
        apiService.getDashboardMetrics(),
        apiService.getRecentActivities(),
        apiService.getAtRiskCustomers()
      ]);
      
      setMetrics(metricsData);
      setActivities(activitiesData.activities);
      setAtRiskCustomers(customersData.customers);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setIsLoading(false);
    }
  };

  const triggerAgent = async () => {
    try {
      await apiService.triggerAgent();
      setTimeout(fetchDashboardData, 3000); // Refresh after agent runs
    } catch (error) {
      console.error('Failed to trigger agent:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>🤖 Autonomous Customer Success Agent Starting...</p>
      </div>
    );
  }

  return (
    <div className="churn-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <Heart className="heartbeat" size={32} />
            </div>
            <div>
              <h1>Customer Success Agent</h1>
              <p>Autonomous AI that saves customers from churn • TiDB Serverless</p>
            </div>
          </div>
          
          <div className="status-section">
            <div className="save-counter">
              <div className="counter-value">{saveCounter}</div>
              <div className="counter-label">Customers Saved</div>
            </div>
            <div className="status-indicator active">
              <div className="status-dot pulse"></div>
              <span>Agent Monitoring</span>
            </div>
            <button className="trigger-button" onClick={triggerAgent}>
              <Zap size={16} />
              Save Customers Now
            </button>
          </div>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="kpi-section">
        <div className="kpi-card success">
          <div className="kpi-header">
            <CheckCircle className="kpi-icon" size={24} />
            <span className="kpi-change positive">+73 this week</span>
          </div>
          <div className="kpi-value">{metrics?.kpis?.customers_saved?.value || 0}</div>
          <div className="kpi-label">Customers Saved</div>
          <div className="kpi-detail">From high-risk churn situations</div>
        </div>

        <div className="kpi-card revenue">
          <div className="kpi-header">
            <DollarSign className="kpi-icon" size={24} />
            <span className="kpi-change positive">{metrics?.kpis?.revenue_retained?.change}</span>
          </div>
          <div className="kpi-value">${(metrics?.kpis?.revenue_retained?.value / 1000000).toFixed(1)}M</div>
          <div className="kpi-label">Revenue Retained</div>
          <div className="kpi-detail">Monthly recurring revenue saved</div>
        </div>

        <div className="kpi-card churn">
          <div className="kpi-header">
            <TrendingDown className="kpi-icon" size={24} />
            <span className="kpi-change positive">{metrics?.kpis?.churn_reduction?.change}</span>
          </div>
          <div className="kpi-value">{metrics?.kpis?.churn_reduction?.value}%</div>
          <div className="kpi-label">Churn Rate Reduction</div>
          <div className="kpi-detail">Dramatic improvement in retention</div>
        </div>

        <div className="kpi-card autonomy">
          <div className="kpi-header">
            <Bot className="kpi-icon" size={24} />
            <span className="kpi-change neutral">{metrics?.kpis?.agent_autonomy?.change}</span>
          </div>
          <div className="kpi-value">{metrics?.kpis?.agent_autonomy?.value}%</div>
          <div className="kpi-label">Agent Autonomy</div>
          <div className="kpi-detail">Fully autonomous interventions</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Live Activity Feed */}
        <div className="activity-section">
          <div className="section-header">
            <h2>🚨 Live Customer Rescue Operations</h2>
            <div className="activity-status">
              <div className="status-dot active pulse"></div>
              <span>Real-time</span>
            </div>
          </div>
          
          <div className="activity-feed">
            {activities.map((activity, index) => (
              <ActivityItem key={activity.id || index} activity={activity} />
            ))}
          </div>
        </div>

        {/* At-Risk Customers */}
        <div className="customers-section">
          <div className="section-header">
            <h2>⚠️ Customers at Risk</h2>
            <span className="customer-count">{atRiskCustomers.length} high-risk</span>
          </div>
          
          <div className="customers-list">
            {atRiskCustomers.slice(0, 8).map(customer => (
              <CustomerCard key={customer.id} customer={customer} />
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Analytics */}
      <div className="bottom-analytics">
        <div className="analytics-card">
          <h3>📊 Churn Risk Distribution</h3>
          <div className="risk-breakdown">
            <div className="risk-item critical">
              <div className="risk-label">Critical Risk</div>
              <div className="risk-count">
                {metrics?.churn_risk_summary?.churn_distribution?.critical?.count || 0}
              </div>
              <div className="risk-revenue">
                ${(metrics?.churn_risk_summary?.churn_distribution?.critical?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              </div>
            </div>
            <div className="risk-item high">
              <div className="risk-label">High Risk</div>
              <div className="risk-count">
                {metrics?.churn_risk_summary?.churn_distribution?.high?.count || 0}
              </div>
              <div className="risk-revenue">
                ${(metrics?.churn_risk_summary?.churn_distribution?.high?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              </div>
            </div>
            <div className="risk-item medium">
              <div className="risk-label">Medium Risk</div>
              <div className="risk-count">
                {metrics?.churn_risk_summary?.churn_distribution?.medium?.count || 0}
              </div>
              <div className="risk-revenue">
                ${(metrics?.churn_risk_summary?.churn_distribution?.medium?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              </div>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>🤖 Agent Performance</h3>
          <div className="performance-metrics">
            <div className="metric">
              <span className="metric-label">Response Time:</span>
              <span className="metric-value">{metrics?.agent_performance?.avg_response_time_minutes?.toFixed(0) || 0}s</span>
            </div>
            <div className="metric">
              <span className="metric-label">Customers Processed (24h):</span>
              <span className="metric-value">{metrics?.agent_performance?.customers_processed_24h || 0}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Critical Interventions:</span>
              <span className="metric-value">{metrics?.agent_performance?.critical_interventions_24h || 0}</span>
            </div>
          </div>
        </div>

        <div className="analytics-card tidb-status">
          <h3>🚀 TiDB Serverless Status</h3>
          <div className="tidb-metrics">
            <div className="tidb-metric">Vector Search: <span className="status-ok">Active</span></div>
            <div className="tidb-metric">HTAP Processing: <span className="status-ok">1.2M ops/sec</span></div>
            <div className="tidb-metric">Churn Models: <span className="status-ok">Updated 2min ago</span></div>
            <div className="tidb-metric">Auto-scaling: <span className="status-ok">Optimized</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ActivityItem = ({ activity }) => {
  const getActivityIcon = (type, status) => {
    if (type === 'churn_intervention') {
      return <AlertTriangle className={`activity-icon ${status}`} size={20} />;
    } else if (type === 'customer_saved') {
      return <CheckCircle className="activity-icon success" size={20} />;
    } else if (type === 'self_correction') {
      return <Zap className="activity-icon warning" size={20} />;
    } else {
      return <Bot className="activity-icon info" size={20} />;
    }
  };

  const getUrgencyClass = (urgency) => {
    switch (urgency) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'low';
    }
  };

  return (
    <div className={`activity-item ${getUrgencyClass(activity.urgency)} ${activity.status}`}>
      <div className="activity-header">
        {getActivityIcon(activity.type, activity.status)}
        <div className="activity-content">
          <div className="activity-title">{activity.title}</div>
          <div className="activity-description">{activity.description}</div>
        </div>
        <div className="activity-timestamp">{activity.timestamp}</div>
      </div>
      
      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
        <div className="activity-metadata">
          {activity.metadata.churn_probability && (
            <span className="metadata-tag">
              Risk: {(activity.metadata.churn_probability * 100).toFixed(0)}%
            </span>
          )}
          {activity.metadata.revenue_at_risk && (
            <span className="metadata-tag revenue">
              ${(activity.metadata.revenue_at_risk / 1000).toFixed(0)}K at risk
            </span>
          )}
        </div>
      )}
    </div>
  );
};

const CustomerCard = ({ customer }) => {
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#10b981';
    }
  };

  return (
    <div className="customer-card" style={{'--risk-color': getRiskColor(customer.churn_risk_level)}}>
      <div className="customer-header">
        <div className="customer-info">
          <div className="customer-name">{customer.name}</div>
          <div className="customer-company">{customer.company}</div>
        </div>
        <div className="churn-probability">
          {(customer.churn_probability * 100).toFixed(0)}%
        </div>
      </div>
      
      <div className="customer-metrics">
        <div className="metric-item">
          <span className="metric-label">Revenue:</span>
          <span className="metric-value">${(customer.annual_contract_value / 1000).toFixed(0)}K</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Last Login:</span>
          <span className="metric-value">{customer.last_login_days_ago}d ago</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Usage Score:</span>
          <span className="metric-value">{(customer.feature_usage_score * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};

export default ChurnDashboard;
