import os
import sys

import pytest
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def pytest_configure(config) -> None:
    """
    Called before tests are collected and run.

    This function loads environment variables from the .env file and verifies
    that the GROQ_API_KEY is present in the environment variables.
    
    Args:
        config: The pytest configuration object.
    
    Raises:
        SystemExit: If GROQ_API_KEY is not found in environment variables.
    """
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Verify GROQ_API_KEY is loaded
    if not os.getenv("GROQ_API_KEY"):
        pytest.exit("GROQ_API_KEY not found in environment variables")