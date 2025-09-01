# backend/services/tidb_service.py
import json
import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models.database import Customer, RetentionPattern, ChurnIntervention
import logging

logger = logging.getLogger(__name__)

class TiDBService:
    def __init__(self, db: Session):
        self.db = db
    
    async def find_similar_retention_cases(self, customer_embedding: List[float], 
                                         customer_segment: str, churn_probability: float, 
                                         limit: int = 5) -> List[Dict]:
        """Use TiDB vector search to find similar successful retention cases"""
        
        if not customer_embedding:
            logger.warning("No customer embedding provided, using segment-based matching")
            return await self._get_segment_based_patterns(customer_segment, limit)
        
        try:
            # Convert embedding to proper format for TiDB vector search
            query_vector = json.dumps(customer_embedding)
            
            # TiDB Vector Search Query - Find similar retention patterns
            vector_search_query = text("""
                SELECT 
                    rp.id,
                    rp.pattern_name,
                    rp.customer_characteristics,
                    rp.successful_interventions,
                    rp.success_rate,
                    rp.customer_segment,
                    rp.churn_reason_category,
                    VEC_COSINE_DISTANCE(JSON_EXTRACT(rp.embedding, '$'), JSON_EXTRACT(:query_vector, '$')) as similarity_distance
                FROM retention_patterns rp
                WHERE rp.customer_segment = :customer_segment
                    AND rp.success_rate > 0.5
                ORDER BY similarity_distance ASC
                LIMIT :limit
            """)
            
            # Execute vector search query
            result = self.db.execute(
                vector_search_query,
                {
                    "query_vector": query_vector,
                    "customer_segment": customer_segment,
                    "limit": limit
                }
            )
            
            similar_cases = []
            for row in result:
                try:
                    similar_cases.append({
                        "id": row.id,
                        "pattern_name": row.pattern_name,
                        "customer_characteristics": json.loads(row.customer_characteristics or "{}"),
                        "successful_interventions": json.loads(row.successful_interventions or "[]"),
                        "success_rate": row.success_rate,
                        "customer_segment": row.customer_segment,
                        "churn_reason_category": row.churn_reason_category,
                        "similarity_score": 1.0 - row.similarity_distance,  # Convert distance to similarity
                        "confidence": min(row.success_rate * (1.0 - row.similarity_distance), 0.95)
                    })
                except Exception as e:
                    logger.error(f"Error processing vector search result: {e}")
                    continue
            
            logger.info(f"Found {len(similar_cases)} similar retention cases using vector search")
            
            # If no vector results, fall back to segment-based matching
            if not similar_cases:
                logger.info("No vector matches found, falling back to segment-based patterns")
                return await self._get_segment_based_patterns(customer_segment, limit)
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            # Fallback to segment-based patterns
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
                },
                {
                    "id": "default_enterprise_2", 
                    "pattern_name": "enterprise_feature_adoption",
                    "customer_characteristics": {
                        "segment": "enterprise",
                        "avg_revenue": 75000,
                        "avg_usage_score": 0.4,
                        "common_issues": ["underutilization", "training_needs"]
                    },
                    "successful_interventions": ["feature_workshop", "success_manager_assignment", "implementation_support"],
                    "success_rate": 0.78,
                    "customer_segment": "enterprise",
                    "churn_reason_category": "underutilization",
                    "similarity_score": 0.65,
                    "confidence": 0.72
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
