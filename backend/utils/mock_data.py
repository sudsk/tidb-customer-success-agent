# backend/utils/mock_data.py
import json
import random
import numpy as np        logger.info(f"Updated retention patterns based on {len(completed_interventions)} interventions")
    
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
