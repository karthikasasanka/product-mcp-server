from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Product MCP Server"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()


