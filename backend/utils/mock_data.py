# backend/utils/mock_data.py
import json
import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.database import Customer, RetentionPattern, ChurnIntervention
import logging

logger = logging.getLogger(__name__)

async def initialize_customer_data(db: Session):
    """Initialize comprehensive customer data for demo"""
    
    # Check if data already exists
    existing_customers = db.query(Customer).count()
    if existing_customers > 0:
        logger.info("Customer data already exists, skipping initialization")
        return
    
    logger.info("🚀 Initializing customer success agent data...")
    
    # Sample customer data with realistic churn indicators
    customers_data = [
        # High-risk customers (demonstration targets)
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@techstart.com",
            "company": "TechStart Inc",
            "subscription_plan": "pro",
            "monthly_revenue": 1200,
            "annual_contract_value": 14400,
            "days_since_signup": 180,
            "last_login_days_ago": 12,  # Haven't logged in recently
            "support_tickets_count": 8,  # High support burden
            "feature_usage_score": 0.3,  # Low usage
            "nps_score": 5,  # Low satisfaction
            "payment_delays": 1,
            "phone": "+1-555-0201",
            "timezone": "America/Los_Angeles",
            "preferred_contact": "email"
        },
        {
            "name": "Mike Rodriguez",
            "email": "mike@growthcorp.com",
            "company": "GrowthCorp",
            "subscription_plan": "enterprise",
            "monthly_revenue": 4500,
            "annual_contract_value": 54000,
            "days_since_signup": 90,
            "last_login_days_ago": 8,
            "support_tickets_count": 12,
            "feature_usage_score": 0.25,  # Very low usage
            "nps_score": 4,  # Very dissatisfied
            "payment_delays": 2,
            "phone": "+1-555-0202",
            "timezone": "America/New_York", 
            "preferred_contact": "phone"
        },
        {
            "name": "Jennifer Walsh",
            "email": "j.walsh@innovateplus.com",
            "company": "InnovatePlus",
            "subscription_plan": "pro",
            "monthly_revenue": 800,
            "annual_contract_value": 9600,
            "days_since_signup": 45,
            "last_login_days_ago": 15,  # Very inactive
            "support_tickets_count": 6,
            "feature_usage_score": 0.2,
            "nps_score": 6,
            "payment_delays": 0,
            "phone": "+1-555-0203",
            "timezone": "America/Chicago",
            "preferred_contact": "email"
        },
        
        # Medium-risk customers
        {
            "name": "David Park",
            "email": "david@nexustech.com", 
            "company": "Nexus Technologies",
            "subscription_plan": "basic",
            "monthly_revenue": 299,
            "annual_contract_value": 3588,
            "days_since_signup": 120,
            "last_login_days_ago": 5,
            "support_tickets_count": 3,
            "feature_usage_score": 0.6,
            "nps_score": 7,
            "payment_delays": 0,
            "phone": "+1-555-0204",
            "timezone": "America/Los_Angeles",
            "preferred_contact": "email"
        },
        {
            "name": "Lisa Thompson",
            "email": "lisa@fasttrack.com",
            "company": "FastTrack Solutions",
            "subscription_plan": "pro",
            "monthly_revenue": 1500,
            "annual_contract_value": 18000,
            "days_since_signup": 200,
            "last_login_days_ago": 3,
            "support_tickets_count": 2,
            "feature_usage_score": 0.55,
            "nps_score": 6,  # Somewhat dissatisfied 
            "payment_delays": 1,
            "phone": "+1-555-0205",
            "timezone": "America/New_York",
            "preferred_contact": "phone"
        },
        
        # Low-risk customers (healthy accounts)
        {
            "name": "Alex Kumar",
            "email": "alex@scalevision.com",
            "company": "ScaleVision Inc",
            "subscription_plan": "enterprise",
            "monthly_revenue": 8900,
            "annual_contract_value": 106800,
            "days_since_signup": 300,
            "last_login_days_ago": 1,
            "support_tickets_count": 1,
            "feature_usage_score": 0.9,
            "nps_score": 9,
            "payment_delays": 0,
            "phone": "+1-555-0206",
            "timezone": "America/Los_Angeles", 
            "preferred_contact": "email"
        },
        {
            "name": "Rachel Green",
            "email": "rachel@brightfuture.com",
            "company": "BrightFuture Corp",
            "subscription_plan": "pro",
            "monthly_revenue": 2200,
            "annual_contract_value": 26400,
            "days_since_signup": 150,
            "last_login_days_ago": 1,
            "support_tickets_count": 0,
            "feature_usage_score": 0.8,
            "nps_score": 8,
            "payment_delays": 0,
            "phone": "+1-555-0207",
            "timezone": "America/New_York",
            "preferred_contact": "email"
        },
        {
            "name": "Tom Wilson",
            "email": "tom@dynamictech.com",
            "company": "Dynamic Tech",
            "subscription_plan": "basic",
            "monthly_revenue": 199,
            "annual_contract_value": 2388,
            "days_since_signup": 60,
            "last_login_days_ago": 2,
            "support_tickets_count": 1,
            "feature_usage_score": 0.7,
            "nps_score": 8,
            "payment_delays": 0,
            "phone": "+1-555-0208",
            "timezone": "America/Chicago",
            "preferred_contact": "email"
        },

        # Additional customers for realistic dataset
        {
            "name": "Emma Davis",
            "email": "emma@cloudstream.com",
            "company": "CloudStream",
            "subscription_plan": "enterprise",
            "monthly_revenue": 5600,
            "annual_contract_value": 67200,
            "days_since_signup": 400,
            "last_login_days_ago": 7,  # Moderate risk
            "support_tickets_count": 4,
            "feature_usage_score": 0.4,
            "nps_score": 6,
            "payment_delays": 1,
            "phone": "+1-555-0209",
            "timezone": "America/Los_Angeles",
            "preferred_contact": "phone"
        },
        {
            "name": "James Miller",
            "email": "james@pivotcorp.com", 
            "company": "Pivot Corporation",
            "subscription_plan": "pro",
            "monthly_revenue": 999,
            "annual_contract_value": 11988,
            "days_since_signup": 75,
            "last_login_days_ago": 4,
            "support_tickets_count": 2,
            "feature_usage_score": 0.65,
            "nps_score": 7,
            "payment_delays": 0,
            "phone": "+1-555-0210",
            "timezone": "America/New_York",
            "preferred_contact": "email"
        }
    ]
    
    # Create customers with churn predictions
    from services.churn_predictor import ChurnPredictor
    churn_predictor = ChurnPredictor()
    
    for customer_data in customers_data:
        # Generate behavior embedding
        customer_data['behavior_embedding'] = generate_customer_embedding(customer_data)
        customer_data['usage_patterns'] = generate_usage_patterns(customer_data)
        
        # Predict churn probability
        churn_prob = churn_predictor.predict_churn_probability(customer_data)
        customer_data['churn_probability'] = churn_prob
        customer_data['churn_risk_level'] = churn_predictor.get_churn_risk_level(churn_prob)
        
        customer = Customer(**customer_data)
        db.add(customer)
    
    # Sample retention patterns
    retention_patterns = [
        {
            "pattern_name": "enterprise_retention_call",
            "customer_characteristics": json.dumps({
                "segment": "enterprise",
                "avg_revenue": 50000,
                "avg_usage_score": 0.6,
                "avg_nps": 6
            }),
            "successful_interventions": json.dumps(["executive_outreach", "custom_training", "account_review"]),
            "success_rate": 0.84,
            "customer_segment": "enterprise",
            "churn_reason_category": "satisfaction_issues",
            "embedding": generate_pattern_embedding("enterprise_success_call")
        },
        {
            "pattern_name": "smb_discount_offer",
            "customer_characteristics": json.dumps({
                "segment": "smb", 
                "avg_revenue": 8000,
                "avg_usage_score": 0.4,
                "avg_nps": 5
            }),
            "successful_interventions": json.dumps(["discount_offer", "payment_plan", "feature_demo"]),
            "success_rate": 0.71,
            "customer_segment": "smb",
            "churn_reason_category": "pricing_concerns",
            "embedding": generate_pattern_embedding("smb_discount_offer")
        },
        {
            "pattern_name": "mid_market_feature_adoption",
            "customer_characteristics": json.dumps({
                "segment": "mid_market",
                "avg_revenue": 25000,
                "avg_usage_score": 0.3,
                "avg_nps": 6
            }),
            "successful_interventions": json.dumps(["feature_demo", "training_session", "success_call"]),
            "success_rate": 0.78,
            "customer_segment": "mid_market", 
            "churn_reason_category": "underutilization",
            "embedding": generate_pattern_embedding("mid_market_feature_adoption")
        },
        {
            "pattern_name": "enterprise_support_escalation",
            "customer_characteristics": json.dumps({
                "segment": "enterprise",
                "avg_revenue": 75000,
                "avg_usage_score": 0.7,
                "avg_nps": 4
            }),
            "successful_interventions": json.dumps(["support_escalation", "dedicated_csm", "executive_review"]),
            "success_rate": 0.89,
            "customer_segment": "enterprise",
            "churn_reason_category": "support_issues", 
            "embedding": generate_pattern_embedding("enterprise_support_escalation")
        }
    ]
    
    # Create retention patterns
    for pattern_data in retention_patterns:
        pattern = RetentionPattern(**pattern_data)
        db.add(pattern)
    
    # Sample historical interventions (for learning)
    historical_interventions = [
        {
            "customer_id": 1,  # Sarah Chen - will be created with ID 1
            "intervention_type": "retention_outreach",
            "churn_probability_before": 0.89,
            "churn_probability_after": 0.34,
            "trigger_reason": "Low usage and high support tickets",
            "strategy_chosen": "personalized_success_call",
            "confidence_score": 0.82,
            "expected_success_rate": 0.75,
            "status": "successful",
            "revenue_at_risk": 14400,
            "estimated_retention_value": 10800,
            "actual_outcome": "retained",
            "execution_steps": json.dumps([
                {"type": "personalized_outreach", "method": "email", "status": "success"},
                {"type": "schedule_call", "urgency": "high", "status": "success"},
                {"type": "feature_demo", "focus": "underutilized_features", "status": "success"}
            ]),
            "created_at": datetime.now() - timedelta(days=2),
            "completed_at": datetime.now() - timedelta(days=1, hours=12)
        }
    ]
    
    # Create historical interventions
    for intervention_data in historical_interventions:
        intervention = ChurnIntervention(**intervention_data)
        db.add(intervention)
    
    # Commit all data
    db.commit()
    
    logger.info(f"✅ Initialized {len(customers_data)} customers, {len(retention_patterns)} patterns, and {len(historical_interventions)} historical interventions")

    await create_tidb_enhanced_tables(db)

