# backend/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    subscription_plan = Column(String(100), nullable=False)  # basic, pro, enterprise
    monthly_revenue = Column(Float, nullable=False)
    annual_contract_value = Column(Float, nullable=False)
    
    # Customer metrics
    days_since_signup = Column(Integer, default=0)
    last_login_days_ago = Column(Integer, default=0)
    support_tickets_count = Column(Integer, default=0)
    feature_usage_score = Column(Float, default=0.5)  # 0-1 scale
    nps_score = Column(Integer, default=7)  # 0-10 Net Promoter Score
    payment_delays = Column(Integer, default=0)
    
    # Churn indicators
    churn_probability = Column(Float, default=0.0)  # 0-1 probability
    churn_risk_level = Column(String(20), default="low")  # low, medium, high, critical
    
    # Contact info
    phone = Column(String(50))
    timezone = Column(String(50), default="UTC")
    preferred_contact = Column(String(20), default="email")  # email, phone, slack
    
    # Vector embedding for similarity search
    behavior_embedding = Column(JSON)
    usage_patterns = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ChurnIntervention(Base):
    __tablename__ = "churn_interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    intervention_type = Column(String(100), nullable=False)  # retention_call, discount_offer, feature_demo, etc.
    churn_probability_before = Column(Float, nullable=False)
    churn_probability_after = Column(Float)
    
    # Intervention details
    trigger_reason = Column(String(512), nullable=False)
    strategy_chosen = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    expected_success_rate = Column(Float, nullable=False)
    
    # Execution tracking
    status = Column(String(50), default="pending")  # pending, executing, successful, failed, timeout
    execution_steps = Column(JSON)  # Track multi-step execution
    outcome_details = Column(JSON)
    
    # Business impact
    revenue_at_risk = Column(Float, nullable=False)
    estimated_retention_value = Column(Float, nullable=False)
    actual_outcome = Column(String(50))  # retained, churned, pending
    
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer)
    customer_id = Column(Integer)
    
    activity_type = Column(String(100), nullable=False)  # churn_detected, intervention_started, self_correction, etc.
    description = Column(Text, nullable=False)
    urgency_level = Column(String(20), default="medium")  # low, medium, high, critical
    
    status = Column(String(50), default="active")
    activity_metadata = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class RetentionPattern(Base):
    __tablename__ = "retention_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(255), nullable=False)
    customer_characteristics = Column(JSON)  # Common traits of customers who were saved
    successful_interventions = Column(JSON)  # What worked
    success_rate = Column(Float, default=0.0)
    
    # Pattern metadata
    customer_segment = Column(String(100))  # enterprise, smb, startup
    churn_reason_category = Column(String(100))  # pricing, features, support, competition
    
    embedding = Column(JSON)  # Vector representation for similarity search
    graph_relationships = Column(JSON)
    memory_references = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AgentMemory(Base):
    __tablename__ = "agent_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False)
    customer_id = Column(Integer, nullable=False)
    interaction_type = Column(String(100), nullable=False)
    context = Column(JSON, nullable=False)
    outcome = Column(String(100), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    embedding = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())

class CustomerCommunication(Base):
    __tablename__ = "customer_communications"
    
    communication_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    message_content = Column(Text, nullable=False)
    communication_type = Column(String(50), nullable=False)  # email, phone, chat
    timestamp = Column(DateTime, server_default=func.now())
    sentiment_score = Column(Float, default=0.0)
    communication_direction = Column(String(20), default='inbound')  # inbound/outbound
    
    created_at = Column(DateTime, server_default=func.now())
    
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
