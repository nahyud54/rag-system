"""Stage 4: Chat endpoints - complete RAG pipeline with WebSocket streaming"""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, WebSocketDisconnect
from fastapi.websockets import WebSocket
from pydantic import BaseModel

from dependencies import get_rag_chain

router = APIRouter(prefix="/chat", tags=["Chat"])

# In-memory session storage
sessions: dict = {}


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    top_k: Optional[int] = 5
    use_streaming: Optional[bool] = False


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    query: str
    answer: str
    sources: Optional[List[dict]] = None
    retrieved_count: int = 0
    timestamp: datetime
    metadata: Optional[dict] = None


def _get_or_create_session(session_id: Optional[str]) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = {"created_at": datetime.utcnow(), "messages": []}
    return sid


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest) -> ChatResponse:
    """Send a message and get a RAG-powered response."""
    session_id = _get_or_create_session(request.session_id)
    message_id = str(uuid.uuid4())

    rag = get_rag_chain()
    result = rag.run(request.query)

    msg_user = {"role": "user", "content": request.query, "timestamp": datetime.utcnow().isoformat()}
    msg_assistant = {
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", []),
        "timestamp": datetime.utcnow().isoformat(),
    }
    sessions[session_id]["messages"].extend([msg_user, msg_assistant])

    return ChatResponse(
        session_id=session_id,
        message_id=message_id,
        query=request.query,
        answer=result["answer"],
        sources=result.get("sources", []),
        retrieved_count=result.get("retrieved_count", 0),
        timestamp=datetime.utcnow(),
    )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming RAG responses token by token."""
    await websocket.accept()
    _get_or_create_session(session_id)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("query", "")

            if not query:
                await websocket.send_json({"type": "error", "message": "Empty query"})
                continue

            rag = get_rag_chain()

            # Retrieve + rerank first (non-streaming), then stream generation
            try:
                docs = rag._retrieve_and_rerank(query)
                if not docs:
                    await websocket.send_json({
                        "type": "done",
                        "answer": "Không tìm thấy thông tin liên quan.",
                        "sources": [],
                    })
                    continue

                context, ordered_docs = rag.context_preparer.prepare(docs)
                prompt = rag.llm.build_rag_prompt(query, context)

                full_answer = ""
                for token in rag.llm.stream(prompt):
                    full_answer += token
                    await websocket.send_json({"type": "token", "token": token})

                sources = [
                    {
                        "file": d.get("metadata", {}).get("file_name", ""),
                        "slide": d.get("metadata", {}).get("slide_number", ""),
                        "score": round(d.get("rerank_score", d.get("score", 0)), 3),
                        "preview": d["text"][:150],
                    }
                    for d in ordered_docs
                ]

                sessions[session_id]["messages"].extend([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": full_answer, "sources": sources},
                ])

                await websocket.send_json({"type": "done", "answer": full_answer, "sources": sources})

            except RuntimeError as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = sessions[session_id]["messages"][-limit:]
    return {"session_id": session_id, "messages": msgs, "total": len(msgs)}


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    sessions[session_id]["messages"] = []
    return {"status": "cleared"}


@router.get("/sessions")
async def list_sessions():
    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": s["created_at"],
                "message_count": len(s["messages"]),
            }
            for sid, s in sessions.items()
        ],
    }
