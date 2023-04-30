from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.card import router as card_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(card_router, tags=['card'])