def generate_customer_embedding(customer_data: dict) -> list:
    """Generate realistic customer behavior embedding"""
    
    # Seed for consistency
    seed_value = hash(customer_data['email']) % 2**32
    np.random.seed(seed_value)
    
    embedding = [0.0] * 768
    
    # Encode customer characteristics into embedding
    # Revenue dimension
    revenue_normalized = min(customer_data['monthly_revenue'] / 5000, 1.0)
    embedding[0] = revenue_normalized
    
    # Usage dimension
    embedding[1] = customer_data['feature_usage_score']
    
    # Satisfaction dimension  
    embedding[2] = customer_data['nps_score'] / 10.0
    
    # Support burden dimension
    support_normalized = min(customer_data['support_tickets_count'] / 10, 1.0)
    embedding[3] = support_normalized
    
    # Engagement dimension (inverse of days since last login)
    engagement = max(0, 1 - (customer_data['last_login_days_ago'] / 30))
    embedding[4] = engagement
    
    # Subscription tier dimension
    if customer_data['subscription_plan'] == 'basic':
        tier_score = 0.3
    elif customer_data['subscription_plan'] == 'pro':
        tier_score = 0.7
    else:  # enterprise
        tier_score = 1.0
    embedding[5] = tier_score
    
    # Fill remaining dimensions with correlated noise
    for i in range(6, 768):
        base_value = (embedding[i % 6] - 0.5) * 0.3  # Correlate with existing dimensions
        noise = np.random.normal(0, 0.15)
        embedding[i] = np.clip(base_value + noise, -1, 1)
    
    return embedding


