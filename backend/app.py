# backend/app.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import logging
from contextual import asynccontextmanager
from datetime import datetime

from models.database import create_tables, get_db
from services.agent_service import AutonomousCustomerSuccessAgent
from services.tidb_service import TiDBService
from utils.mock_data import initialize_customer_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent task
agent_task = None
latest_activities = []
latest_analytics = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Autonomous Customer Success Agent...")
    create_tables()
    
    # Initialize sample data
    db = next(get_db())
    await initialize_customer_data(db)
    
    # Start background agent
    global agent_task
    agent_task = asyncio.create_task(run_agent_loop())
    
    yield
    
    # Shutdown
    if agent_task:
        agent_task.cancel()
    logger.info("Agent stopped")

app = FastAPI(
    title="TiDB Autonomous Customer Success Agent",
    description="Hackathon MVP - AI Agent that Prevents Customer Churn",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_agent_loop():
    """Background task running the autonomous customer success agent"""
    while True:
        try:
            db = next(get_db())
            agent = AutonomousCustomerSuccessAgent(db)
            
            # Process customer health checks
            activities = await agent.process_customer_health_check()
            
            # Update global state
            global latest_activities, latest_analytics
            latest_activities.extend(activities[-10:])
            latest_activities = latest_activities[-25:]  # Keep last 25 activities
            
            # Update analytics
            tidb_service = TiDBService(db)
            latest_analytics = await tidb_service.get_churn_analytics()
            
            logger.info(f"🤖 Agent cycle completed: {len(activities)} new interventions")
            
        except Exception as e:
            logger.error(f"Agent loop error: {e}")
        
        # Run every 15 seconds for faster demo
        await asyncio.sleep(15)

@app.get("/")
async def root():
    return {
        "message": "TiDB Autonomous Customer Success Agent",
        "status": "active",
        "version": "1.0.0",
        "description": "AI Agent that prevents customer churn"
    }

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get real-time dashboard metrics"""
    
    tidb_service = TiDBService(db)
    analytics = await tidb_service.get_churn_analytics()
    
    # Calculate key metrics
    total_at_risk = sum(seg.get('total_at_risk', 0) for seg in analytics['churn_distribution'].values())
    high_risk_revenue = analytics['churn_distribution'].get('high', {}).get('total_at_risk', 0)
    critical_risk_revenue = analytics['churn_distribution'].get('critical', {}).get('total_at_risk', 0)
    
    return {
        "kpis": {
            "customers_saved": {
                "value": 847,  # Mock accumulated saves
                "change": "+73 this week",
                "label": "Customers Saved from Churn"
            },
            "revenue_retained": {
                "value": 2300000,  # $2.3M
                "change": "+35% vs last month", 
                "label": "Revenue Retained (Monthly)"
            },
            "churn_reduction": {
                "value": 67.4,  # 67.4% reduction
                "change": "From 8.2% to 2.7%",
                "label": "Churn Rate Reduction"
            },
            "agent_autonomy": {
                "value": analytics['agent_performance']['autonomy_level'],
                "change": f"{analytics['agent_performance']['avg_response_time_minutes']:.0f}s avg response",
                "label": "Agent Autonomy Level"
            }
        },
        "churn_risk_summary": {
            "total_customers": analytics['total_customers'],
            "high_risk_customers": analytics['high_risk_customers'],
            "total_revenue_at_risk": total_at_risk,
            "critical_revenue_at_risk": critical_risk_revenue,
            "churn_distribution": analytics['churn_distribution']
        },
        "agent_performance": analytics['agent_performance']
    }

@app.get("/api/dashboard/activities")
async def get_recent_activities():
    """Get recent agent activities"""
    
    formatted_activities = []
    
    for activity in latest_activities[-15:]:
        if activity.get('type') == 'churn_intervention':
            formatted_activities.append({
                "id": f"intervention_{activity.get('intervention_id', 'unknown')}",
                "type": "churn_intervention", 
                "title": f"🚨 Customer at Risk: {activity['customer']} ({activity['company']})",
                "description": f"Churn risk: {activity['churn_probability']:.0%} • Revenue at risk: ${activity['revenue_at_risk']/1000:.0f}K • Strategy: {activity['intervention']}",
                "status": "executing" if activity.get('execution_result', {}).get('overall_status') == 'successful' else 'failed',
                "urgency": "critical" if activity['churn_probability'] >= 0.9 else "high",
                "timestamp": "2 min ago",
                "metadata": {
                    "customer": activity['customer'],
                    "churn_probability": activity['churn_probability'],
                    "revenue_at_risk": activity['revenue_at_risk'],
                    "intervention": activity['intervention'],
                    "confidence": activity.get('confidence', 0)
                }
            })
        elif activity.get('type') == 'intervention_follow_up':
            outcome_icon = "✅" if activity.get('outcome') == 'success' else "⚠️"
            status = 'success' if activity.get('outcome') == 'success' else 'monitoring'
            
            formatted_activities.append({
                "id": f"followup_{activity.get('intervention_id', 'unknown')}",
                "type": "intervention_followup",
                "title": f"{outcome_icon} Follow-up: {activity['customer']}",
                "description": f"Churn risk: {activity['probability_before']:.0%} → {activity['probability_after']:.0%} • Improvement: {activity['improvement']:+.0%}",
                "status": status,
                "urgency": "low",
                "timestamp": "15 min ago",
                "metadata": {
                    "customer": activity['customer'],
                    "improvement": activity['improvement'],
                    "revenue_impact": activity.get('revenue_impact', 0)
                }
            })
    
    # Add some mock activities for demo richness
    if len(formatted_activities) < 8:
        mock_activities = [
            {
                "id": "demo_1",
                "type": "customer_saved",
                "title": "✅ Customer Saved: Sarah Chen (TechStart Inc)",
                "description": "Successful retention call • 89% → 23% churn risk • $45K annual value retained",
                "status": "success",
                "urgency": "low",
                "timestamp": "8 min ago",
                "metadata": {"revenue_saved": 45000}
            },
            {
                "id": "demo_2",
                "type": "self_correction", 
                "title": "🔄 Self-correction: Email failed → Phone call successful",
                "description": "Customer: Mike Rodriguez (GrowthCorp) • Alternative outreach strategy worked",
                "status": "corrected",
                "urgency": "medium",
                "timestamp": "12 min ago",
                "metadata": {}
            },
            {
                "id": "demo_3",
                "type": "pattern_learning",
                "title": "🧠 Pattern learned: Enterprise discount strategy 94% effective",
                "description": "Updated retention patterns in TiDB • Enterprise segment responds well to payment terms",
                "status": "completed",
                "urgency": "low", 
                "timestamp": "18 min ago",
                "metadata": {}
            }
        ]
        
        formatted_activities.extend(mock_activities[:8-len(formatted_activities)])
    
    return {"activities": formatted_activities}

@app.get("/api/customers/at-risk")
async def get_at_risk_customers(db: Session = Depends(get_db)):
    """Get customers currently at high risk of churning"""
    
    from models.database import Customer
    
    high_risk_customers = db.query(Customer).filter(
        Customer.churn_probability >= 0.6
    ).order_by(Customer.churn_probability.desc()).limit(20).all()
    
    customers_data = []
    for customer in high_risk_customers:
        customers_data.append({
            "id": customer.id,
            "name": customer.name,
            "company": customer.company,
            "email": customer.email,
            "subscription_plan": customer.subscription_plan,
            "monthly_revenue": customer.monthly_revenue,
            "annual_contract_value": customer.annual_contract_value,
            "churn_probability": customer.churn_probability,
            "churn_risk_level": customer.churn_risk_level,
            "last_login_days_ago": customer.last_login_days_ago,
            "support_tickets_count": customer.support_tickets_count,
            "feature_usage_score": customer.feature_usage_score,
            "nps_score": customer.nps_score,
            "days_since_signup": customer.days_since_signup
        })
    
    return {"customers": customers_data}

@app.get("/api/analytics/churn")
async def get_churn_analytics(db: Session = Depends(get_db)):
    """Get comprehensive churn analytics"""
    
    tidb_service = TiDBService(db)
    return await tidb_service.get_churn_analytics()

@app.get("/api/feed/realtime")
async def get_realtime_feed(db: Session = Depends(get_db)):
    """Get real-time customer activity feed"""
    
    tidb_service = TiDBService(db)
    return await tidb_service.get_real_time_customer_feed()

@app.post("/api/agent/trigger")
async def trigger_agent_manually(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger agent for demo purposes"""
    
    async def process_demo():
        agent = AutonomousCustomerSuccessAgent(db)
        activities = await agent.process_customer_health_check()
        
        global latest_activities
        latest_activities.extend(activities)
        latest_activities = latest_activities[-25:]
    
    background_tasks.add_task(process_demo)
    
    return {"message": "Customer Success Agent triggered", "status": "processing"}

@app.get("/api/interventions/recent")
async def get_recent_interventions(db: Session = Depends(get_db)):
    """Get recent intervention attempts and outcomes"""
    
    from models.database import ChurnIntervention, Customer
    
    recent_interventions = db.query(ChurnIntervention).join(Customer).order_by(
        ChurnIntervention.created_at.desc()
    ).limit(15).all()
    
    interventions_data = []
    for intervention in recent_interventions:
        customer = db.query(Customer).filter(Customer.id == intervention.customer_id).first()
        
        interventions_data.append({
            "id": intervention.id,
            "customer_name": customer.name if customer else "Unknown",
            "company": customer.company if customer else "Unknown",
            "intervention_type": intervention.intervention_type,
            "strategy_chosen": intervention.strategy_chosen,
            "churn_probability_before": intervention.churn_probability_before,
            "churn_probability_after": intervention.churn_probability_after,
            "status": intervention.status,
            "actual_outcome": intervention.actual_outcome,
            "revenue_at_risk": intervention.revenue_at_risk,
            "estimated_retention_value": intervention.estimated_retention_value,
            "created_at": intervention.created_at.isoformat(),
            "completed_at": intervention.completed_at.isoformat() if intervention.completed_at else None
        })
    
    return {"interventions": interventions_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
