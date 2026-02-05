import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from backend.models.exercise import ExerciseCollection
from backend.models.roster import MAPPING_EIGHT_HOURS_SHIFT, Roster
from backend.models.data import PERSONNELS_DATA
from backend.models.personal import Personnel
from backend.models.sleep import SleepCollection
from ..schemas.chat import ChatRequest, ChatResponse, GraphRAGChatbot, RagChatbotError, UserInfoRetrievalError, ResponseGenerationError

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat(request: ChatRequest) -> ChatResponse:
    """
        Handle chat requests using GraphRAG chatbot.

        **Args:**
        * `request` (ChatRequest): The chat request containing user ID and message.

        **Returns:**
        * `ChatResponse`: The chat response containing the generated answer.

        **Raises:**
        * `HTTPException`: If there are errors during processing.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
        # Initialise RAG component
    rag = GraphRAGChatbot()

    # TODO: Fetch message history if needed (using request.user_id)
    messages = []

    # TODO: We use static definitions to fetch roster_info and personal_info for now
    person: Personnel = PERSONNELS_DATA.get(request.user_id, None)

    if not person:
        raise UserInfoRetrievalError(f"User info not found for user_id: {request.user_id}")

    roster_info: Roster = person.roster_info
    exercise_info: ExerciseCollection = person.exercise_info
    sleep_info: SleepCollection = person.sleep_info

    # Parse roster, exercise, and sleep info to string formats (JSON)
    roster_info_json = roster_info.model_dump_json() if roster_info else ""
    exercise_info_json = exercise_info.exercise_summary.model_dump_json() if exercise_info and exercise_info.exercise_summary else ""
    sleep_info_json = sleep_info.summary.model_dump_json() if sleep_info and sleep_info.summary else ""
    # Perform RAG search
    rag_response = None
    print("Performing RAG chat...")
    try:
        rag_response = rag.chat(
            current_query=request.message,
            messages=messages,
            roster_info=roster_info_json,
            exercise_info=exercise_info_json,
            sleep_info=sleep_info_json,
        )
    except RagChatbotError as e: 
        raise HTTPException(status_code=500, detail=str(e))
    
    if rag_response and rag_response.answer:
        return ChatResponse(timestamp=datetime.now().isoformat(),response=rag_response.answer)

    return ChatResponse(timestamp=datetime.now().isoformat(),response="")


@router.get("/history")
async def get_chat_history():
    """Get chat history."""
    # TODO: Implement chat history retrieval
    return {"messages": []}