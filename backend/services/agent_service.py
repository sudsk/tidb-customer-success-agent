# backend/services/agent_service.py
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.database import Customer, ChurnIntervention, AgentActivity, RetentionPattern
from services.tidb_service import TiDBService
from services.llm_service import LLMService
from services.notification_service import NotificationService
from services.churn_predictor import ChurnPredictor
from config import config
import logging

logger = logging.getLogger(__name__)

class AutonomousCustomerSuccessAgent:
    def __init__(self, db: Session):
        self.db = db
        self.tidb_service = TiDBService(db)
        self.llm_service = LLMService()
        self.notification_service = NotificationService()
        self.churn_predictor = ChurnPredictor()
        
    async def process_customer_health_check(self) -> List[Dict]:
        """Main agent loop - monitors all customers for churn risk"""
        activities = []
        
        # Step 1: Update churn predictions for all active customers
        customers_updated = await self.update_churn_predictions()
        
        # Step 2: Detect high-risk customers needing intervention
        high_risk_customers = await self.detect_churn_risks()
        
        # Step 3: Process interventions for each high-risk customer
        for customer in high_risk_customers:
            intervention_result = await self.execute_autonomous_intervention(customer)
            if intervention_result:
                activities.append(intervention_result)
        
        # Step 4: Follow up on existing interventions
        follow_up_results = await self.follow_up_interventions()
        activities.extend(follow_up_results)
        
        # Step 5: Learn from completed interventions
        await self.update_retention_patterns()
        
        return activities
    
    async def update_churn_predictions(self) -> int:
        """Update churn predictions for all customers"""
        customers = self.db.query(Customer).all()
        updated_count = 0
        
        for customer in customers:
            try:
                # Get customer data for prediction
                customer_data = {
                    'days_since_signup': customer.days_since_signup,
                    'last_login_days_ago': customer.last_login_days_ago,
                    'support_tickets_count': customer.support_tickets_count,
                    'feature_usage_score': customer.feature_usage_score,
                    'nps_score': customer.nps_score,
                    'payment_delays': customer.payment_delays,
                    'monthly_revenue': customer.monthly_revenue
                }
                
                # Predict churn probability
                new_probability = self.churn_predictor.predict_churn_probability(customer_data)
                new_risk_level = self.churn_predictor.get_churn_risk_level(new_probability)
                
                # Update if significantly changed
                if abs(customer.churn_probability - new_probability) > 0.05:
                    customer.churn_probability = new_probability
                    customer.churn_risk_level = new_risk_level
                    updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating churn prediction for customer {customer.id}: {e}")
        
        self.db.commit()
        logger.info(f"Updated churn predictions for {updated_count} customers")
        return updated_count
    
    async def detect_churn_risks(self) -> List[Customer]:
        """Detect customers at high risk of churning who need immediate intervention"""
        
        # Find customers with high churn probability who don't have recent interventions
        high_risk_customers = self.db.query(Customer).filter(
            Customer.churn_probability >= config.CHURN_THRESHOLD
        ).all()
        
        # Filter out customers who already have active interventions
        customers_needing_intervention = []
        for customer in high_risk_customers:
            recent_intervention = self.db.query(ChurnIntervention).filter(
                ChurnIntervention.customer_id == customer.id,
                ChurnIntervention.status.in_(["pending", "executing"]),
                ChurnIntervention.created_at >= datetime.now() - timedelta(hours=24)
            ).first()
            
            if not recent_intervention:
                customers_needing_intervention.append(customer)
        
        logger.info(f"Found {len(customers_needing_intervention)} customers needing intervention")
        return customers_needing_intervention
    
    async def execute_autonomous_intervention(self, customer: Customer) -> Optional[Dict]:
        """Execute autonomous intervention for a high-risk customer"""
        
        try:
            # Step 1: Find similar successful retention cases using TiDB vector search
            similar_cases = await self.tidb_service.find_similar_retention_cases(
                customer_embedding=customer.behavior_embedding,
                customer_segment=self._get_customer_segment(customer),
                churn_probability=customer.churn_probability
            )
            
            # Step 2: Use LLM to choose optimal intervention strategy
            intervention_strategy = await self.llm_service.analyze_retention_strategy(
                customer_profile=self._build_customer_profile(customer),
                churn_probability=customer.churn_probability,
                similar_cases=similar_cases
            )
            
            if intervention_strategy['confidence'] < 0.6:
                logger.info(f"Low confidence intervention for {customer.name}, skipping")
                return None
            
            # Step 3: Create intervention record
            intervention = ChurnIntervention(
                customer_id=customer.id,
                intervention_type=intervention_strategy['intervention_type'],
                churn_probability_before=customer.churn_probability,
                trigger_reason=intervention_strategy['trigger_reason'],
                strategy_chosen=intervention_strategy['strategy'],
                confidence_score=intervention_strategy['confidence'],
                expected_success_rate=intervention_strategy['expected_success_rate'],
                revenue_at_risk=customer.annual_contract_value,
                estimated_retention_value=customer.annual_contract_value * intervention_strategy['expected_success_rate'],
                status="executing",
                execution_steps=json.dumps(intervention_strategy['execution_plan'])
            )
            
            self.db.add(intervention)
            self.db.commit()
            self.db.refresh(intervention)
            
            # Step 4: Execute intervention with self-correction
            execution_result = await self.execute_intervention_with_correction(intervention, customer)
            
            # Step 5: Log activity
            activity = AgentActivity(
                intervention_id=intervention.id,
                customer_id=customer.id,
                activity_type="intervention_executed",
                description=f"Autonomous intervention for {customer.name}: {intervention_strategy['strategy']}",
                urgency_level="high" if customer.churn_probability >= 0.9 else "medium",
                activity_metadata=json.dumps({
                    "churn_probability": customer.churn_probability,
                    "revenue_at_risk": customer.annual_contract_value,
                    "intervention_type": intervention_strategy['intervention_type'],
                    "confidence": intervention_strategy['confidence']
                })
            )
            
            self.db.add(activity)
            self.db.commit()
            
            return {
                "type": "churn_intervention",
                "customer": customer.name,
                "company": customer.company,
                "churn_probability": customer.churn_probability,
                "revenue_at_risk": customer.annual_contract_value,
                "intervention": intervention_strategy['strategy'],
                "confidence": intervention_strategy['confidence'],
                "execution_result": execution_result,
                "intervention_id": intervention.id
            }
            
        except Exception as e:
            logger.error(f"Error executing intervention for customer {customer.id}: {e}")
            return None
    
    async def execute_intervention_with_correction(self, intervention: ChurnIntervention, customer: Customer) -> Dict:
        """Execute intervention steps with autonomous self-correction"""
        
        execution_steps = json.loads(intervention.execution_steps)
        results = []
        
        for step in execution_steps:
            try:
                if step['type'] == 'personalized_outreach':
                    result = await self._execute_outreach(intervention, customer, step)
                elif step['type'] == 'retention_offer':
                    result = await self._execute_retention_offer(intervention, customer, step)
                elif step['type'] == 'schedule_call':
                    result = await self._schedule_success_call(intervention, customer, step)
                elif step['type'] == 'feature_demo':
                    result = await self._schedule_feature_demo(intervention, customer, step)
                else:
                    result = {"status": "unknown_step", "step": step}
                
                results.append(result)
                
                # Self-correction: If step fails, try alternative approach
                if result['status'] == 'failed':
                    corrected_result = await self._self_correct_intervention(intervention, customer, step, result)
                    results.append(corrected_result)
                
            except Exception as e:
                logger.error(f"Execution error in intervention {intervention.id}: {e}")
                # Self-correction on exception
                corrected_result = await self._handle_intervention_error(intervention, step, str(e))
                results.append(corrected_result)
        
        # Update intervention status
        overall_success = any(r.get('status') == 'success' for r in results)
        intervention.status = "successful" if overall_success else "failed"
        intervention.outcome_details = json.dumps(results)
        intervention.completed_at = datetime.now()
        
        self.db.commit()
        
        return {
            "intervention_id": intervention.id,
            "overall_status": intervention.status,
            "execution_results": results,
            "steps_attempted": len(results)
        }
    
    async def _self_correct_intervention(self, intervention: ChurnIntervention, 
                                       customer: Customer, failed_step: Dict, failure_result: Dict) -> Dict:
        """Autonomous self-correction when intervention step fails"""
        
        # Log self-correction activity
        activity = AgentActivity(
            intervention_id=intervention.id,
            customer_id=customer.id,
            activity_type="self_correction",
            description=f"Self-correcting failed intervention step: {failed_step['type']}",
            urgency_level="high",
            activity_metadata=json.dumps({
                "failed_step": failed_step,
                "failure_reason": failure_result.get('error', 'Unknown'),
                "correction_strategy": "alternative_approach"
            })
        )
        self.db.add(activity)
        self.db.commit()
        
        # Example self-corrections based on failure type
        if failed_step['type'] == 'personalized_outreach' and failed_step.get('method') == 'email':
            # Email failed -> try phone call
            corrected_step = failed_step.copy()
            corrected_step['method'] = 'phone'
            return await self._execute_outreach(intervention, customer, corrected_step)
        
        elif failed_step['type'] == 'retention_offer' and 'budget' in failure_result.get('error', '').lower():
            # Budget concerns -> offer payment plan instead of discount
            corrected_step = {
                "type": "retention_offer",
                "offer_type": "payment_plan",
                "details": "Flexible payment terms to ease budget concerns"
            }
            return await self._execute_retention_offer(intervention, customer, corrected_step)
        
        elif failed_step['type'] == 'schedule_call' and customer.preferred_contact != 'phone':
            # Phone call rejected -> schedule video demo instead
            return await self._schedule_feature_demo(intervention, customer, {
                "type": "feature_demo",
                "method": "video_call",
                "focus": "value_demonstration"
            })
        
        return {"status": "correction_attempted", "original_failure": failure_result}
    
    async def follow_up_interventions(self) -> List[Dict]:
        """Follow up on existing interventions and check their effectiveness"""
        
        # Find interventions that need follow-up (completed in last 24-48 hours)
        interventions_to_follow_up = self.db.query(ChurnIntervention).filter(
            ChurnIntervention.status.in_(["successful", "failed"]),
            ChurnIntervention.completed_at >= datetime.now() - timedelta(hours=48),
            ChurnIntervention.completed_at <= datetime.now() - timedelta(hours=24)
        ).all()
        
        follow_up_results = []
        
        for intervention in interventions_to_follow_up:
            customer = self.db.query(Customer).filter(Customer.id == intervention.customer_id).first()
            if not customer:
                continue
            
            # Check if customer's churn risk improved
            new_churn_probability = self.churn_predictor.predict_churn_probability({
                'days_since_signup': customer.days_since_signup,
                'last_login_days_ago': customer.last_login_days_ago,
                'support_tickets_count': customer.support_tickets_count,
                'feature_usage_score': customer.feature_usage_score,
                'nps_score': customer.nps_score,
                'payment_delays': customer.payment_delays,
                'monthly_revenue': customer.monthly_revenue
            })
            
            # Update intervention outcome
            intervention.churn_probability_after = new_churn_probability
            
            probability_improvement = intervention.churn_probability_before - new_churn_probability
            
            if probability_improvement > 0.1:  # Significant improvement
                intervention.actual_outcome = "retained"
                outcome_status = "success"
            elif probability_improvement > -0.05:  # Stable
                intervention.actual_outcome = "stable"
                outcome_status = "partial_success"
            else:  # Worsened
                intervention.actual_outcome = "at_risk"
                outcome_status = "needs_escalation"
            
            follow_up_results.append({
                "type": "intervention_follow_up",
                "intervention_id": intervention.id,
                "customer": customer.name,
                "outcome": outcome_status,
                "probability_before": intervention.churn_probability_before,
                "probability_after": new_churn_probability,
                "improvement": probability_improvement,
                "revenue_impact": customer.annual_contract_value if outcome_status == "success" else 0
            })
        
        self.db.commit()
        return follow_up_results
    
    async def update_retention_patterns(self):
        """Learn from intervention outcomes and update success patterns"""
        
        # Get recent completed interventions with outcomes
        completed_interventions = self.db.query(ChurnIntervention).filter(
            ChurnIntervention.actual_outcome.isnot(None),
            ChurnIntervention.completed_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        for intervention in completed_interventions:
            customer = self.db.query(Customer).filter(Customer.id == intervention.customer_id).first()
            if not customer:
                continue
            
            success = intervention.actual_outcome == "retained"
            
            # Update or create retention pattern
            await self.tidb_service.update_retention_patterns(
                customer_segment=self._get_customer_segment(customer),
                intervention_type=intervention.intervention_type,
                strategy=intervention.strategy_chosen,
                success=success,
                customer_characteristics=self._build_customer_profile(customer)
            )
        
        logger.info(f"Updated retention patterns based on {len(completed_interventions)} interventions")
    
    def _get_customer_segment(self, customer: Customer) -> str:
        """Determine customer segment based on revenue and characteristics"""
        if customer.annual_contract_value >= 50000:
            return "enterprise"
        elif customer.annual_contract_value >= 10000:
            return "mid_market"
        else:
            return "smb"
    
    def _build_customer_profile(self, customer: Customer) -> Dict:
        """Build comprehensive customer profile for analysis"""
        return {
            "name": customer.name,
            "company": customer.company,
            "segment": self._get_customer_segment(customer),
            "subscription_plan": customer.subscription_plan,
            "monthly_revenue": customer.monthly_revenue,
            "annual_contract_value": customer.annual_contract_value,
            "days_since_signup": customer.days_since_signup,
            "last_login_days_ago": customer.last_login_days_ago,
            "support_tickets_count": customer.support_tickets_count,
            "feature_usage_score": customer.feature_usage_score,
            "nps_score": customer.nps_score,
            "payment_delays": customer.payment_delays,
            "churn_probability": customer.churn_probability,
            "churn_risk_level": customer.churn_risk_level,
            "preferred_contact": customer.preferred_contact,
            "timezone": customer.timezone
        }
    
    # Implementation of intervention execution methods
    async def _execute_outreach(self, intervention: ChurnIntervention, customer: Customer, step: Dict) -> Dict:
        """Execute personalized outreach to customer"""
        try:
            method = step.get('method', customer.preferred_contact)
            
            if method == 'email':
                subject = f"We value your partnership, {customer.name}"
                content = await self.llm_service.generate_retention_email(
                    customer_name=customer.name,
                    company=customer.company,
                    churn_risk_factors=step.get('personalization', {}),
                    intervention_type=intervention.intervention_type
                )
                
                success = await self.notification_service.send_email(
                    to=customer.email,
                    subject=subject,
                    content=content
                )
                
            elif method == 'phone':
                success = await self.notification_service.schedule_phone_call(
                    customer_phone=customer.phone,
                    customer_timezone=customer.timezone,
                    urgency="high" if customer.churn_probability >= 0.9 else "medium"
                )
                
            elif method == 'slack':
                success = await self.notification_service.send_slack_message(
                    customer_id=customer.id,
                    message=f"Hi {customer.name}! Your success manager would like to connect. Can we schedule a quick call?"
                )
            
            else:
                return {"status": "failed", "error": f"Unknown contact method: {method}"}
            
            return {
                "status": "success" if success else "failed",
                "step_type": "personalized_outreach",
                "method": method,
                "customer": customer.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _execute_retention_offer(self, intervention: ChurnIntervention, customer: Customer, step: Dict) -> Dict:
        """Execute retention offer (discount, upgrade, etc.)"""
        try:
            offer_type = step.get('offer_type', 'discount')
            
            if offer_type == 'discount':
                discount_percent = min(step.get('discount_percent', 20), 30)  # Max 30% discount
                offer_details = f"{discount_percent}% discount on your next renewal"
                
            elif offer_type == 'upgrade':
                offer_details = f"Complimentary upgrade to {step.get('target_plan', 'Pro')} plan for 3 months"
                
            elif offer_type == 'payment_plan':
                offer_details = "Flexible payment terms - pay monthly instead of annually"
                
            elif offer_type == 'feature_credit':
                offer_details = f"${step.get('credit_amount', 500)} in feature credits"
                
            else:
                offer_details = step.get('custom_offer', 'Custom retention package')
            
            # Send offer via preferred method
            success = await self.notification_service.send_retention_offer(
                customer_email=customer.email,
                customer_name=customer.name,
                offer_details=offer_details,
                urgency_level="high" if customer.churn_probability >= 0.9 else "medium"
            )
            
            return {
                "status": "success" if success else "failed",
                "step_type": "retention_offer",
                "offer_type": offer_type,
                "offer_details": offer_details,
                "customer": customer.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _schedule_success_call(self, intervention: ChurnIntervention, customer: Customer, step: Dict) -> Dict:
        """Schedule success call with customer success manager"""
        try:
            call_urgency = "immediate" if customer.churn_probability >= 0.9 else "within_24h"
            
            success = await self.notification_service.schedule_success_call(
                customer_name=customer.name,
                customer_phone=customer.phone,
                customer_timezone=customer.timezone,
                urgency=call_urgency,
                talking_points=step.get('talking_points', [
                    f"Address churn risk factors",
                    f"Discuss value realization",
                    f"Identify additional needs"
                ])
            )
            
            return {
                "status": "success" if success else "failed",
                "step_type": "success_call_scheduled",
                "urgency": call_urgency,
                "customer": customer.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _schedule_feature_demo(self, intervention: ChurnIntervention, customer: Customer, step: Dict) -> Dict:
        """Schedule personalized feature demonstration"""
        try:
            demo_focus = step.get('focus', 'underutilized_features')
            
            success = await self.notification_service.schedule_feature_demo(
                customer_email=customer.email,
                customer_name=customer.name,
                demo_focus=demo_focus,
                feature_usage_score=customer.feature_usage_score
            )
            
            return {
                "status": "success" if success else "failed",
                "step_type": "feature_demo_scheduled",
                "demo_focus": demo_focus,
                "customer": customer.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _handle_intervention_error(self, intervention: ChurnIntervention, step: Dict, error: str) -> Dict:
        """Handle unexpected intervention errors"""
        return {
            "status": "error_handled",
            "step_type": step['type'],
            "error": error,
            "recovery_action": "logged_for_manual_review",
            "timestamp": datetime.now().isoformat()
        }