def generate_usage_patterns(customer_data: dict) -> dict:
    """Generate realistic usage patterns for customer"""
    
    usage_score = customer_data['feature_usage_score']
    
    patterns = {
        "daily_logins": max(0, int(7 * usage_score * (1 + np.random.normal(0, 0.3)))),
        "features_used": max(1, int(20 * usage_score * (1 + np.random.normal(0, 0.2)))),
        "time_spent_minutes": max(10, int(180 * usage_score * (1 + np.random.normal(0, 0.4)))),
        "advanced_features_adopted": max(0, int(5 * usage_score * usage_score)),  # Quadratic for advanced features
        "integration_usage": usage_score > 0.6,  # Only high-usage customers use integrations
        "mobile_usage_ratio": min(1.0, usage_score + np.random.normal(0, 0.2)),
        "weekend_activity": usage_score > 0.7  # Only very engaged users work weekends
    }
    
    return patterns


def generate_pattern_embedding(pattern_type: str) -> list:
    """Generate embedding for retention pattern"""
    
    # Seed based on pattern type for consistency
    np.random.seed(hash(pattern_type) % 2**32)
    
    embedding = [0.0] * 768
    
    # Set characteristic dimensions based on pattern type
    if "enterprise" in pattern_type:
        embedding[0] = 0.9  # High revenue
        embedding[5] = 1.0  # Enterprise tier
    elif "smb" in pattern_type:
        embedding[0] = 0.3  # Lower revenue
        embedding[5] = 0.3  # Basic tier
    else:  # mid_market
        embedding[0] = 0.6  # Medium revenue
        embedding[5] = 0.7  # Pro tier
    
    if "discount" in pattern_type:
        embedding[10] = 0.8  # Price sensitivity
    elif "feature" in pattern_type:
        embedding[11] = 0.8  # Feature focus
    elif "support" in pattern_type:
        embedding[12] = 0.8  # Support issues
    
    # Fill remaining dimensions
    for i in range(13, 768):
        embedding[i] = np.random.normal(0, 0.1)
    
    return embedding

