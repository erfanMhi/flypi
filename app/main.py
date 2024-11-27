"""
Main application module for Circuit Analysis API.

This module initializes the FastAPI application, sets up middleware,
logging, and telemetry configuration.
"""
import os
import sys
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from openinference.instrumentation.groq import GroqInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

from app.api.endpoints import circuit_components, circuit_schema, health
from app.core.exceptions import ConfigurationError

# Constants
PHOENIX_ENDPOINT: str = "http://localhost:4317"
PROJECT_NAME: str = "llm-service"
API_VERSION: str = "v0"
API_PREFIX: str = f"/api/{API_VERSION}"

def setup_telemetry() -> None:
    """Initialize telemetry and instrumentation."""
    register(
        project_name=PROJECT_NAME,
        endpoint=PHOENIX_ENDPOINT
    )
    LiteLLMInstrumentor().instrument()
    GroqInstrumentor().instrument()
    OpenAIInstrumentor().instrument()

def configure_logging() -> None:
    """Configure logging handlers and formats."""
    logger.configure(
        handlers=[
            {
                "sink": "logs/app.log",
                "rotation": "500 MB",
                "format": "{time} | {level} | {message}",
                "level": "DEBUG"
            },
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                         "<level>{level}</level> | <level>{message}</level>",
                "level": "INFO"
            }
        ]
    )

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Circuit Analysis API",
        description="API for analyzing electronic circuit components "
                   "using computer vision",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(
        circuit_components.router, 
        prefix=API_PREFIX, 
        tags=["circuit"]
    )
    app.include_router(
        circuit_schema.router, 
        prefix=API_PREFIX, 
        tags=["circuit"]
    )
    app.include_router(
        health.router, 
        prefix=API_PREFIX, 
        tags=["health"]
    )

    return app

def verify_environment() -> None:
    """
    Verify required environment variables are set.

    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    required_vars = ["GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    logger.info("Environment variables verified successfully")

# Application initialization
load_dotenv(override=True)
verify_environment()
setup_telemetry()
configure_logging()
app = create_application()