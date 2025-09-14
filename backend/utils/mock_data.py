# backend/utils/mock_data.py
import json
import random
import numpy as np
import hashlib
import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import (
    Customer, RetentionPattern, ChurnIntervention, AgentActivity, 
    AgentMemory, CustomerCommunication
)
import logging

logger = logging.getLogger(__name__)

def generate_semantic_embedding(text: str, dimension: int = 768) -> list:
    """Generate consistent, meaningful embeddings for mock data"""
    # Create deterministic hash-based seed
    text_hash = hashlib.md5(text.encode()).hexdigest()
    seed = int(text_hash[:8], 16)
    
    # Generate base random embedding
    def next_random(seed):
        return (seed * 1664525 + 1013904223) % (2**32)
    
    embedding = []
    current_seed = seed
    
    for i in range(dimension):
        current_seed = next_random(current_seed)
        val = (current_seed / (2**32 - 1)) * 2 - 1  # [-1, 1] range
        embedding.append(val)
    
    # Add semantic meaning
    text_lower = text.lower()
    
    # Segment-based features (dimensions 0-50)
    if 'enterprise' in text_lower:
        for i in range(min(50, dimension)):
            embedding[i] += 0.4
    elif 'pro' in text_lower:
        for i in range(min(50, dimension)):
            embedding[i] += 0.2
    elif 'basic' in text_lower:
        for i in range(min(50, dimension)):
            embedding[i] -= 0.1
    
    # Risk-based features (dimensions 50-100)
    if any(risk in text_lower for risk in ['critical', 'high_risk', '0.9', '0.8']):
        for i in range(50, min(100, dimension)):
            embedding[i] += 0.6
    elif 'medium_risk' in text_lower:
        for i in range(50, min(100, dimension)):
            embedding[i] += 0.3
    
    # Usage-based features (dimensions 100-150)
    if 'low_usage' in text_lower or 'underutilization' in text_lower:
        for i in range(100, min(150, dimension)):
            embedding[i] += 0.5
    
    # Support-based features (dimensions 150-200)
    if any(support in text_lower for support in ['support', 'tickets', 'billing']):
        for i in range(150, min(200, dimension)):
            embedding[i] += 0.4
    
    # Normalize to unit vector
    magnitude = math.sqrt(sum(x * x for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding

async def reset_all_demo_data(db: Session):
    """Complete database reset for demo - truncate and reload all tables"""
    
    logger.info("🔄 Starting complete demo data reset...")
    
    try:
        # Truncate all tables in correct order (respecting foreign keys)
        tables_to_truncate = [
            'agent_activities',
            'churn_interventions', 
            'customer_communications',
            'agent_memory',
            'retention_patterns',
            'customers'
        ]
        
        for table in tables_to_truncate:
            try:
                db.execute(text(f"DELETE FROM {table}"))
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.warning(f"Could not clear {table}: {e}")
        
        # Reload all data
        await load_customers(db)
        await load_retention_patterns(db) 
        await load_agent_memory(db)
        await load_customer_communications(db)
        await load_historical_interventions(db)
        
        db.commit()
        logger.info("✅ Complete demo data reset successful")
        
    except Exception as e:
        logger.error(f"Error in demo data reset: {e}")
        db.rollback()
        raise

async def load_customers(db: Session):
    """Load realistic customer data with proper churn probabilities"""
    
    customers_data = [
        # High-risk customers for impressive demos
        {
            "name": "Marcus Crisis",
            "email": "marcus@crisis-corp.com", 
            "company": "Crisis Corporation",
            "subscription_plan": "enterprise",
            "monthly_revenue": 7500,
            "annual_contract_value": 90000,
            "days_since_signup": 120,
            "last_login_days_ago": 18,
            "support_tickets_count": 15,
            "feature_usage_score": 0.15,
            "nps_score": 3,
            "payment_delays": 2,
            "churn_probability": 0.94,
            "churn_risk_level": "critical",
            "phone": "+1-555-0999",
            "timezone": "America/New_York",
            "preferred_contact": "phone"
        },
        {
            "name": "Diana Emergency",
            "email": "diana@urgent-solutions.com",
            "company": "Urgent Solutions Ltd", 
            "subscription_plan": "pro",
            "monthly_revenue": 3200,
            "annual_contract_value": 38400,
            "days_since_signup": 90,
            "last_login_days_ago": 21,
            "support_tickets_count": 12,
            "feature_usage_score": 0.18,
            "nps_score": 4,
            "payment_delays": 3,
            "churn_probability": 0.91,
            "churn_risk_level": "critical",
            "phone": "+1-555-0888",
            "timezone": "America/Los_Angeles", 
            "preferred_contact": "email"
        },
        {
            "name": "Mike Rodriguez",
            "email": "mike@struggletech.com",
            "company": "StruggleTech Inc",
            "subscription_plan": "enterprise",
            "monthly_revenue": 5200,
            "annual_contract_value": 62400,
            "days_since_signup": 200,
            "last_login_days_ago": 14,
            "support_tickets_count": 18,
            "feature_usage_score": 0.22,
            "nps_score": 3,
            "payment_delays": 2,
            "churn_probability": 0.89,
            "churn_risk_level": "critical",
            "phone": "+1-555-0777",
            "timezone": "America/Chicago",
            "preferred_contact": "email"
        },
        
        # Medium-risk customers
        {
            "name": "Sarah Johnson",
            "email": "sarah@midmarket.com",
            "company": "MidMarket Solutions",
            "subscription_plan": "pro", 
            "monthly_revenue": 2800,
            "annual_contract_value": 33600,
            "days_since_signup": 150,
            "last_login_days_ago": 8,
            "support_tickets_count": 6,
            "feature_usage_score": 0.45,
            "nps_score": 6,
            "payment_delays": 1,
            "churn_probability": 0.67,
            "churn_risk_level": "high",
            "phone": "+1-555-0666",
            "timezone": "America/New_York",
            "preferred_contact": "email"
        },
        {
            "name": "Robert Kim",
            "email": "robert@techventure.io",
            "company": "TechVenture Partners",
            "subscription_plan": "basic",
            "monthly_revenue": 1200,
            "annual_contract_value": 14400,
            "days_since_signup": 80,
            "last_login_days_ago": 6,
            "support_tickets_count": 4,
            "feature_usage_score": 0.52,
            "nps_score": 6,
            "payment_delays": 1,
            "churn_probability": 0.58,
            "churn_risk_level": "medium",
            "phone": "+1-555-0555",
            "timezone": "America/Los_Angeles",
            "preferred_contact": "phone"
        },
        
        # Healthy customers (for contrast)
        {
            "name": "Alex Chen",
            "email": "alex@successtech.com",
            "company": "SuccessTech Solutions",
            "subscription_plan": "enterprise",
            "monthly_revenue": 8900,
            "annual_contract_value": 106800,
            "days_since_signup": 300,
            "last_login_days_ago": 1,
            "support_tickets_count": 1,
            "feature_usage_score": 0.92,
            "nps_score": 9,
            "payment_delays": 0,
            "churn_probability": 0.15,
            "churn_risk_level": "low",
            "phone": "+1-555-0111",
            "timezone": "America/New_York",
            "preferred_contact": "email"
        },
        {
            "name": "Jennifer Walsh",
            "email": "jennifer@growthcorp.com", 
            "company": "GrowthCorp Industries",
            "subscription_plan": "pro",
            "monthly_revenue": 3500,
            "annual_contract_value": 42000,
            "days_since_signup": 250,
            "last_login_days_ago": 2,
            "support_tickets_count": 2,
            "feature_usage_score": 0.78,
            "nps_score": 8,
            "payment_delays": 0,
            "churn_probability": 0.28,
            "churn_risk_level": "low",
            "phone": "+1-555-0222", 
            "timezone": "America/Chicago",
            "preferred_contact": "email"
        }
    ]
    
    # Add more customers for realistic dataset
    additional_customers = []
    companies = [
        "DataFlow Inc", "CloudScale Corp", "TechPioneer Ltd", "InnovateNow Solutions",
        "NextGen Systems", "SmartBiz Technologies", "FutureForward Inc", "AgileWorks Corp",
        "DigitalEdge Solutions", "ScaleUp Technologies", "ModernTech Inc", "FlexiSoft Corp"
    ]
    
    plans = ["basic", "pro", "enterprise"]
    plan_revenues = {"basic": (500, 1500), "pro": (1500, 4000), "enterprise": (4000, 12000)}
    
    for i in range(len(additional_customers), 60):  # Total 67 customers
        plan = random.choice(plans)
        min_rev, max_rev = plan_revenues[plan]
        monthly_revenue = random.randint(min_rev, max_rev)
        
        # Generate realistic churn probability based on characteristics
        base_churn = random.uniform(0.1, 0.65)
        
        # Adjust based on usage and satisfaction
        feature_usage = random.uniform(0.1, 0.9)
        nps = random.randint(3, 10)
        support_tickets = random.randint(0, 12)
        last_login = random.randint(1, 25)
        
        # Calculate final churn probability
        churn_prob = base_churn
        if feature_usage < 0.3: churn_prob += 0.15
        if nps < 6: churn_prob += 0.10
        if support_tickets > 8: churn_prob += 0.08
        if last_login > 14: churn_prob += 0.12
        
        churn_prob = min(0.85, max(0.05, churn_prob))
        
        if churn_prob >= 0.8:
            risk_level = "critical"
        elif churn_prob >= 0.6:
            risk_level = "high"
        elif churn_prob >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        company = companies[i % len(companies)]
        customer = {
            "name": f"Customer {i+1}",
            "email": f"customer{i+1}@{company.lower().replace(' ', '').replace(',', '')}.com",
            "company": company,
            "subscription_plan": plan,
            "monthly_revenue": monthly_revenue,
            "annual_contract_value": monthly_revenue * 12,
            "days_since_signup": random.randint(30, 500),
            "last_login_days_ago": last_login,
            "support_tickets_count": support_tickets,
            "feature_usage_score": feature_usage,
            "nps_score": nps,
            "payment_delays": random.randint(0, 3),
            "churn_probability": churn_prob,
            "churn_risk_level": risk_level,
            "phone": f"+1-555-{1000 + i:04d}",
            "timezone": random.choice(["America/New_York", "America/Los_Angeles", "America/Chicago"]),
            "preferred_contact": random.choice(["email", "phone"])
        }
        additional_customers.append(customer)
    
    # Combine all customers
    all_customers = customers_data + additional_customers
    
    # Create customers with embeddings
    for customer_data in all_customers:
        # Generate behavior embedding based on customer characteristics
        customer_text = f"company:{customer_data['company']} segment:{customer_data['subscription_plan']} usage:{customer_data['feature_usage_score']:.2f} nps:{customer_data['nps_score']} risk:{customer_data['churn_probability']:.2f}"
        customer_data['behavior_embedding'] = json.dumps(generate_semantic_embedding(customer_text))
        customer_data['usage_patterns'] = json.dumps({
            "daily_logins": max(0, int(7 * customer_data['feature_usage_score'])),
            "features_used": max(1, int(15 * customer_data['feature_usage_score'])),
            "time_spent_minutes": max(10, int(120 * customer_data['feature_usage_score']))
        })
        
        customer = Customer(**customer_data)
        db.add(customer)
    
    logger.info(f"Added {len(all_customers)} customers to database")

async def load_retention_patterns(db: Session):
    """Load retention patterns with proper vector embeddings for similarity search"""
    
    patterns = [
        {
            "pattern_name": "enterprise_high_risk_billing_support",
            "customer_characteristics": json.dumps({
                "segment": "enterprise",
                "avg_revenue": 75000,
                "common_issues": ["billing_complexity", "invoice_questions", "payment_terms"],
                "avg_churn_probability": 0.85,
                "avg_support_tickets": 12
            }),
            "successful_interventions": json.dumps([
                "dedicated_billing_specialist",
                "executive_account_review", 
                "custom_payment_terms",
                "billing_system_training"
            ]),
            "success_rate": 0.89,
            "customer_segment": "enterprise",
            "churn_reason_category": "billing_complexity"
        },
        {
            "pattern_name": "pro_underutilization_training",
            "customer_characteristics": json.dumps({
                "segment": "pro",
                "avg_revenue": 30000,
                "common_issues": ["low_feature_usage", "training_needs", "complexity"],
                "avg_churn_probability": 0.72,
                "avg_usage_score": 0.25
            }),
            "successful_interventions": json.dumps([
                "personalized_training_session",
                "success_coaching",
                "simplified_workflow_setup",
                "feature_adoption_plan"
            ]),
            "success_rate": 0.76,
            "customer_segment": "pro", 
            "churn_reason_category": "underutilization"
        },
        {
            "pattern_name": "critical_risk_executive_escalation",
            "customer_characteristics": json.dumps({
                "segment": "enterprise",
                "avg_revenue": 85000,
                "common_issues": ["executive_concerns", "strategic_alignment", "contract_renewal"],
                "avg_churn_probability": 0.91,
                "avg_nps": 3
            }),
            "successful_interventions": json.dumps([
                "c_level_executive_call",
                "strategic_roadmap_alignment",
                "contract_renegotiation",
                "dedicated_success_manager"
            ]),
            "success_rate": 0.84,
            "customer_segment": "enterprise",
            "churn_reason_category": "strategic_misalignment"
        },
        {
            "pattern_name": "support_ticket_overload_resolution",
            "customer_characteristics": json.dumps({
                "segment": "pro",
                "avg_revenue": 35000,
                "common_issues": ["support_response_time", "ticket_volume", "technical_issues"],
                "avg_churn_probability": 0.78,
                "avg_support_tickets": 15
            }),
            "successful_interventions": json.dumps([
                "dedicated_support_engineer",
                "priority_support_queue",
                "technical_health_check",
                "proactive_monitoring"
            ]),
            "success_rate": 0.81,
            "customer_segment": "pro",
            "churn_reason_category": "support_issues"
        },
        {
            "pattern_name": "basic_pricing_sensitivity_discount",
            "customer_characteristics": json.dumps({
                "segment": "basic",
                "avg_revenue": 12000,
                "common_issues": ["pricing_concerns", "budget_constraints", "competitor_pricing"],
                "avg_churn_probability": 0.69,
                "avg_payment_delays": 2
            }),
            "successful_interventions": json.dumps([
                "loyalty_discount_offer",
                "flexible_payment_plan",
                "feature_value_demonstration",
                "competitive_analysis_presentation"
            ]),
            "success_rate": 0.71,
            "customer_segment": "basic",
            "churn_reason_category": "pricing_sensitivity"
        }
    ]
    
    # Generate embeddings for each pattern
    for pattern_data in patterns:
        # Create embedding based on pattern characteristics
        characteristics = json.loads(pattern_data["customer_characteristics"])
        pattern_text = f"segment:{pattern_data['customer_segment']} category:{pattern_data['churn_reason_category']} revenue:{characteristics.get('avg_revenue', 0)} success_rate:{pattern_data['success_rate']}"
        
        pattern_data["embedding"] = json.dumps(generate_semantic_embedding(pattern_text))
        pattern_data["graph_relationships"] = json.dumps({
            "related_patterns": [],
            "customer_count": random.randint(5, 25),
            "success_examples": random.randint(3, 15)
        })
        pattern_data["memory_references"] = json.dumps([])
        
        pattern = RetentionPattern(**pattern_data)
        db.add(pattern)
    
    logger.info(f"Added {len(patterns)} retention patterns with embeddings")

async def load_agent_memory(db: Session):
    """Load agent memory with embeddings for memory retrieval"""
    
    memories = [
        {
            "session_id": "mem_success_001",
            "customer_id": 1,  # Marcus Crisis
            "interaction_type": "churn_intervention",
            "context": json.dumps({
                "segment": "enterprise",
                "original_churn_probability": 0.94,
                "issue_category": "billing_complexity",
                "intervention_strategy": "executive_escalation",
                "success_factors": ["dedicated_billing_specialist", "c_level_call"],
                "timeline_days": 3
            }),
            "outcome": "successful"
        },
        {
            "session_id": "mem_success_002", 
            "customer_id": 2,  # Diana Emergency
            "interaction_type": "churn_intervention",
            "context": json.dumps({
                "segment": "pro",
                "original_churn_probability": 0.91,
                "issue_category": "underutilization",
                "intervention_strategy": "personalized_training",
                "success_factors": ["hands_on_training", "workflow_optimization"],
                "timeline_days": 5
            }),
            "outcome": "successful"
        },
        {
            "session_id": "mem_success_003",
            "customer_id": 3,  # Mike Rodriguez
            "interaction_type": "churn_intervention", 
            "context": json.dumps({
                "segment": "enterprise",
                "original_churn_probability": 0.89,
                "issue_category": "support_overload",
                "intervention_strategy": "dedicated_support_engineer",
                "success_factors": ["priority_queue", "technical_specialist"],
                "timeline_days": 2
            }),
            "outcome": "successful"
        }
    ]
    
    # Generate embeddings for memories
    for memory_data in memories:
        context = json.loads(memory_data["context"])
        memory_text = f"segment:{context['segment']} issue:{context['issue_category']} strategy:{context['intervention_strategy']} outcome:{memory_data['outcome']}"
        memory_data["embedding"] = json.dumps(generate_semantic_embedding(memory_text))
        
        memory = AgentMemory(**memory_data)
        db.add(memory)
    
    logger.info(f"Added {len(memories)} agent memories with embeddings")

async def load_customer_communications(db: Session):
    """Load customer communications for full-text search"""
    
    communications = [
        # Marcus Crisis communications (high frustration)
        {
            "customer_id": 1,
            "message_content": "I've been trying to understand our monthly invoice for weeks. The billing structure is completely opaque and our accounting team is frustrated. We're seriously considering switching to a competitor with clearer pricing.",
            "communication_type": "email",
            "communication_direction": "inbound",
            "sentiment_score": -0.7
        },
        {
            "customer_id": 1,
            "message_content": "Third escalation this month regarding billing discrepancies. This is impacting our budget planning and executive team confidence in your platform.",
            "communication_type": "support_ticket",
            "communication_direction": "inbound", 
            "sentiment_score": -0.8
        },
        
        # Diana Emergency communications (usage struggles)
        {
            "customer_id": 2,
            "message_content": "Our team is struggling to adopt the new features. The interface seems complex and we haven't seen the ROI we expected. Need help getting more value from our subscription.",
            "communication_type": "email",
            "communication_direction": "inbound",
            "sentiment_score": -0.5
        },
        {
            "customer_id": 2,
            "message_content": "Can we schedule training? Our feature utilization is low and management is questioning the investment. We want this to work but need guidance.",
            "communication_type": "chat",
            "communication_direction": "inbound",
            "sentiment_score": -0.3
        },
        
        # Mike Rodriguez communications (support issues)
        {
            "customer_id": 3,
            "message_content": "Support response times have been unacceptable lately. Critical issues taking 2-3 days for initial response. This is affecting our operations and customer satisfaction.",
            "communication_type": "email", 
            "communication_direction": "inbound",
            "sentiment_score": -0.8
        },
        {
            "customer_id": 3,
            "message_content": "Ticket #5647 escalation: System integration failing repeatedly. Our development team is spending too much time on workarounds instead of building features.",
            "communication_type": "support_ticket",
            "communication_direction": "inbound",
            "sentiment_score": -0.6
        }
    ]
    
    # Add more communications for other customers
    positive_messages = [
        "Really impressed with the recent feature updates. Exactly what our team needed for the new quarter.",
        "Your support team resolved our integration issue quickly and professionally. Great experience.",
        "Platform stability has been excellent. No downtime issues this month which is critical for us.",
        "The new dashboard makes reporting so much easier. Our executives love the insights.",
        "Training session was incredibly helpful. Team adoption has improved significantly."
    ]
    
    neutral_messages = [
        "Can you clarify the pricing for additional users? Planning our team expansion.",
        "What's the timeline for the mobile app improvements mentioned in your roadmap?",
        "Need documentation on the API rate limits for our integration project.",
        "Is there a volume discount available as we scale to 500+ users?",
        "When will the SSO integration be available? Important for our security compliance."
    ]
    
    # Add communications for other customers
    for customer_id in range(4, 8):  # Customers 4-7
        # Add 2-3 communications per customer
        for i in range(random.randint(2, 4)):
            if random.random() < 0.3:  # 30% negative
                message = f"Having some challenges with {random.choice(['setup', 'configuration', 'billing', 'features'])}. Could use some guidance."
                sentiment = random.uniform(-0.6, -0.2)
            elif random.random() < 0.7:  # 40% positive  
                message = random.choice(positive_messages)
                sentiment = random.uniform(0.3, 0.8)
            else:  # 30% neutral
                message = random.choice(neutral_messages)
                sentiment = random.uniform(-0.1, 0.1)
            
            communications.append({
                "customer_id": customer_id,
                "message_content": message,
                "communication_type": random.choice(["email", "chat", "support_ticket"]),
                "communication_direction": "inbound",
                "sentiment_score": sentiment
            })
    
    # Create communications
    for comm_data in communications:
        communication = CustomerCommunication(**comm_data)
        db.add(communication)
    
    logger.info(f"Added {len(communications)} customer communications")

async def load_historical_interventions(db: Session):
    """Load some historical successful interventions"""
    
    interventions = [
        {
            "customer_id": 6,  # Alex Chen (successful case)
            "intervention_type": "proactive_success_call",
            "churn_probability_before": 0.45,
            "churn_probability_after": 0.15,
            "trigger_reason": "Declining usage score detected",
            "strategy_chosen": "success_coaching_with_feature_training",
            "confidence_score": 0.82,
            "expected_success_rate": 0.78,
            "status": "successful",
            "revenue_at_risk": 106800,
            "estimated_retention_value": 83304,
            "actual_outcome": "retained",
            "execution_steps": json.dumps([
                {"type": "success_call", "status": "completed", "outcome": "positive"},
                {"type": "feature_training", "status": "completed", "outcome": "high_engagement"},
                {"type": "follow_up_check", "status": "completed", "outcome": "improved_usage"}
            ]),
            "outcome_details": json.dumps({
                "usage_improvement": "60% increase in feature adoption",
                "nps_improvement": "7 to 9 points",
                "engagement_score": "significantly improved"
            }),
            "created_at": datetime.now() - timedelta(days=30),
            "completed_at": datetime.now() - timedelta(days=25)
        },
        {
            "customer_id": 7,  # Jennifer Walsh (successful case)
            "intervention_type": "retention_outreach",
            "churn_probability_before": 0.52,
            "churn_probability_after": 0.28,
            "trigger_reason": "Support ticket volume increase",
            "strategy_chosen": "dedicated_support_with_training",
            "confidence_score": 0.75,
            "expected_success_rate": 0.71,
            "status": "successful", 
            "revenue_at_risk": 42000,
            "estimated_retention_value": 29820,
            "actual_outcome": "retained",
            "execution_steps": json.dumps([
                {"type": "support_escalation", "status": "completed", "outcome": "issues_resolved"},
                {"type": "training_session", "status": "completed", "outcome": "team_confident"},
                {"type": "process_optimization", "status": "completed", "outcome": "workflow_improved"}
            ]),
            "outcome_details": json.dumps({
                "support_tickets_reduced": "85% reduction in monthly tickets",
                "team_satisfaction": "much improved",
                "process_efficiency": "30% workflow improvement"
            }),
            "created_at": datetime.now() - timedelta(days=45),
            "completed_at": datetime.now() - timedelta(days=40)
        }
    ]
    
    # Create interventions
    for intervention_data in interventions:
        intervention = ChurnIntervention(**intervention_data)
        db.add(intervention)
    
    logger.info(f"Added {len(interventions)} historical interventions")

# Main initialization function
async def initialize_customer_data(db: Session):
    """Initialize all customer data - check if reset is needed"""
    
    # Check if data already exists
    existing_customers = db.query(Customer).count()
    if existing_customers > 0:
        logger.info(f"Found {existing_customers} existing customers, skipping initialization")
        return
    
    logger.info("🚀 Initializing comprehensive customer success agent data...")
    await reset_all_demo_data(db)

# Enhanced table creation for TiDB features
async def create_tidb_enhanced_tables(db: Session):
    """Create enhanced tables for TiDB features"""
    
    try:
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
                INDEX idx_customer_time (customer_id, timestamp),
                FULLTEXT(message_content)
            )
            """
        ]
        
        # Execute table creation
        for sql in create_tables_sql:
            db.execute(text(sql))
        
        db.commit()
        logger.info("✅ Enhanced TiDB tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating enhanced tables: {e}")
        db.rollback()
        
# Update your reset function to use this comprehensive data
async def full_demo_reset(db: Session):
    """Complete demo reset function for reset button"""
    try:
        await reset_all_demo_data(db)
        return {
            "status": "success",
            "message": "Complete demo data reset successful",
            "customers_loaded": db.query(Customer).count(),
            "patterns_loaded": db.query(RetentionPattern).count(),
            "memories_loaded": db.query(AgentMemory).count(),
            "communications_loaded": db.query(CustomerCommunication).count()
        }
    except Exception as e:
        logger.error(f"Full demo reset failed: {e}")
        return {
            "status": "error", 
            "message": str(e)
        }