async def create_tidb_enhanced_tables(db: Session):
    """Create new TiDB enhanced tables and populate demo data"""
    
    try:
        # Create tables using raw SQL
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                customer_id INT NOT NULL,
                interaction_type VARCHAR(100) NOT NULL,
                context JSON NOT NULL,
                outcome VARCHAR(100) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                embedding JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_customer_type (customer_id, interaction_type),
                INDEX idx_session (session_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customer_communications (
                communication_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                message_content TEXT NOT NULL,
                communication_type VARCHAR(50) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sentiment_score FLOAT DEFAULT 0.0,
                communication_direction VARCHAR(20) DEFAULT 'inbound',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_customer_time (customer_id, timestamp)
            )
            """
        ]
        
        # Execute table creation
        for sql in create_tables_sql:
            db.execute(text(sql))
        
        db.commit()
        logger.info("✅ Enhanced TiDB tables created")
        
        # Add sample communications for demo
        sample_communications = [
            {
                "customer_id": 1,  # Sarah Chen
                "message_content": "I'm really frustrated with the billing system. It's so confusing and I can't understand my charges. Considering switching to your competitor.",
                "communication_type": "email",
                "communication_direction": "inbound",
                "sentiment_score": -0.7
            },
            {
                "customer_id": 1,
                "message_content": "Support ticket #12345: Feature request - need better reporting dashboard. Current one is inadequate for our needs.",
                "communication_type": "support_ticket",
                "communication_direction": "inbound", 
                "sentiment_score": -0.3
            },
            {
                "customer_id": 2,  # Mike Rodriguez
                "message_content": "The new features are too complex for my team. We need simpler interface and better training materials.",
                "communication_type": "phone",
                "communication_direction": "inbound",
                "sentiment_score": -0.5
            },
            {
                "customer_id": 2,
                "message_content": "Meeting notes: Discussed contract renewal concerns. Price increase of 20% is significant burden for our budget.",
                "communication_type": "meeting",
                "communication_direction": "inbound",
                "sentiment_score": -0.4
            }
        ]
        
        # Insert communications
        for comm in sample_communications:
            insert_sql = text("""
                INSERT INTO customer_communications 
                (customer_id, message_content, communication_type, communication_direction, sentiment_score)
                VALUES (:customer_id, :message_content, :communication_type, :communication_direction, :sentiment_score)
            """)
            db.execute(insert_sql, comm)
        
        # Add sample agent memories
        sample_memories = [
            {
                "session_id": "memory_001",
                "customer_id": 1,
                "interaction_type": "churn_intervention",
                "context": json.dumps({
                    "segment": "smb",
                    "issue": "billing_confusion",
                    "strategy": "personalized_billing_walkthrough",
                    "original_churn_prob": 0.89
                }),
                "outcome": "successful",
                "embedding": json.dumps([0.1, 0.2, 0.3] + [0.0] * 765)  # Mock embedding
            },
            {
                "session_id": "memory_002", 
                "customer_id": 2,
                "interaction_type": "churn_intervention",
                "context": json.dumps({
                    "segment": "enterprise",
                    "issue": "feature_complexity",
                    "strategy": "dedicated_training_session",
                    "original_churn_prob": 0.91
                }),
                "outcome": "successful",
                "embedding": json.dumps([0.2, 0.4, 0.1] + [0.0] * 765)  # Mock embedding
            }
        ]
        
        # Insert memories
        for memory in sample_memories:
            insert_sql = text("""
                INSERT INTO agent_memory 
                (session_id, customer_id, interaction_type, context, outcome, embedding)
                VALUES (:session_id, :customer_id, :interaction_type, :context, :outcome, :embedding)
            """)
            db.execute(insert_sql, memory)
        
        db.commit()
        logger.info("✅ Enhanced demo data populated")
        
    except Exception as e:
        logger.error(f"Error creating enhanced tables: {e}")
        db.rollback()
