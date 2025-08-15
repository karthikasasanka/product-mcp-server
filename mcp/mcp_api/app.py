import logging
from fastapi import FastAPI, Request
import time
from mcp_api.config import settings
from mcp_api.product.views import router as product_router
from fastapi_mcp import FastApiMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    logger.info("🚀 Creating MCP server application...")
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        logger.info("🏥 Health check requested")
        return {"status": "healthy", "service": "mcp-api"}

    # Routers
    logger.info("📋 Including product router...")
    app.include_router(product_router, prefix="/products", tags=["products"])

    @app.middleware("http")
    async def log_request_time(request: Request, call_next):
        start = time.perf_counter()
        logger.info(f"📥 Incoming request: {request.method} {request.url}")
        logger.info(f"📋 Headers: {dict(request.headers)}")
        
        # Log request body if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    logger.info(f"📦 Request body: {body.decode()}")
            except Exception as e:
                logger.warning(f"⚠️ Could not read request body: {e}")
        
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(f"📤 Response: {response.status_code} (took {duration_ms:.1f}ms)")
        return response

    # Wrap FastAPI with MCP
    logger.info("🔗 Setting up MCP wrapper...")
    mcp = FastApiMCP(app)  # registers tools/endpoints with MCP
    mcp.mount_http(mount_path="/mcp")
    logger.info("✅ MCP server application created successfully")
    return app
