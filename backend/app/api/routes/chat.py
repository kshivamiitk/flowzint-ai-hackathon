from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.application.chat_service import ChatOrchestrator
from app.application.dto import ChatResponse, MessageRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/messages", response_model=ChatResponse)
async def send_message(
    payload: MessageRequest,
    service: ChatOrchestrator = Depends(get_chat_service),
) -> ChatResponse:
    return await service.handle(payload)
