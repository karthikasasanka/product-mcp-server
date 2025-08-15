from fastapi import FastAPI
from chat_api.chat.views import chat_router


def initialize_routers(server: FastAPI):
    server.include_router(chat_router, prefix="/chat", tags=["Chat"])