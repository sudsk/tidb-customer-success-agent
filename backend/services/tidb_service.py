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
                    VEC_COSINE_DISTANCE(JSON_EXTRACT(rp.embedding, '# TiDB Autonomous Customer Success Agent - Complete MVP
