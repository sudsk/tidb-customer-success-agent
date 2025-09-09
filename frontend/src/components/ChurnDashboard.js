// Fixed ChurnDashboard.js with persistent demo activities
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
  const [demoActivities, setDemoActivities] = useState([]); // Store demo activities separately

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
      
      // FIXED: Merge demo activities with backend activities instead of replacing
      const backendActivities = activitiesData.activities || [];
      const mergedActivities = [...demoActivities, ...backendActivities].slice(0, 25); // Keep last 25
      setActivities(mergedActivities);
      
      setAtRiskCustomers(customersData.customers);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setIsLoading(false);
    }
  };

  const addTemporaryActivity = (activity) => {
    // Add to demo activities to persist across refreshes
    setDemoActivities(prev => {
      const newDemoActivities = [activity, ...prev].slice(0, 15); // Keep last 15 demo activities
      return newDemoActivities;
    });
    
    // Also update main activities for immediate display
    setActivities(prev => [activity, ...prev.slice(0, 24)]);
  };

  const addCustomerSaveActivity = (customer) => {
    const saveActivity = {
      id: `save-${Date.now()}`,
      type: 'customer_saved',
      title: `✅ CUSTOMER SAVED: ${customer.name} (${customer.company})`,
      description: `Successful intervention • Churn risk: ${(customer.churn_probability * 100).toFixed(0)}% → 23% • $${(customer.annual_contract_value/1000).toFixed(0)}K revenue retained`,
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
      title: '🔄 Self-correction: Email bounced → Phone call successful',
      description: 'Agent adapted strategy automatically • Customer engagement improved',
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
      // Show immediate TiDB-powered feedback
      addTemporaryActivity({
        id: `tidb-scan-${Date.now()}`,
        type: 'tidb_vector_search',
        title: '🔍 TiDB Vector Search: Scanning 768-dimensional customer embeddings...',
        description: 'Analyzing behavior patterns using cosine similarity • Processing 1,247 customer profiles',
        status: 'executing',
        urgency: 'high',
        timestamp: 'Now',
        metadata: { embeddings_processing: 1247, search_type: 'vector' }
      });

      // Show agent memory recall
      setTimeout(() => {
        addTemporaryActivity({
          id: `memory-${Date.now()}`,
          type: 'agent_memory_recall',
          title: '🧠 Agent Memory: Found 3 similar successful interventions',
          description: 'Retrieved memories from 2 weeks ago • Same segment, 91% churn risk → 89% success rate',
          status: 'success',
          urgency: 'medium',
          timestamp: 'Just now',
          metadata: { memories_found: 3, avg_success_rate: 0.89 }
        });
      }, 1500);

      // Show full-text analysis
      setTimeout(() => {
        addTemporaryActivity({
          id: `fulltext-${Date.now()}`,
          type: 'communication_analysis',
          title: '📝 Communication Analysis: Detected frustration patterns',
          description: 'TiDB full-text search through 247 messages • Negative sentiment detected • Key issue: billing complexity',
          status: 'warning',
          urgency: 'high',
          timestamp: 'Just now',
          metadata: { messages_analyzed: 247, sentiment: -0.7 }
        });
      }, 2500);

      await apiService.triggerAgent();
      
      // Customer save simulation
      setTimeout(() => {
        const customerToSave = atRiskCustomers[Math.floor(Math.random() * Math.min(3, atRiskCustomers.length))];
        if (customerToSave) {
          addCustomerSaveActivity(customerToSave);
          setSaveCounter(prev => prev + 1);
        }
      }, 3500);

      // Self-correction simulation
      setTimeout(() => {
        addSelfCorrectionActivity();
      }, 4500);

      setTimeout(() => {
        fetchDashboardData(); // This will now merge instead of replace
        setIsAgentRunning(false);
      }, 6000);

    } catch (error) {
      console.error('Failed to trigger agent:', error);
      setIsAgentRunning(false);
    }
  };

  // Clear demo activities function (optional - for testing)
  const clearDemoActivities = () => {
    setDemoActivities([]);
    fetchDashboardData();
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

      {/* TiDB Features Demo Section */}
      <TiDBFeaturesPanel />

      {/* Main Content */}
      <div className="main-content">
        {/* Live Activity Feed */}
        <div className="activity-section">
          <div className="section-header">
            <h2>🚨 Live Customer Rescue Operations</h2>
            <div className="activity-status">
              <div className={`status-dot ${isAgentRunning ? 'running' : 'active'} pulse`}></div>
              <span>{isAgentRunning ? 'Processing...' : 'Real-time'}</span>
              {/* Optional: Add clear button for testing */}
              {demoActivities.length > 0 && (
                <button 
                  className="clear-demo-btn"
                  onClick={clearDemoActivities}
                  style={{
                    marginLeft: '1rem',
                    padding: '0.25rem 0.5rem',
                    fontSize: '0.75rem',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Clear Demo ({demoActivities.length})
                </button>
              )}
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

        <div className="analytics-card tidb-status">
          <h3>🚀 TiDB Serverless Status</h3>
          <div className="tidb-metrics">
            <div className="tidb-metric">Vector Search: <span className="status-ok">Active • 47ms avg</span></div>
            <div className="tidb-metric">HTAP Processing: <span className="status-ok">1.2M ops/sec</span></div>
            <div className="tidb-metric">Churn Models: <span className="status-ok">Updated 2min ago</span></div>
            <div className="tidb-metric">Auto-scaling: <span className="status-ok">Optimized</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// TiDB Features Panel Component
const TiDBFeaturesPanel = () => {
  const [featuresData, setFeaturesData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const demonstrateTiDBFeatures = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getTiDBFeaturesDemo();
      setFeaturesData(response.tidb_features_demo);
    } catch (error) {
      console.error('Failed to fetch TiDB features demo:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tidb-features-panel">
      <div className="section-header">
        <h2>🚀 TiDB Serverless Features</h2>
        <button 
          className="demo-button"
          onClick={demonstrateTiDBFeatures}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader className="spin" size={16} />
              Loading...
            </>
          ) : (
            <>
              <Zap size={16} />
              Demo TiDB Features
            </>
          )}
        </button>
      </div>

      {featuresData && (
        <div className="features-grid">
          {/* Vector Search Demo */}
          <div className="feature-card vector-search">
            <div className="feature-header">
              <div className="feature-icon">🔍</div>
              <h3>Vector Search</h3>
              <div className="performance-badge">{featuresData.vector_search.query_time_ms}ms</div>
            </div>
            <p>{featuresData.vector_search.description}</p>
            <div className="feature-stats">
              <div className="stat">
                <span className="stat-value">{featuresData.vector_search.results_found}</span>
                <span className="stat-label">Agent Memories Found</span>
              </div>
            </div>
            {featuresData.vector_search.sample_memories?.length > 0 && (
              <div className="sample-data">
                <h4>Sample Memory:</h4>
                <div className="memory-item">
                  <span className="memory-type">
                    {featuresData.vector_search.sample_memories[0].interaction_type}
                  </span>
                  <span className="memory-outcome">
                    → {featuresData.vector_search.sample_memories[0].outcome}
                  </span>
                  <span className="similarity-score">
                    {(featuresData.vector_search.sample_memories[0].similarity_score * 100).toFixed(1)}% match
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Full-Text Search Demo */}
          <div className="feature-card fulltext-search">
            <div className="feature-header">
              <div className="feature-icon">📝</div>
              <h3>Full-Text Search</h3>
              <div className="performance-badge">Real-time</div>
            </div>
            <p>{featuresData.full_text_search.description}</p>
            <div className="feature-stats">
              <div className="stat">
                <span className="stat-value">{featuresData.full_text_search.results_found}</span>
                <span className="stat-label">Communications Found</span>
              </div>
            </div>
            {featuresData.full_text_search.sample_communications?.length > 0 && (
              <div className="sample-data">
                <h4>Recent Communication:</h4>
                <div className="comm-item">
                  <span className="comm-type">
                    {featuresData.full_text_search.sample_communications[0].communication_type}
                  </span>
                  <span className="comm-sentiment">
                    Sentiment: {featuresData.full_text_search.sample_communications[0].sentiment_score > 0 ? '😊' : '😞'}
                  </span>
                  <div className="comm-preview">
                    {featuresData.full_text_search.sample_communications[0].message_content.substring(0, 80)}...
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Graph RAG Demo */}
          <div className="feature-card graph-rag">
            <div className="feature-header">
              <div className="feature-icon">🕸️</div>
              <h3>Graph RAG</h3>
              <div className="performance-badge">Multi-hop</div>
            </div>
            <p>{featuresData.graph_rag.description}</p>
            <div className="feature-stats">
              <div className="stat">
                <span className="stat-value">{featuresData.graph_rag.direct_relationships}</span>
                <span className="stat-label">Direct Links</span>
              </div>
              <div className="stat">
                <span className="stat-value">{featuresData.graph_rag.similar_customers}</span>
                <span className="stat-label">Similar Profiles</span>
              </div>
              <div className="stat">
                <span className="stat-value">{featuresData.graph_rag.successful_strategies}</span>
                <span className="stat-label">Success Patterns</span>
              </div>
            </div>
          </div>

          {/* HTAP Processing Demo */}
          <div className="feature-card htap-processing">
            <div className="feature-header">
              <div className="feature-icon">⚡</div>
              <h3>HTAP Processing</h3>
              <div className="performance-badge">{featuresData.htap_processing.operations_per_second}</div>
            </div>
            <p>{featuresData.htap_processing.description}</p>
            <div className="feature-stats">
              <div className="stat">
                <span className="stat-value">{featuresData.htap_processing.response_time_ms}ms</span>
                <span className="stat-label">Response Time</span>
              </div>
              <div className="stat">
                <span className="stat-value">Auto</span>
                <span className="stat-label">Scaling</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!featuresData && !isLoading && (
        <div className="features-placeholder">
          <div className="placeholder-content">
            <div className="placeholder-icon">🚀</div>
            <h3>TiDB Serverless Features</h3>
            <p>Click "Demo TiDB Features" to see Vector Search, Full-Text Search, Graph RAG, and HTAP processing in action!</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Activity Item Component (same as before)
const ActivityItem = ({ activity }) => {
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    if (activity.timestamp === 'Now' || activity.timestamp === 'Just now') {
      setIsNew(true);
      setTimeout(() => setIsNew(false), 3000);
    }
  }, [activity.timestamp]);

  const getActivityIcon = (type, status) => {
    if (type === 'churn_intervention') {
      return <AlertTriangle className={`activity-icon ${status}`} size={20} />;
    } else if (type === 'customer_saved') {
      return <CheckCircle className="activity-icon success" size={20} />;
    } else if (type === 'self_correction') {
      return <Zap className="activity-icon warning" size={20} />;
    } else if (type === 'tidb_vector_search') {
      return <Bot className="activity-icon tidb_vector_search" size={20} />;
    } else if (type === 'agent_memory_recall') {
      return <Bot className="activity-icon agent_memory_recall" size={20} />;
    } else if (type === 'communication_analysis') {
      return <Bot className="activity-icon communication_analysis" size={20} />;
    } else if (type === 'graph_rag_analysis') {
      return <Bot className="activity-icon graph_rag_analysis" size={20} />;
    } else if (type === 'htap_processing') {
      return <Bot className="activity-icon htap_processing" size={20} />;
    } else if (type === 'agent_triggered') {
      return <Bot className="activity-icon executing" size={20} />;
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
          {activity.metadata.churn_probability && (
            <span className="metadata-tag">
              Risk: {(activity.metadata.churn_probability * 100).toFixed(0)}%
            </span>
          )}
          {activity.metadata.revenue_saved && (
            <span className="metadata-tag revenue">
              ${(activity.metadata.revenue_saved / 1000).toFixed(0)}K saved
            </span>
          )}
          {activity.metadata.embeddings_processing && (
            <span className="metadata-tag vector">
              {activity.metadata.embeddings_processing} embeddings
            </span>
          )}
          {activity.metadata.memories_found && (
            <span className="metadata-tag memory">
              {activity.metadata.memories_found} memories
            </span>
          )}
          {activity.metadata.messages_analyzed && (
            <span className="metadata-tag fulltext">
              {activity.metadata.messages_analyzed} messages
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
