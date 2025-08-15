import os
from dotenv import load_dotenv

# Load .env file if present (useful for local dev)
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MANTLE_PRIVATE_KEY: str = os.getenv("MANTLE_PRIVATE_KEY", "")
    MANTLE_RPC_URL: str = os.getenv(
        "MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz"
    )
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "5003"))  # Mantle Sepolia

settings = Settings()