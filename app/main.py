from fastapi import FastAPI
from app.api.endpoints import circuit
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Circuit Analysis API",
    description="API for analyzing electronic circuit components using computer vision",
    version="1.0.0"
)

# Include routers
app.include_router(circuit.router, prefix="/api/v1", tags=["circuit"]) 