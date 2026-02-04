from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message and get a response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Initalise GraphRAG pipeline object and trigger method to handle request

    
    return ChatResponse(response="")


@router.get("/history")
async def get_chat_history():
    """Get chat history."""
    # TODO: Implement chat history retrieval
    return {"messages": []}