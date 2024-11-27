from fastapi import APIRouter

router = APIRouter()

@router.get("/health/test-connection")
async def test_connection():
    """Health check endpoint to verify API connectivity"""
    return {"message": "Connection successful"} 