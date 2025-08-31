# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # TiDB Configuration
    TIDB_HOST = os.getenv("TIDB_HOST", "gateway01.us-west-2.prod.aws.tidbcloud.com")
    TIDB_PORT = int(os.getenv("TIDB_PORT", 4000))
    TIDB_USER = os.getenv("TIDB_USER", "your_user")
    TIDB_PASSWORD = os.getenv("TIDB_PASSWORD", "your_password")
    TIDB_DATABASE = os.getenv("TIDB_DATABASE", "customer_success_agent")
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-key")
    
    # Agent Configuration
    AGENT_UPDATE_INTERVAL = 15  # seconds - faster for customer success
    VECTOR_DIMENSIONS = 768
    CHURN_THRESHOLD = 0.75  # 75% churn probability triggers intervention
    
    # Business Configuration
    HIGH_VALUE_THRESHOLD = 10000  # $10K+ annual value = high value customer
    INTERVENTION_TIMEOUT = 300  # 5 minutes to attempt intervention
    
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.TIDB_USER}:{self.TIDB_PASSWORD}@{self.TIDB_HOST}:{self.TIDB_PORT}/{self.TIDB_DATABASE}?ssl_verify_cert=true&ssl_verify_identity=true"

config = Config()
