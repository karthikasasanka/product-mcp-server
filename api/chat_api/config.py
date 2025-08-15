from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MCP_SERVER_URL: str = "http://localhost:9000"
    OLLAMA_SERVER_URL: str = "http://localhost:11434"
    USE_FAST_FALLBACK: bool = True  # Enable fast rule-based fallback for sub-second responses
    
    # NLP Model Configuration
    NLP_MODEL_NAME: str = "llama3.1:8b"  # Default to llama3.1:8b
    NLP_TIMEOUT: float = 300.0  # Default to 5 minutes for llama3.1:8b
    NLP_TEMPERATURE: float = 0.0  # Default to deterministic


settings = Settings()
