import uvicorn
from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    ssl_config = {}
    if settings.USE_HTTPS:
        ssl_config.update({
            'ssl_keyfile': settings.SSL_KEYFILE,
            'ssl_certfile': settings.SSL_CERTFILE
        })

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        **ssl_config
    ) 