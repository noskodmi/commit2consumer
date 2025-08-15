import os
from dotenv import load_dotenv

# Load .env file if present (useful for local dev)
load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    
    # Blockchain settings
    MANTLE_PRIVATE_KEY: str = os.getenv("MANTLE_PRIVATE_KEY", "")
    MANTLE_RPC_URL: str = os.getenv("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "5003"))  # Mantle Sepolia
    
    # Storage settings
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
    
    # Environment
    PRODUCTION: bool = os.getenv("ENVIRONMENT", "development") == "production"
    
    # Validate required settings
    def validate(self):
        missing = []
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not self.MANTLE_PRIVATE_KEY:
            missing.append("MANTLE_PRIVATE_KEY")
        if not self.GITHUB_WEBHOOK_SECRET:
            missing.append("GITHUB_WEBHOOK_SECRET")
        
        return missing

settings = Settings()