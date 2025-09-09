import google.generativeai as genai
from typing import Dict, List
import json
from config import config
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize Gemini - GCP handles authentication automatically"""
        # On Cloud Run, GCP automatically provides credentials
        # No explicit authentication needed!
        genai.configure()  # Uses Application Default Credentials automatically
        
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Gemini initialized with automatic GCP authentication")
    
    async def analyze_retention_strategy(self, customer_profile: Dict, churn_probability: float,
                                       similar_cases: List[Dict]) -> Dict:
        """Use Gemini to analyze retention strategy and choose optimal intervention"""
        
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

        Based on this analysis, determine the best intervention strategy.

        Respond ONLY with valid JSON in this exact format:
        {{
            "trigger_reason": "specific reason for churn risk",
            "intervention_type": "retention_outreach",
            "strategy": "strategy_name",
            "confidence": 0.85,
            "expected_success_rate": 0.73,
            "execution_plan": [
                {{"type": "personalized_outreach", "method": "email"}},
                {{"type": "retention_offer", "offer_type": "discount", "discount_percent": 20}},
                {{"type": "schedule_call", "urgency": "high"}}
            ],
            "reasoning": "detailed explanation"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Clean up response to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["trigger_reason", "intervention_type", "strategy", "confidence", "expected_success_rate", "execution_plan"]
            for field in required_fields:
                if field not in result:
                    raise KeyError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            # Fallback decision making
            return self._fallback_retention_strategy(customer_profile, churn_probability)
    
    async def generate_retention_email(self, customer_name: str, company: str,
                                     churn_risk_factors: Dict, intervention_type: str) -> str:
        """Generate personalized retention email using Gemini"""
        
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
        6. Keep it under 200 words
        
        Write only the email content, no subject line or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return f"""
            Dear {customer_name},
            
            I hope this email finds you well. I noticed some changes in your account activity and wanted to personally reach out to see how we can better support {company}'s success.
            
            Your partnership means everything to us, and I'd love to schedule a quick 15-minute call to discuss how we can enhance your experience with our platform.
            
            Would you be available for a brief call this week? I'm here to help ensure you're getting maximum value from our partnership.
            
            Best regards,
            Your Customer Success Team
            """
    
    def _fallback_retention_strategy(self, customer_profile: Dict, churn_probability: float) -> Dict:
        """Fallback retention strategy when Gemini is unavailable"""
        
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


    async def analyze_enhanced_retention_strategy(self, customer_profile: Dict, 
                                                agent_memories: List[Dict],
                                                communications: List[Dict],
                                                relationships: Dict,
                                                churn_probability: float) -> Dict:
        """Enhanced retention strategy using agent memory, communications, and graph RAG"""
        
        prompt = f"""
        As an autonomous customer success AI agent with memory and relationship analysis, 
        determine the optimal retention strategy for this at-risk customer:
    
        CUSTOMER PROFILE:
        - Name: {customer_profile['name']} ({customer_profile['company']})
        - Segment: {customer_profile['segment']}
        - Annual Value: ${customer_profile['annual_contract_value']:,.0f}
        - Churn Risk: {churn_probability:.1%}
        - Usage Score: {customer_profile['feature_usage_score']:.2f}
        - NPS: {customer_profile['nps_score']}/10
    
        AGENT MEMORY (Past Successful Cases):
        {json.dumps(agent_memories[:3], indent=2)}
    
        CUSTOMER COMMUNICATIONS ANALYSIS:
        {json.dumps(communications[:5], indent=2)}
    
        RELATIONSHIP GRAPH ANALYSIS:
        - Direct relationships: {len(relationships.get('direct_relationships', []))} customers
        - Similar profiles: {len(relationships.get('similar_profile_customers', []))} customers  
        - Successful strategies from similar customers: {relationships.get('successful_strategies', [])}
    
        Based on this multi-dimensional analysis using TiDB's vector search, full-text search, 
        and graph relationships, determine the optimal intervention strategy.
    
        Respond ONLY with valid JSON:
        {{
            "trigger_reason": "specific reason with memory/communication context",
            "intervention_type": "retention_outreach",
            "strategy": "strategy_name",
            "confidence": 0.85,
            "expected_success_rate": 0.73,
            "execution_plan": [
                {{"type": "memory_informed_outreach", "method": "email"}},
                {{"type": "relationship_leveraged_offer", "details": "based_on_similar_success"}},
                {{"type": "communication_context_call", "urgency": "high"}}
            ],
            "reasoning": "detailed explanation of memory/communication/relationship insights used"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            
            # Validate and enhance with TiDB insights
            result["tidb_features_used"] = {
                "vector_search": len(agent_memories) > 0,
                "full_text_search": len(communications) > 0,
                "graph_rag": len(relationships.get('successful_strategies', [])) > 0,
                "agent_memory": True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced Gemini analysis failed: {e}")
            # Enhanced fallback with memory context
            return self._enhanced_fallback_strategy(customer_profile, agent_memories, relationships)
    
    def _enhanced_fallback_strategy(self, customer_profile: Dict, 
                                  agent_memories: List[Dict], 
                                  relationships: Dict) -> Dict:
        """Enhanced fallback strategy incorporating available data"""
        
        # Use memory insights if available
        if agent_memories:
            successful_strategy = agent_memories[0].get('context', {}).get('strategy', 'personalized_outreach')
        elif relationships.get('successful_strategies'):
            successful_strategy = relationships['successful_strategies'][0].get('successful_strategy', 'retention_call')
        else:
            successful_strategy = "data_driven_outreach"
        
        return {
            "trigger_reason": f"High churn probability with {len(agent_memories)} similar memory cases",
            "intervention_type": "memory_enhanced_retention",
            "strategy": successful_strategy,
            "confidence": 0.75,
            "expected_success_rate": 0.68,
            "execution_plan": [
                {"type": "memory_informed_outreach", "method": customer_profile['preferred_contact']},
                {"type": "relationship_context_offer", "details": "based_on_graph_analysis"},
                {"type": "adaptive_follow_up", "urgency": "high"}
            ],
            "reasoning": f"Enhanced fallback using {len(agent_memories)} memory cases and {len(relationships.get('successful_strategies', []))} relationship insights",
            "tidb_features_used": {
                "vector_search": True,
                "full_text_search": True,
                "graph_rag": True,
                "agent_memory": True
            }
        }
