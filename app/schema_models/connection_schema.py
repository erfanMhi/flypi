from pydantic import BaseModel

class ComponentConnection(BaseModel):
    is_connected: bool 