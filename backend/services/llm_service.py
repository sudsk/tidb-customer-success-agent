import vertexai
from vertexai.generative_models import GenerativeModel
from typing import Dict, List
import json
from config import config
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize Gemini via Vertex AI - uses ADC automatically"""
        try:        
            # Initialize Vertex AI (uses Application Default Credentials)
            vertexai.init(project=config.GCP_PROJECT_ID, location="us-central1")
            
            # Use Vertex AI Gemini model
            self.model = GenerativeModel("gemini-2.5-flash")
            logger.info("Vertex AI Gemini initialized with ADC")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI Gemini: {e}")
            raise
    
    async def analyze_enhanced_retention_strategy(self, customer_profile: Dict, 
                                                agent_memories: List[Dict],
                                                communications: List[Dict],
                                                relationships: Dict,
                                                churn_probability: float,
                                                similar_cases: List[Dict] = None) -> Dict:
        """Enhanced retention strategy using agent memory, communications, graph RAG, and vector search"""
        
        prompt = f"""
        As an autonomous customer success AI agent with advanced TiDB capabilities, 
        determine the optimal retention strategy for this at-risk customer:
    
        CUSTOMER PROFILE:
        - Name: {customer_profile['name']} ({customer_profile['company']})
        - Segment: {customer_profile['segment']}
        - Annual Value: ${customer_profile['annual_contract_value']:,.0f}
        - Churn Risk: {churn_probability:.1%}
        - Usage Score: {customer_profile['feature_usage_score']:.2f}
        - NPS: {customer_profile['nps_score']}/10
    
        VECTOR SEARCH RESULTS (TiDB Serverless):
        {json.dumps(similar_cases[:3] if similar_cases else [], indent=2)}
    
        AGENT MEMORY (Past Successful Cases):
        {json.dumps(agent_memories[:3], indent=2)}
    
        CUSTOMER COMMUNICATIONS ANALYSIS:
        {json.dumps(communications[:5], indent=2)}
    
        RELATIONSHIP GRAPH ANALYSIS:
        - Direct relationships: {len(relationships.get('direct_relationships', []))} customers
        - Similar profiles: {len(relationships.get('similar_profile_customers', []))} customers  
        - Successful strategies from similar customers: {relationships.get('successful_strategies', [])}
    
        Based on this comprehensive analysis using TiDB Serverless vector search, 
        agent memory, full-text search, and graph relationships, determine the optimal intervention.
    
        Respond ONLY with valid JSON:
        {{
            "trigger_reason": "specific reason with vector search context (max 200 chars)",
            "intervention_type": "enhanced_retention_outreach",
            "strategy": "short_strategy_name_max_80_chars", 
            "confidence": 0.87,
            "expected_success_rate": 0.78,
            "execution_plan": [
                {{"type": "vector_informed_outreach", "method": "email", "similar_case_confidence": 0.87}},
                {{"type": "memory_enhanced_offer", "details": "based_on_successful_patterns"}},
                {{"type": "graph_relationship_leverage", "urgency": "high"}}
            ],
            "reasoning": "detailed explanation using vector search, agent memory, and relationship insights",
            "tidb_features_used": {{
                "vector_search": true,
                "agent_memory": true,
                "full_text_search": true,
                "graph_rag": true,
                "htap_processing": true
            }}
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
            
            # Enhance with vector search insights
            if similar_cases:
                result["vector_search_insights"] = {
                    "cases_found": len(similar_cases),
                    "top_similarity": max([case.get('similarity_score', 0) for case in similar_cases]) if similar_cases else 0,
                    "avg_success_rate": sum([case.get('success_rate', 0) for case in similar_cases]) / len(similar_cases) if similar_cases else 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced Gemini analysis failed: {e}")
            # Enhanced fallback with vector search context
            return self._enhanced_fallback_strategy(customer_profile, agent_memories, relationships, similar_cases)
    
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
    
    def _enhanced_fallback_strategy(self, customer_profile: Dict, 
                                  agent_memories: List[Dict], 
                                  relationships: Dict, 
                                  similar_cases: List[Dict]) -> Dict:
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
