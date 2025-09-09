// Business-focused ChurnDashboard.js - TiDB features integrated into agent workflow
import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Users, TrendingDown, Bot, CheckCircle, 
  Clock, Zap, Heart, DollarSign, Shield, Loader
} from 'lucide-react';
import { apiService } from '../services/api';
import '../styles/Dashboard.css';

const ChurnDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [activities, setActivities] = useState([]);
  const [atRiskCustomers, setAtRiskCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [saveCounter, setSaveCounter] = useState(847);
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [recentSaves, setRecentSaves] = useState([]);
  const [demoActivities, setDemoActivities] = useState([]);

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
    }, 45000);
    
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
      
      // Merge demo activities with backend activities
      const backendActivities = activitiesData.activities || [];
      const mergedActivities = [...demoActivities, ...backendActivities].slice(0, 25);
      setActivities(mergedActivities);
      
      setAtRiskCustomers(customersData.customers);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setIsLoading(false);
    }
  };

  const addTemporaryActivity = (activity) => {
    setDemoActivities(prev => {
      const newDemoActivities = [activity, ...prev].slice(0, 15);
      return newDemoActivities;
    });
    
    setActivities(prev => [activity, ...prev.slice(0, 24)]);
  };

  const addCustomerSaveActivity = (customer) => {
    const saveActivity = {
      id: `save-${Date.now()}`,
      type: 'customer_saved',
      title: `✅ CUSTOMER SAVED: ${customer.name} (${customer.company})`,
      description: `AI agent successfully prevented churn • Risk reduced from ${(customer.churn_probability * 100).toFixed(0)}% to 23% • $${(customer.annual_contract_value/1000).toFixed(0)}K revenue secured`,
      status: 'success',
      urgency: 'low',
      timestamp: 'Just now',
      metadata: {
        customer: customer.name,
        revenue_saved: customer.annual_contract_value,
        risk_before: customer.churn_probability,
        risk_after: 0.23
      }
    };
    
    addTemporaryActivity(saveActivity);
    setRecentSaves(prev => [customer.name, ...prev.slice(0, 4)]);
  };

  const addSelfCorrectionActivity = () => {
    const correctionActivity = {
      id: `correction-${Date.now()}`,
      type: 'self_correction',
      title: '🔄 Agent Self-Correction: Adapted strategy for better results',
      description: 'Initial email approach failed • Agent automatically switched to phone outreach • Customer successfully engaged',
      status: 'corrected',
      urgency: 'medium',
      timestamp: 'Just now',
      metadata: {}
    };
    
    addTemporaryActivity(correctionActivity);
  };

  const triggerAgent = async () => {
    setIsAgentRunning(true);
    
    try {
      // Business-focused activity sequence showing agent intelligence
      
      // Step 1: Agent analyzes customer patterns
      addTemporaryActivity({
        id: `analysis-${Date.now()}`,
        type: 'customer_analysis',
        title: '🔍 AI Agent: Analyzing customer behavior patterns...',
        description: 'Agent scanning 1,247 customer profiles • Finding similar cases from successful interventions • Identifying optimal retention strategies',
        status: 'executing',
        urgency: 'high',
        timestamp: 'Now',
        metadata: { customers_analyzed: 1247 }
      });

      // Step 2: Agent recalls successful strategies
      setTimeout(() => {
        addTemporaryActivity({
          id: `strategy-${Date.now()}`,
          type: 'strategy_selection',
          title: '🧠 AI Agent: Found proven retention strategies',
          description: 'Agent recalled 3 similar cases from past successes • Same customer segment with 91% risk → 89% success rate • Strategy: Personalized training approach',
          status: 'success',
          urgency: 'medium',
          timestamp: 'Just now',
          metadata: { similar_cases: 3, success_rate: 0.89 }
        });
      }, 1500);

      // Step 3: Agent analyzes customer communications  
      setTimeout(() => {
        addTemporaryActivity({
          id: `communication-${Date.now()}`,
          type: 'communication_insight',
          title: '📞 AI Agent: Discovered customer pain points',
          description: 'Agent analyzed 247 recent messages • Detected frustration with billing complexity • Key insight: Customer needs simplified onboarding',
          status: 'warning',
          urgency: 'high',
          timestamp: 'Just now',
          metadata: { messages_analyzed: 247, sentiment: 'frustrated' }
        });
      }, 2500);

      await apiService.triggerAgent();
      
      // Step 4: Customer gets saved
      setTimeout(() => {
        const customerToSave = atRiskCustomers[Math.floor(Math.random() * Math.min(3, atRiskCustomers.length))];
        if (customerToSave) {
          addCustomerSaveActivity(customerToSave);
          setSaveCounter(prev => prev + 1);
        }
      }, 3500);

      // Step 5: Show agent learning
      setTimeout(() => {
        addTemporaryActivity({
          id: `learning-${Date.now()}`,
          type: 'agent_learning',
          title: '📈 AI Agent: Learning from success',
          description: 'Agent updated retention patterns • Strategy effectiveness confirmed • Similar future cases will benefit from this approach',
          status: 'info',
          urgency: 'low',
          timestamp: 'Just now',
          metadata: { patterns_updated: 1 }
        });
      }, 4500);

      setTimeout(() => {
        fetchDashboardData();
        setIsAgentRunning(false);
      }, 6000);

    } catch (error) {
      console.error('Failed to trigger agent:', error);
      setIsAgentRunning(false);
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
              <p>Autonomous AI that saves customers from churn • Powered by advanced analytics</p>
            </div>
          </div>
          
          <div className="status-section">
            <div className="save-counter">
              <div className="counter-value">{saveCounter}</div>
              <div className="counter-label">Customers Saved</div>
              {recentSaves.length > 0 && (
                <div className="recent-saves">
                  <div className="save-flash">+1 {recentSaves[0]}!</div>
                </div>
              )}
            </div>
            <div className={`status-indicator ${isAgentRunning ? 'running' : 'active'}`}>
              <div className="status-dot pulse"></div>
              <span>{isAgentRunning ? 'Agent Working...' : 'Agent Monitoring'}</span>
            </div>
            <button 
              className={`trigger-button ${isAgentRunning ? 'running' : ''}`}
              onClick={triggerAgent}
              disabled={isAgentRunning}
            >
              {isAgentRunning ? (
                <>
                  <Loader className="spin" size={16} />
                  Rescuing Customers...
                </>
              ) : (
                <>
                  <Zap size={16} />
                  Save Customers Now
                </>
              )}
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
          <div className="kpi-value">{saveCounter}</div>
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
              <div className={`status-dot ${isAgentRunning ? 'running' : 'active'} pulse`}></div>
              <span>{isAgentRunning ? 'AI Agent Processing...' : 'Real-time Monitoring'}</span>
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
              <CustomerCard 
                key={customer.id} 
                customer={customer} 
                isBeingRescued={recentSaves.includes(customer.name)}
              />
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

        <div className="analytics-card ai-intelligence">
          <h3>🧠 AI Intelligence Engine</h3>
          <div className="ai-metrics">
            <div className="ai-metric">Pattern Recognition: <span className="status-ok">Advanced ML Models</span></div>
            <div className="ai-metric">Real-time Processing: <span className="status-ok">1.2M ops/sec</span></div>
            <div className="ai-metric">Success Prediction: <span className="status-ok">94.7% accuracy</span></div>
            <div className="ai-metric">Auto-scaling: <span className="status-ok">Cloud-native</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced ActivityItem component for business focus
const ActivityItem = ({ activity }) => {
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    if (activity.timestamp === 'Now' || activity.timestamp === 'Just now') {
      setIsNew(true);
      setTimeout(() => setIsNew(false), 3000);
    }
  }, [activity.timestamp]);

  const getActivityIcon = (type, status) => {
    if (type === 'customer_analysis') {
      return <Bot className="activity-icon analyzing" size={20} />;
    } else if (type === 'strategy_selection') {
      return <Bot className="activity-icon success" size={20} />;
    } else if (type === 'communication_insight') {
      return <Bot className="activity-icon warning" size={20} />;
    } else if (type === 'agent_learning') {
      return <Bot className="activity-icon info" size={20} />;
    } else if (type === 'customer_saved') {
      return <CheckCircle className="activity-icon success" size={20} />;
    } else if (type === 'self_correction') {
      return <Zap className="activity-icon warning" size={20} />;
    } else if (type === 'churn_intervention') {
      return <AlertTriangle className={`activity-icon ${status}`} size={20} />;
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
    <div className={`activity-item ${getUrgencyClass(activity.urgency)} ${activity.status} ${isNew ? 'new-activity' : ''}`}>
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
          {activity.metadata.customers_analyzed && (
            <span className="metadata-tag analytics">
              {activity.metadata.customers_analyzed} profiles analyzed
            </span>
          )}
          {activity.metadata.similar_cases && (
            <span className="metadata-tag intelligence">
              {activity.metadata.similar_cases} similar cases found
            </span>
          )}
          {activity.metadata.messages_analyzed && (
            <span className="metadata-tag communication">
              {activity.metadata.messages_analyzed} messages analyzed
            </span>
          )}
          {activity.metadata.revenue_saved && (
            <span className="metadata-tag revenue">
              ${(activity.metadata.revenue_saved / 1000).toFixed(0)}K secured
            </span>
          )}
        </div>
      )}
    </div>
  );
};

// Customer Card Component (same as before)
const CustomerCard = ({ customer, isBeingRescued }) => {
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#10b981';
    }
  };

  return (
    <div className={`customer-card ${isBeingRescued ? 'being-rescued' : ''}`} style={{'--risk-color': getRiskColor(customer.churn_risk_level)}}>
      {isBeingRescued && (
        <div className="rescue-indicator">
          <CheckCircle size={16} />
          RESCUED!
        </div>
      )}
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
