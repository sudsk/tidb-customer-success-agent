# backend/services/churn_predictor.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ChurnPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'days_since_signup', 'last_login_days_ago', 'support_tickets_count',
            'feature_usage_score', 'nps_score', 'payment_delays', 'monthly_revenue_log',
            'tickets_per_month', 'usage_trend', 'revenue_tier'
        ]
        self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial model with synthetic data for demo"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features
        X = np.random.rand(n_samples, len(self.feature_names))
        
        # Create realistic feature distributions
        X[:, 0] = np.random.exponential(200, n_samples)  # days_since_signup
        X[:, 1] = np.random.exponential(5, n_samples)    # last_login_days_ago  
        X[:, 2] = np.random.poisson(2, n_samples)        # support_tickets
        X[:, 3] = np.random.beta(2, 2, n_samples)        # feature_usage_score
        X[:, 4] = np.random.normal(7, 2, n_samples)      # nps_score
        X[:, 5] = np.random.poisson(0.5, n_samples)      # payment_delays
        
        # Create labels with realistic churn logic
        churn_probability = (
            0.1 * (X[:, 1] > 7) +      # Haven't logged in recently
            0.2 * (X[:, 4] < 6) +      # Low NPS
            0.15 * (X[:, 3] < 0.3) +   # Low usage
            0.15 * (X[:, 2] > 5) +     # Many support tickets
            0.1 * (X[:, 5] > 2)        # Payment delays
        )
        
        y = (churn_probability + np.random.normal(0, 0.1, n_samples)) > 0.4
        
        # Train model
        X_scaled = self.scaler.fit_transform(X)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        logger.info(f"Churn prediction model trained with {n_samples} samples")
    
    def predict_churn_probability(self, customer_data: Dict) -> float:
        """Predict churn probability for a customer"""
        try:
            features = self._extract_features(customer_data)
            features_scaled = self.scaler.transform([features])
            
            # Get probability of churn (class 1)
            probability = self.model.predict_proba(features_scaled)[0, 1]
            return float(np.clip(probability, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return 0.5  # Default moderate risk
    
    def _extract_features(self, customer_data: Dict) -> List[float]:
        """Extract features from customer data"""
        features = []
        
        # Basic features
        features.append(customer_data.get('days_since_signup', 0))
        features.append(customer_data.get('last_login_days_ago', 0))
        features.append(customer_data.get('support_tickets_count', 0))
        features.append(customer_data.get('feature_usage_score', 0.5))
        features.append(customer_data.get('nps_score', 7))
        features.append(customer_data.get('payment_delays', 0))
        
        # Derived features
        monthly_revenue = customer_data.get('monthly_revenue', 100)
        features.append(np.log1p(monthly_revenue))  # log revenue
        
        days_active = max(customer_data.get('days_since_signup', 1), 1)
        tickets_per_month = customer_data.get('support_tickets_count', 0) * 30 / days_active
        features.append(tickets_per_month)
        
        # Usage trend (mock - in real system would calculate from time series)
        usage_trend = customer_data.get('feature_usage_score', 0.5) - 0.5
        features.append(usage_trend)
        
        # Revenue tier (0=low, 1=medium, 2=high)
        if monthly_revenue < 50:
            revenue_tier = 0
        elif monthly_revenue < 500:
            revenue_tier = 1
        else:
            revenue_tier = 2
        features.append(revenue_tier)
        
        return features
    
    def get_churn_risk_level(self, churn_probability: float) -> str:
        """Convert probability to risk level"""
        if churn_probability >= 0.8:
            return "critical"
        elif churn_probability >= 0.6:
            return "high"
        elif churn_probability >= 0.4:
            return "medium"
        else:
            return "low"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.model:
            return {}
        
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_names, importance_scores))
