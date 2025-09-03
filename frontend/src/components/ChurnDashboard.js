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
    
      {/* Header */}
      
        
          
            
              
            
            
              Customer Success Agent
              Autonomous AI that saves customers from churn • TiDB Serverless
            
          
          
          
            
              {saveCounter}
              Customers Saved
            
            
              
              Agent Monitoring
            
            
              
              Save Customers Now
            
          
        
      

      {/* KPI Cards */}
      
        
          
            
            +73 this week
          
          {metrics?.kpis?.customers_saved?.value || 0}
          Customers Saved
          From high-risk churn situations
        

        
          
            
            {metrics?.kpis?.revenue_retained?.change}
          
          ${(metrics?.kpis?.revenue_retained?.value / 1000000).toFixed(1)}M
          Revenue Retained
          Monthly recurring revenue saved
        

        
          
            
            {metrics?.kpis?.churn_reduction?.change}
          
          {metrics?.kpis?.churn_reduction?.value}%
          Churn Rate Reduction
          Dramatic improvement in retention
        

        
          
            
            {metrics?.kpis?.agent_autonomy?.change}
          
          {metrics?.kpis?.agent_autonomy?.value}%
          Agent Autonomy
          Fully autonomous interventions
        
      

      {/* Main Content */}
      
        {/* Live Activity Feed */}
        
          
            🚨 Live Customer Rescue Operations
            
              
              Real-time
            
          
          
          
            {activities.map((activity, index) => (
              
            ))}
          
        

        {/* At-Risk Customers */}
        
          
            ⚠️ Customers at Risk
            {atRiskCustomers.length} high-risk
          
          
          
            {atRiskCustomers.slice(0, 8).map(customer => (
              
            ))}
          
        
      

      {/* Bottom Analytics */}
      
        
          📊 Churn Risk Distribution
          
            
              Critical Risk
              
                {metrics?.churn_risk_summary?.churn_distribution?.critical?.count || 0}
              
              
                ${(metrics?.churn_risk_summary?.churn_distribution?.critical?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              
            
            
              High Risk
              
                {metrics?.churn_risk_summary?.churn_distribution?.high?.count || 0}
              
              
                ${(metrics?.churn_risk_summary?.churn_distribution?.high?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              
            
            
              Medium Risk
              
                {metrics?.churn_risk_summary?.churn_distribution?.medium?.count || 0}
              
              
                ${(metrics?.churn_risk_summary?.churn_distribution?.medium?.total_at_risk / 1000 || 0).toFixed(0)}K at risk
              
            
          
        

        
          🤖 Agent Performance
          
            
              Response Time:
              {metrics?.agent_performance?.avg_response_time_minutes?.toFixed(0) || 0}s
            
            
              Customers Processed (24h):
              {metrics?.agent_performance?.customers_processed_24h || 0}
            
            
              Critical Interventions:
              {metrics?.agent_performance?.critical_interventions_24h || 0}
            
          
        

        
          🚀 TiDB Serverless Status
          
            Vector Search: Active
            HTAP Processing: 1.2M ops/sec
            Churn Models: Updated 2min ago
            Auto-scaling: Optimized
          
        
      
    
  );
};

const ActivityItem = ({ activity }) => {
  const getActivityIcon = (type, status) => {
    if (type === 'churn_intervention') {
      return ;
    } else if (type === 'customer_saved') {
      return ;
    } else if (type === 'self_correction') {
      return ;
    } else {
      return ;
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
    
      
        {getActivityIcon(activity.type, activity.status)}
        
          {activity.title}
          {activity.description}
        
        {activity.timestamp}
      
      
      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
        
          {activity.metadata.churn_probability && (
            
              Risk: {(activity.metadata.churn_probability * 100).toFixed(0)}%
            
          )}
          {activity.metadata.revenue_at_risk && (
            
              ${(activity.metadata.revenue_at_risk / 1000).toFixed(0)}K at risk
            
          )}
        
      )}
    
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
      
        
          {customer.name}
          {customer.company}
        
        
          {(customer.churn_probability * 100).toFixed(0)}%
        
      
      
      
        
          Revenue:
          ${(customer.annual_contract_value / 1000).toFixed(0)}K
        
        
          Last Login:
          {customer.last_login_days_ago}d ago
        
        
          Usage Score:
          {(customer.feature_usage_score * 100).toFixed(0)}%
        
      
    
  );
};

export default ChurnDashboard;
