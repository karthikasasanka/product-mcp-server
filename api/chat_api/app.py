import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat_api.init import initialize_routers
from chat_api.classifier.csv_classifier import CSVBasedClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global CSV classifier instance
csv_classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Chat API application...")
    
    # Load CSV classifier model at startup
    global csv_classifier
    try:
        logger.info("📂 Loading CSV classifier model at startup...")
        csv_classifier = CSVBasedClassifier()
        csv_classifier.load_model()
        logger.info("✅ CSV classifier model loaded successfully")
        
        # Store in app state for access by endpoints
        app.state.csv_classifier = csv_classifier
    except Exception as e:
        logger.error(f"❌ Failed to load CSV classifier model: {e}")
        # Don't fail the app startup, just log the error
    
    logger.info("✅ Chat API application started successfully")
    yield
    # Shutdown (if needed)
    logger.info("🛑 Shutting down Chat API application...")


def create_app() -> FastAPI:
    logger.info("🔧 Creating Chat API FastAPI application...")
    server = FastAPI(
        docs_url="/", 
        title="AI Chat Service",
        lifespan=lifespan
    )

    # Add CORS middleware
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    logger.info("📋 Initializing routers...")
    initialize_routers(server=server)
    logger.info("✅ Chat API application created successfully")

    return server
