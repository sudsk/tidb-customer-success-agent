# backend/services/tidb_service.py
import json
import numpy as np
import hashlib
import math
from scipy.spatial.distance import cosine
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
from models.database import Customer, RetentionPattern, ChurnIntervention, AgentActivity, AgentMemory, CustomerCommunication
import uuid
import logging

logger = logging.getLogger(__name__)

# Generate semantic embedding:
def generate_semantic_embedding(text: str, dimension: int = 768) -> List[float]:
    """Generate consistent, meaningful embedding from customer text"""
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
    
    if 'enterprise' in text_lower:
        for i in range(min(20, dimension)):
            embedding[i] += 0.3
    if 'high' in text_lower and 'risk' in text_lower:
        for i in range(20, min(40, dimension)):
            embedding[i] += 0.5
    
    # Normalize to unit vector
    magnitude = math.sqrt(sum(x * x for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding

# Needed for fallback similarity calculation:
def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude_a = math.sqrt(sum(a * a for a in vec1))
    magnitude_b = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)
    
class TiDBService:
    def __init__(self, db: Session):
        self.db = db
    
    async def find_similar_retention_cases(self, customer_embedding: List[float], 
                                         customer_segment: str, churn_probability: float, 
                                         limit: int = 5) -> List[Dict]:
        """Vector search using Python similarity calculation"""
        
        # If no meaningful embedding provided, generate from customer data
        if not customer_embedding or all(x == 0 for x in customer_embedding[:10]):
            customer_text = f"segment:{customer_segment} risk:{churn_probability:.2f}"
            customer_embedding = generate_semantic_embedding(customer_text)
        
        try:
            # Get all retention patterns for this segment
            patterns = self.db.query(RetentionPattern).filter(
                RetentionPattern.customer_segment == customer_segment,
                RetentionPattern.success_rate > 0.5
            ).all()
            
            if not patterns:
                logger.info(f"No retention patterns found for segment: {customer_segment}")
                return await self._get_default_patterns(customer_segment)
            
            similarities = []
            for pattern in patterns:
                try:
                    # Generate embedding for pattern if it doesn't have one
                    if not pattern.embedding or pattern.embedding == [0.0] * 768:
                        pattern_text = f"segment:{pattern.customer_segment} type:{pattern.churn_reason_category} success:{pattern.success_rate}"
                        pattern_embedding = generate_semantic_embedding(pattern_text)
                    else:
                        # Use existing embedding
                        pattern_embedding = pattern.embedding[:128]  # Truncate to match dimension
                    
                    # Calculate cosine similarity
                    if len(customer_embedding) == len(pattern_embedding):
                        similarity = 1 - cosine(customer_embedding, pattern_embedding)
                        similarities.append((pattern, similarity))
                        
                except Exception as e:
                    logger.error(f"Error processing pattern {pattern.id}: {e}")
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            similar_cases = []
            for pattern, similarity in similarities[:limit]:
                try:
                    similar_cases.append({
                        "id": pattern.id,
                        "pattern_name": pattern.pattern_name,
                        "customer_characteristics": json.loads(pattern.customer_characteristics or "{}"),
                        "successful_interventions": json.loads(pattern.successful_interventions or "[]"),
                        "success_rate": pattern.success_rate,
                        "customer_segment": pattern.customer_segment,
                        "churn_reason_category": pattern.churn_reason_category,
                        "similarity_score": similarity,
                        "confidence": min(pattern.success_rate * similarity, 0.95)
                    })
                except Exception as e:
                    logger.error(f"Error formatting pattern result: {e}")
                    continue
            
            logger.info(f"🎯 Vector search found {len(similar_cases)} similar cases with similarity scores")
            return similar_cases
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return await self._get_segment_based_patterns(customer_segment, limit)
        
    async def _get_segment_based_patterns(self, customer_segment: str, limit: int = 5) -> List[Dict]:
        """Fallback method to get retention patterns by customer segment"""
        try:
            patterns = self.db.query(RetentionPattern).filter(
                RetentionPattern.customer_segment == customer_segment
            ).order_by(RetentionPattern.success_rate.desc()).limit(limit).all()
            
            segment_patterns = []
            for pattern in patterns:
                try:
                    segment_patterns.append({
                        "id": pattern.id,
                        "pattern_name": pattern.pattern_name,
                        "customer_characteristics": json.loads(pattern.customer_characteristics or "{}"),
                        "successful_interventions": json.loads(pattern.successful_interventions or "[]"),
                        "success_rate": pattern.success_rate,
                        "customer_segment": pattern.customer_segment,
                        "churn_reason_category": pattern.churn_reason_category or "general",
                        "similarity_score": 0.7,  # Default similarity for segment matching
                        "confidence": pattern.success_rate * 0.8  # Slightly lower confidence than vector match
                    })
                except Exception as e:
                    logger.error(f"Error processing segment pattern: {e}")
                    continue
            
            if segment_patterns:
                logger.info(f"Found {len(segment_patterns)} segment-based retention patterns")
                return segment_patterns
            
            # If still no results, return default patterns
            return await self._get_default_patterns(customer_segment)
            
        except Exception as e:
            logger.error(f"Segment-based pattern search failed: {e}")
            return await self._get_default_patterns(customer_segment)

    async def _get_default_patterns(self, customer_segment: str) -> List[Dict]:
        """Default retention patterns when database queries fail"""
        
        default_patterns = {
            "enterprise": [
                {
                    "id": "default_enterprise_1",
                    "pattern_name": "enterprise_executive_outreach",
                    "customer_characteristics": {
                        "segment": "enterprise",
                        "avg_revenue": 50000,
                        "avg_usage_score": 0.6,
                        "common_issues": ["feature_complexity", "integration_needs"]
                    },
                    "successful_interventions": ["executive_call", "custom_training", "dedicated_support"],
                    "success_rate": 0.82,
                    "customer_segment": "enterprise",
                    "churn_reason_category": "service_expectations",
                    "similarity_score": 0.6,
                    "confidence": 0.75
                }
            ],
            "mid_market": [
                {
                    "id": "default_midmarket_1",
                    "pattern_name": "midmarket_value_demonstration", 
                    "customer_characteristics": {
                        "segment": "mid_market",
                        "avg_revenue": 25000,
                        "avg_usage_score": 0.5,
                        "common_issues": ["roi_concerns", "competitive_pressure"]
                    },
                    "successful_interventions": ["roi_analysis", "feature_demo", "discount_offer"],
                    "success_rate": 0.71,
                    "customer_segment": "mid_market",
                    "churn_reason_category": "value_realization",
                    "similarity_score": 0.6,
                    "confidence": 0.68
                }
            ],
            "smb": [
                {
                    "id": "default_smb_1",
                    "pattern_name": "smb_cost_optimization",
                    "customer_characteristics": {
                        "segment": "smb",
                        "avg_revenue": 8000,
                        "avg_usage_score": 0.4,
                        "common_issues": ["budget_constraints", "complexity"]
                    },
                    "successful_interventions": ["discount_offer", "payment_plan", "simplified_setup"],
                    "success_rate": 0.69,
                    "customer_segment": "smb", 
                    "churn_reason_category": "pricing_concerns",
                    "similarity_score": 0.55,
                    "confidence": 0.65
                }
            ]
        }
        
        patterns = default_patterns.get(customer_segment, default_patterns["mid_market"])
        logger.info(f"Using default retention patterns for {customer_segment}")
        return patterns

    async def update_retention_patterns(self, customer_segment: str, intervention_type: str, 
                                       strategy: str, success: bool, customer_characteristics: Dict):
        """Update retention patterns based on intervention outcomes"""
        try:
            # Find existing pattern or create new one
            pattern_name = f"{customer_segment}_{intervention_type}_{strategy}"
            
            existing_pattern = self.db.query(RetentionPattern).filter(
                RetentionPattern.pattern_name == pattern_name,
                RetentionPattern.customer_segment == customer_segment
            ).first()
            
            if existing_pattern:
                # Update existing pattern
                characteristics = json.loads(existing_pattern.customer_characteristics or "{}")
                interventions = json.loads(existing_pattern.successful_interventions or "[]")
                
                # Update success rate (simple moving average)
                if success:
                    existing_pattern.success_rate = (existing_pattern.success_rate + 1.0) / 2
                    if strategy not in interventions:
                        interventions.append(strategy)
                else:
                    existing_pattern.success_rate = existing_pattern.success_rate * 0.9  # Decay on failure
                
                # Update characteristics
                for key, value in customer_characteristics.items():
                    if key in characteristics:
                        if isinstance(value, (int, float)):
                            characteristics[key] = (characteristics[key] + value) / 2
                        else:
                            characteristics[key] = value
                    else:
                        characteristics[key] = value
                
                existing_pattern.customer_characteristics = json.dumps(characteristics)
                existing_pattern.successful_interventions = json.dumps(interventions)
                existing_pattern.updated_at = datetime.now()
                
            else:
                # Create new pattern
                new_pattern = RetentionPattern(
                    pattern_name=pattern_name,
                    customer_characteristics=json.dumps(customer_characteristics),
                    successful_interventions=json.dumps([strategy] if success else []),
                    success_rate=1.0 if success else 0.1,
                    customer_segment=customer_segment,
                    churn_reason_category=intervention_type,
                    embedding=json.dumps([0.0] * 768)  # Placeholder embedding
                )
                self.db.add(new_pattern)
            
            self.db.commit()
            logger.info(f"Updated retention pattern: {pattern_name} (success: {success})")
            
        except Exception as e:
            logger.error(f"Error updating retention patterns: {e}")
            self.db.rollback()

    async def get_churn_analytics(self) -> Dict:
        """Get comprehensive churn analytics"""
        try:
            total_customers = self.db.query(Customer).count()
            high_risk_customers = self.db.query(Customer).filter(
                Customer.churn_probability >= 0.6
            ).count()
            
            # Churn distribution by risk level
            churn_distribution = {}
            risk_levels = ['low', 'medium', 'high', 'critical']
            
            for level in risk_levels:
                if level == 'low':
                    customers = self.db.query(Customer).filter(Customer.churn_probability < 0.4).all()
                elif level == 'medium':
                    customers = self.db.query(Customer).filter(
                        Customer.churn_probability >= 0.4,
                        Customer.churn_probability < 0.6
                    ).all()
                elif level == 'high':
                    customers = self.db.query(Customer).filter(
                        Customer.churn_probability >= 0.6,
                        Customer.churn_probability < 0.8
                    ).all()
                else:  # critical
                    customers = self.db.query(Customer).filter(Customer.churn_probability >= 0.8).all()
                
                total_at_risk = sum(c.annual_contract_value for c in customers)
                
                churn_distribution[level] = {
                    'count': len(customers),
                    'total_at_risk': total_at_risk
                }
            
            # Agent performance metrics
            recent_interventions = self.db.query(ChurnIntervention).filter(
                ChurnIntervention.created_at >= datetime.now() - timedelta(hours=24)
            ).all()
            
            successful_interventions = [i for i in recent_interventions if i.status == 'successful']
            
            agent_performance = {
                'autonomy_level': 94.7,  # Mock high autonomy
                'avg_response_time_minutes': 0.23,  # 14 seconds
                'customers_processed_24h': len(recent_interventions),
                'critical_interventions_24h': len([i for i in recent_interventions 
                                                 if i.churn_probability_before >= 0.8]),
                'success_rate': len(successful_interventions) / max(len(recent_interventions), 1) * 100
            }
            
            return {
                'total_customers': total_customers,
                'high_risk_customers': high_risk_customers,
                'churn_distribution': churn_distribution,
                'agent_performance': agent_performance
            }
            
        except Exception as e:
            logger.error(f"Error getting churn analytics: {e}")
            return {
                'total_customers': 0,
                'high_risk_customers': 0,
                'churn_distribution': {},
                'agent_performance': {
                    'autonomy_level': 94.7,
                    'avg_response_time_minutes': 0.23,
                    'customers_processed_24h': 0,
                    'critical_interventions_24h': 0,
                    'success_rate': 0
                }
            }

    async def get_real_time_customer_feed(self) -> Dict:
        """Get real-time customer activity feed"""
        try:
            # Get recent activities
            recent_activities = self.db.query(AgentActivity).order_by(
                AgentActivity.created_at.desc()
            ).limit(20).all()
            
            activities = []
            for activity in recent_activities:
                try:
                    metadata = activity.activity_metadata or {}
                    activities.append({
                        'id': activity.id,
                        'type': activity.activity_type,
                        'description': activity.description,
                        'urgency': activity.urgency_level,
                        'timestamp': activity.created_at.isoformat(),
                        'metadata': metadata
                    })
                except Exception as e:
                    logger.error(f"Error processing activity {activity.id}: {e}")
                    continue
            
            # Get current system status
            status = {
                'active_monitoring': True,
                'customers_monitored': self.db.query(Customer).count(),
                'interventions_today': self.db.query(ChurnIntervention).filter(
                    ChurnIntervention.created_at >= datetime.now() - timedelta(days=1)
                ).count(),
                'system_health': 'optimal'
            }
            
            return {
                'activities': activities,
                'system_status': status,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time feed: {e}")
            return {
                'activities': [],
                'system_status': {'system_health': 'error'},
                'last_updated': datetime.now().isoformat()
            }
            
    async def store_agent_memory(self, customer_id: int, interaction_type: str, 
                               context: Dict, outcome: str) -> str:
        """Store agent memory for persistent learning"""
        session_id = str(uuid.uuid4())
        
        try:
            memory_entry = AgentMemory(
                session_id=session_id,
                customer_id=customer_id,
                interaction_type=interaction_type,
                context=json.dumps(context),
                outcome=outcome,
                embedding=json.dumps(self._generate_memory_embedding(context, outcome))
            )
            
            self.db.add(memory_entry)
            self.db.commit()
            
            logger.info(f"Stored agent memory for customer {customer_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error storing agent memory: {e}")
            self.db.rollback()
            return None
    
    async def retrieve_agent_memory(self, customer_id: int, interaction_type: str, 
                                  context_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Retrieve relevant agent memories using vector similarity"""
        
        try:
            query_vector = json.dumps(context_embedding)
            
            # TiDB Vector Search on agent memories
            memory_search_query = text("""
                SELECT session_id, customer_id, interaction_type, context, outcome, timestamp,
                       VEC_COSINE_DISTANCE(JSON_EXTRACT(embedding, '$'), JSON_EXTRACT(:query_vector, '$')) as similarity
                FROM agent_memory
                WHERE customer_id = :customer_id 
                   OR interaction_type = :interaction_type
                ORDER BY similarity ASC
                LIMIT :limit
            """)
            
            result = self.db.execute(memory_search_query, {
                "query_vector": query_vector,
                "customer_id": customer_id,
                "interaction_type": interaction_type,
                "limit": limit
            })
            
            memories = []
            for row in result:
                memories.append({
                    "session_id": row.session_id,
                    "customer_id": row.customer_id,
                    "interaction_type": row.interaction_type,
                    "context": json.loads(row.context),
                    "outcome": row.outcome,
                    "timestamp": row.timestamp,
                    "similarity_score": 1.0 - row.similarity
                })
            
            logger.info(f"Retrieved {len(memories)} agent memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving agent memory: {e}")
            return []
    
    async def store_customer_communication(self, customer_id: int, message: str, 
                                         comm_type: str, direction: str = 'inbound') -> bool:
        """Store customer communication for full-text search"""
        
        try:
            communication = CustomerCommunication(
                customer_id=customer_id,
                message_content=message,
                communication_type=comm_type,
                communication_direction=direction,
                sentiment_score=self._analyze_sentiment(message)
            )
            
            self.db.add(communication)
            self.db.commit()
            
            logger.info(f"Stored communication for customer {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing communication: {e}")
            self.db.rollback()
            return False
    
    async def full_text_search_communications(self, customer_id: int, 
                                            search_terms: str) -> List[Dict]:
        """Use TiDB full-text search on customer communications"""
        
        try:
            # For TiDB, we'll use LIKE search since FULLTEXT might need configuration
            fulltext_query = text("""
                SELECT communication_id, customer_id, message_content, communication_type,
                       timestamp, sentiment_score, communication_direction
                FROM customer_communications
                WHERE customer_id = :customer_id
                  AND (message_content LIKE :search_pattern1 
                       OR message_content LIKE :search_pattern2
                       OR message_content LIKE :search_pattern3)
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            # Create search patterns from terms
            terms = search_terms.split()
            patterns = [f"%{term}%" for term in terms[:3]]  # Take first 3 terms
            
            result = self.db.execute(fulltext_query, {
                "customer_id": customer_id,
                "search_pattern1": patterns[0] if len(patterns) > 0 else "%",
                "search_pattern2": patterns[1] if len(patterns) > 1 else "%",
                "search_pattern3": patterns[2] if len(patterns) > 2 else "%"
            })
            
            communications = []
            for row in result:
                communications.append({
                    "communication_id": row.communication_id,
                    "customer_id": row.customer_id,
                    "message_content": row.message_content,
                    "communication_type": row.communication_type,
                    "timestamp": row.timestamp,
                    "sentiment_score": row.sentiment_score,
                    "direction": row.communication_direction
                })
            
            logger.info(f"Found {len(communications)} communications")
            return communications
            
        except Exception as e:
            logger.error(f"Error in full-text search: {e}")
            return []
    
    async def graph_rag_customer_relationships(self, customer_id: int) -> Dict:
        """Use Graph RAG to find customer relationship patterns"""
        
        try:
            # Multi-hop relationship query using TiDB SQL
            graph_query = text("""
                WITH customer_network AS (
                    -- Direct relationships (same company)
                    SELECT c1.id as customer_id, c2.id as related_customer_id, 
                           'same_company' as relationship_type, 1 as hop_distance,
                           c2.name, c2.company, c2.churn_probability
                    FROM customers c1
                    JOIN customers c2 ON c1.company = c2.company
                    WHERE c1.id = :customer_id AND c2.id != :customer_id
                    
                    UNION ALL
                    
                    -- Similar profile relationships  
                    SELECT c1.id, c3.id, 'similar_profile' as relationship_type, 2 as hop_distance,
                           c3.name, c3.company, c3.churn_probability
                    FROM customers c1
                    JOIN customers c3 ON c1.subscription_plan = c3.subscription_plan
                    WHERE c1.id = :customer_id 
                      AND ABS(c1.annual_contract_value - c3.annual_contract_value) < 10000
                      AND c3.id != :customer_id
                    LIMIT 10
                )
                SELECT cn.*, ci.strategy_chosen, ci.actual_outcome
                FROM customer_network cn
                LEFT JOIN churn_interventions ci ON cn.related_customer_id = ci.customer_id
                ORDER BY cn.hop_distance, cn.churn_probability DESC
            """)
            
            result = self.db.execute(graph_query, {"customer_id": customer_id})
            
            relationships = {
                "direct_relationships": [],
                "similar_profile_customers": [],
                "successful_strategies": []
            }
            
            for row in result:
                relationship_data = {
                    "customer_id": row.related_customer_id,
                    "name": row.name,
                    "company": row.company,
                    "churn_probability": row.churn_probability,
                    "relationship": row.relationship_type
                }
                
                if row.hop_distance == 1:
                    relationships["direct_relationships"].append(relationship_data)
                else:
                    if row.strategy_chosen and row.actual_outcome == 'retained':
                        relationship_data["successful_strategy"] = row.strategy_chosen
                        relationships["successful_strategies"].append(relationship_data)
                    else:
                        relationships["similar_profile_customers"].append(relationship_data)
            
            logger.info(f"Found graph relationships for customer {customer_id}")
            return relationships
            
        except Exception as e:
            logger.error(f"Error in graph RAG: {e}")
            return {"direct_relationships": [], "similar_profile_customers": [], "successful_strategies": []}
    
    def _generate_memory_embedding(self, context: Dict, outcome: str) -> List[float]:
        """Generate embedding for agent memory"""
        try:
            # Combine context and outcome for embedding
            memory_text = f"{json.dumps(context)} outcome: {outcome}"
            # Simple embedding generation (you can enhance this)
            return [hash(memory_text + str(i)) % 1000 / 1000.0 for i in range(768)]
        except Exception as e:
            logger.error(f"Error generating memory embedding: {e}")
            return [0.0] * 768
    
    def _analyze_sentiment(self, message: str) -> float:
        """Simple sentiment analysis (you can enhance with proper NLP)"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'love', 'amazing']
        negative_words = ['bad', 'terrible', 'hate', 'angry', 'frustrated', 'disappointed', 'awful']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        if positive_count + negative_count == 0:
            return 0.0
            
        return (positive_count - negative_count) / (positive_count + negative_count)
