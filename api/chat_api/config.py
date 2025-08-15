from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MCP_SERVER_URL: str = "http://localhost:9000"
    OLLAMA_SERVER_URL: str = "http://localhost:11434"
    USE_FAST_FALLBACK: bool = True  # Enable fast rule-based fallback for sub-second responses


settings = Settings()
