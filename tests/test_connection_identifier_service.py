import pytest
import os
from app.services.component_identifier_service import ComponentIdentifierService
from app.services.connection_identifier_service import ConnectionIdentifierService

@pytest.fixture
def component_identifier():
    return ComponentIdentifierService()

@pytest.fixture
def connection_identifier():
    return ConnectionIdentifierService()

@pytest.fixture
def test_image_bytes():
    # Get the absolute path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "circuit.png")
    image_path = 'circuit.png'
    
    # Ensure the image exists
    assert os.path.exists(image_path), f"Test image not found at {image_path}"
    
    # Read the image bytes
    with open(image_path, "rb") as f:
        return f.read()

@pytest.mark.asyncio
async def test_identify_connections(component_identifier, connection_identifier, test_image_bytes):
    """
    Test that the ConnectionIdentifierService correctly identifies connections
    between components in a circuit diagram.
    """
    # First: Identify components in the circuit
    components = await component_identifier.identify_components(test_image_bytes)
    
    # Then: Identify connections between components
    connections = await connection_identifier.identify_connections(components, test_image_bytes)
    
    print('connections: ', connections)
    # Verify we have exactly one connection
    assert isinstance(connections, list), "Connections should be a list"
    assert len(connections) == 1, "Should have identified exactly one connection"
    
    connection = connections[0]
    # Verify the single connection has the correct structure
    assert "component1" in connection, "Connection missing component1"
    assert "component2" in connection, "Connection missing component2"
    assert "connected" in connection, "Connection missing connected status"
    assert connection["connected"] is True, "Connection should be True"
    
    # Verify both components are present in the components list
    assert connection["component1"] in components, f"Unknown component: {connection['component1']}"
    assert connection["component2"] in components, f"Unknown component: {connection['component2']}" 