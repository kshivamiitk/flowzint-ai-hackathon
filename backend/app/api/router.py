from fastapi import APIRouter

from app.api.routes import chat, customers, operations

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(customers.router)
api_router.include_router(operations.router)
