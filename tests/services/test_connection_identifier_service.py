import os

import pytest
from unittest.mock import AsyncMock
from loguru import logger

from app.services.component_identifier_service import ComponentIdentifierService
from app.services.connection_identifier_service import ConnectionIdentifierService
from app.services.llm_client import LLMService
from app.core.config import get_settings


@pytest.fixture
def component_identifier() -> ComponentIdentifierService:
    """Fixture for creating a ComponentIdentifierService instance."""
    settings = get_settings()
    llm_service = LLMService(settings)
    return ComponentIdentifierService(settings, llm_service)


@pytest.fixture
def connection_identifier() -> ConnectionIdentifierService:
    """Fixture for creating a ConnectionIdentifierService instance."""
    settings = get_settings()
    llm_service = LLMService(settings)
    return ConnectionIdentifierService(settings, llm_service)


@pytest.fixture
def test_image_bytes() -> bytes:
    """Fixture for loading test image bytes."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)
    image_path = os.path.join(current_dir, "benchmarks/images/v0/circuit_9.png")

    assert os.path.exists(image_path), f"Test image not found at {image_path}"

    with open(image_path, "rb") as f:
        return f.read()


@pytest.mark.asyncio
async def test_identify_connections(
    component_identifier: ComponentIdentifierService,
    connection_identifier: ConnectionIdentifierService,
    test_image_bytes: bytes
) -> None:
    """
    Test the ConnectionIdentifierService for identifying connections between
    components in a circuit diagram.

    This test verifies that the service processes inputs and produces outputs
    without errors. It does not validate the output against any labeled data.
    """
    component_identifier.identify_components = AsyncMock(return_value=[
        {"id": "R1", "type": "resistor"},
        {"id": "B1", "type": "battery"}
    ])

    components = await component_identifier.identify_components(test_image_bytes)
    connections = await connection_identifier.identify_connections(
        components, test_image_bytes
    )

    logger.info("connections: %s", connections)

    assert isinstance(connections, list), "Connections should be a list"
    connection = connections[0]
    assert "component" in connection
    assert "connections" in connection
