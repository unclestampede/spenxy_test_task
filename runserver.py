import uvicorn
from app import settings
from app.main import app


if __name__ == "__main__":
    uvicorn.run(app,
                host=settings.APP_HOST,
                port=settings.APP_PORT,
                reload=settings.RELOAD)
