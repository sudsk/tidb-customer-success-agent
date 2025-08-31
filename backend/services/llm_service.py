# backend/services/llm_service.py
import openai
from typing import Dict, List
import json
from config import config

class LLMService:
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
    
    async def analyze_retention_strategy(self, customer_profile: Dict, churn_probability: float,
                                       similar_cases: List[Dict]) -> Dict:
        """Use LLM to analyze retention strategy and choose optimal intervention"""
        
        prompt = f"""
        As an autonomous customer success AI agent, analyze this customer churn situation:

        CUSTOMER PROFILE:
        - Name: {customer_profile['name']} ({customer_profile['company']})
        - Segment: {customer_profile['segment']}
        - Plan: {customer_profile['subscription_plan']} 
        - Monthly Revenue: ${customer_profile['monthly_revenue']:,.0f}
        - Annual Contract Value: ${customer_profile['annual_contract_value']:,.0f}
        - Days since signup: {customer_profile['days_since_signup']}
        - Last login: {customer_profile['last_login_days_ago']} days ago
        - Support tickets: {customer_profile['support_tickets_count']}
        - Feature usage score: {customer_profile['feature_usage_score']:.2f}
        - NPS score: {customer_profile['nps_score']}/10
        - Payment delays: {customer_profile['payment_delays']}

        CHURN RISK:
        - Probability: {churn_probability:.1%}
        - Risk Level: {customer_profile['churn_risk_level']}

        SIMILAR SUCCESSFUL RETENTION CASES:
        {json.dumps(similar_cases[:3], indent=2)}

        Based on this analysis, determine:
        1. Root cause of churn risk
        2. Best intervention strategy
        3. Execution plan with 3-4 specific steps
        4. Expected success rate
        5. Confidence in recommendation

        Consider factors like:
        - Customer segment and value
        - Usage patterns and engagement level
        - Communication preferences
        - Similar case outcomes
        - Urgency based on churn probability

        Respond in JSON format:
        {{
            "trigger_reason": "specific reason for churn risk",
            "intervention_type": "retention_outreach/discount_offer/success_call/feature_demo",
            "strategy": "strategy_name",
            "confidence": 0.85,
            "expected_success_rate": 0.73,
            "execution_plan": [
                {{"type": "personalized_outreach", "method": "email", "personalization": {{}}}},
                {{"type": "retention_offer", "offer_type": "discount", "discount_percent": 20}},
                {{"type": "schedule_call", "urgency": "high"}},
                {{"type": "feature_demo", "focus": "underutilized_features"}}
            ],
            "reasoning": "detailed explanation of strategy choice"
        }}
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert autonomous customer success AI that prevents churn through intelligent interventions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback decision making
            return self._fallback_retention_strategy(customer_profile, churn_probability)
    
    async def generate_retention_email(self, customer_name: str, company: str,
                                     churn_risk_factors: Dict, intervention_type: str) -> str:
        """Generate personalized retention email"""
        
        prompt = f"""
        Write a personalized, empathetic retention email for a customer at risk of churning.
        
        Customer: {customer_name} at {company}
        Intervention Type: {intervention_type}
        Risk Factors: {json.dumps(churn_risk_factors, indent=2)}
        
        The email should:
        1. Show we care about their success
        2. Address their specific concerns
        3. Offer concrete help
        4. Include a clear call-to-action
        5. Be warm but professional
        6. Keep it concise (under 200 words)
        
        Subject line: We value your partnership, {customer_name}
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a customer success manager writing retention emails that save customers and build relationships."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"""
            Dear {customer_name},
            
            I hope this email finds you well. I noticed some changes in your account activity and wanted to personally reach out to see how we can better support {company}'s success.
            
            Your partnership means everything to us, and I'd love to schedule a quick 15-minute call to discuss how we can enhance your experience with our platform.
            
            Would you be available for a brief call this week? I'm here to help ensure you're getting maximum value from our partnership.
            
            Best regards,
            Your Customer Success Team
            
            P.S. I have some ideas that could immediately improve your results - I'd love to share them with you.
            """
    
    def _fallback_retention_strategy(self, customer_profile: Dict, churn_probability: float) -> Dict:
        """Fallback retention strategy when LLM is unavailable"""
        
        # Rule-based fallback logic
        if customer_profile['segment'] == 'enterprise':
            strategy = "executive_outreach"
            intervention_type = "success_call"
            expected_success_rate = 0.78
        elif customer_profile['feature_usage_score'] < 0.3:
            strategy = "feature_adoption"
            intervention_type = "feature_demo"
            expected_success_rate = 0.65
        elif customer_profile['nps_score'] < 6:
            strategy = "satisfaction_recovery"
            intervention_type = "retention_outreach"
            expected_success_rate = 0.71
        else:
            strategy = "value_reinforcement"
            intervention_type = "discount_offer"
            expected_success_rate = 0.68
        
        return {
            "trigger_reason": f"High churn probability ({churn_probability:.1%}) with {customer_profile['churn_risk_level']} risk",
            "intervention_type": intervention_type,
            "strategy": strategy,
            "confidence": 0.75,
            "expected_success_rate": expected_success_rate,
            "execution_plan": [
                {"type": "personalized_outreach", "method": customer_profile['preferred_contact']},
                {"type": "retention_offer", "offer_type": "discount", "discount_percent": 15},
                {"type": "schedule_call", "urgency": "high" if churn_probability >= 0.9 else "medium"}
            ],
            "reasoning": f"Fallback strategy based on {customer_profile['segment']} segment and risk factors"
        }
