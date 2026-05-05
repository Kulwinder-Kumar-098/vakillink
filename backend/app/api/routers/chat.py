"""
chat.py — AI chat sessions (REST) + lawyer↔client real-time WebSocket
======================================================================

REST routes (prefix: /api/v1/chat)
-----------------------------------
  POST /           – submit a legal query to the RAG pipeline
  GET  /sessions   – list all AI chat sessions for the current user
  GET  /sessions/{session_id} – full message history for one session

WebSocket route
---------------
  WS /ws/{consultation_id}
  → canonical URL: ws://host/api/v1/chat/ws/{consultation_id}

  consultation_id is the UUID of the consultation.

Authentication
--------------
  The WS endpoint cannot use the HTTP Authorization header, so the client
  must pass the Supabase JWT as a query parameter:
      ws://host/api/v1/chat/ws/{consultation_id}?token=<vl_token>
  The token is verified via supabase.auth.get_user() before accepting the
  upgrade.  An invalid/missing token causes an immediate close(4001).
"""

import json
import logging
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()


# ──────────────────────────────────────────────────────────────────────────────
# In-memory connection registry
# ──────────────────────────────────────────────────────────────────────────────
#
#  WHY THIS IS FINE FOR A HACKATHON / MVP
#  ───────────────────────────────────────
#  • Single-process: Uvicorn runs one process by default (or a handful of
#    workers).  All WebSocket connections for a given room land in the same
#    process → the same dict → broadcast works perfectly.
#  • Zero dependencies: no Redis, no message broker, no extra infra to spin up
#    or pay for during a demo.
#  • Stateless per request: each WS connection holds its own state; the dict
#    is just a lookup table.
#  • Memory is negligible: a room entry is a list of WebSocket objects (each
#    ~few KB).  Even 1 000 concurrent connections barely register.
#
#  WHAT REPLACES IT IN PRODUCTION
#  ────────────────────────────────
#  The moment you run ≥2 Uvicorn workers or deploy to multiple pods/instances,
#  connections for the same room spread across processes and the dict no longer
#  holds the full picture.  You need a shared pub/sub bus:
#
#  1. Redis Pub/Sub (most common)
#       – Each worker subscribes to the channel "room:{room_id}".
#       – On new message: publish to Redis; every subscribed worker receives
#         it and pushes it to its local WebSocket connections.
#       – Libraries: aioredis, redis-py (async), or Broadcaster.
#
#  2. Redis Streams / Kafka
#       – Better durability and replay guarantees; useful when you also want
#         message persistence and exactly-once delivery semantics.
#
#  3. Supabase Realtime (already in your stack!)
#       – Supabase exposes a Phoenix Channels (Elixir) based realtime layer.
#       – The frontend can subscribe directly to the `chat_messages` table
#         changes for a specific room_id using supabase-js `channel()`.
#       – Backend just inserts; Supabase Realtime fans out to every subscriber
#         automatically — zero custom broadcast code needed.
#       – This is the recommended production path for a Supabase-backed app.

class _RoomRegistry:
    """Thread-safe-enough in-memory registry for a single-process server."""

    def __init__(self):
        # consultation_id → list[WebSocket]
        self._rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, ws: WebSocket, consultation_id: str) -> None:
        await ws.accept()
        self._rooms[consultation_id].append(ws)
        logger.info("WS connected  consultation=%s  total=%d", consultation_id, len(self._rooms[consultation_id]))

    def disconnect(self, ws: WebSocket, consultation_id: str) -> None:
        room = self._rooms.get(consultation_id, [])
        if ws in room:
            room.remove(ws)
        logger.info("WS disconnect consultation=%s  remaining=%d", consultation_id, len(room))
        # Clean up empty rooms to avoid memory leak over time
        if not room:
            self._rooms.pop(consultation_id, None)

    async def broadcast(self, consultation_id: str, payload: dict) -> None:
        """Push JSON to every live connection in a room; drop dead sockets."""
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(consultation_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, consultation_id)


registry = _RoomRegistry()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _assert_consultation_member(user_id: str, consultation_id: str) -> None:
    """
    Validate that user_id is one of the two participants in the consultation.
    """
    client = supabase.get_admin_client()
    response = client.table("consultations").select("client_id, lawyer_id").eq("id", consultation_id).execute()
    if not response.data:
        raise PermissionError("Consultation not found")
    
    consultation = response.data[0]
    if user_id not in (consultation.get("client_id"), consultation.get("lawyer_id")):
        raise PermissionError("Not a consultation member")


def _fetch_history(consultation_id: str, limit: int = 50) -> list[dict]:
    """Fetch the last `limit` messages for a consultation, ordered oldest-first."""
    client = supabase.get_admin_client()
    response = (
        client.table("chat_messages")
        .select("id, consultation_id, sender_id, message, created_at")
        .eq("consultation_id", consultation_id)
        .order("created_at", desc=True)   # newest first so we get the right 50
        .limit(limit)
        .execute()
    )
    messages = list(reversed(response.data or []))  # flip back to chronological
    return messages


def _save_message(consultation_id: str, sender_id: str, message: str) -> dict:
    """Persist a chat message and return the saved row."""
    client = supabase.get_admin_client()
    payload = {
        "consultation_id": consultation_id,
        "sender_id":       sender_id,
        "message":         message.strip(),
    }
    response = client.table("chat_messages").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Failed to persist message")
    return response.data[0]


# ──────────────────────────────────────────────────────────────────────────────
# Existing REST endpoints (unchanged)
# ──────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


@router.post("/", summary="Submit a legal query to the RAG pipeline")
def submit_rag_query(request: ChatRequest, user=Depends(get_current_user)):
    """
    Authenticated endpoint.  Runs the query through the RAG pipeline,
    saves both the user message and the AI response, returns the answer
    with citations and the session_id.
    """
    return chat_service.process_query(
        user_id=user.id,
        query=request.query,
        session_id=request.session_id,
    )


@router.get("/sessions", summary="List all AI chat sessions for the current user")
def get_sessions(user=Depends(get_current_user)):
    return chat_service.get_user_sessions(user_id=user.id)


@router.get("/sessions/{session_id}", summary="Get full message history for a session")
def get_session_history(session_id: str, user=Depends(get_current_user)):
    return chat_service.get_session_messages(session_id=session_id, user_id=user.id)


# ──────────────────────────────────────────────────────────────────────────────
# WebSocket endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.websocket("/ws/{consultation_id}")
async def ws_chat(
    websocket: WebSocket,
    consultation_id: str,
    token: Optional[str] = Query(
        None,
        alias="token",
        description="Supabase JWT (vl_token) — required for WS auth",
    ),
):
    """
    Real-time lawyer ↔ client chat over WebSocket.

    URL pattern
    -----------
        ws://host/api/v1/chat/ws/{consultation_id}?token=<vl_token>

    Lifecycle
    ---------
    1. AUTHENTICATE — verify `token` via Supabase auth.get_user().
       Close 4001 on missing token; close 4001 on invalid/expired token.

    2. AUTHORISE — ensure the authenticated user is one of the two
       participants encoded in `consultation_id`.
       Close 4003 on membership failure.

    3. ACCEPT — upgrade the HTTP connection to WebSocket.

    4. HISTORY — immediately push the last 50 messages for this room
       as a single `history` payload so the client can render prior messages
       without a separate REST call.

    5. RECEIVE LOOP — for each incoming text frame:
         • Expect JSON: {"message": "..."}
         • Ping/pong: {"ping": true} → {"pong": true}
         • Save message to Supabase `chat_messages`.
         • Broadcast the saved row to ALL connections in the same room
           (including the sender, so the sender gets the server-assigned id
           and created_at timestamp).

    6. DISCONNECTION — remove the socket from the registry; if the room
       becomes empty the registry entry is deleted to prevent memory leak.

    Wire format (server → client)
    ------------------------------
    History payload:
        {
          "type": "history",
          "messages": [ { id, consultation_id, sender_id, message, created_at }, … ]
        }

    New message broadcast:
        {
          "type": "message",
          "id":              "<uuid>",
          "consultation_id": "<consultation_id>",
          "sender_id":       "<uuid>",
          "message":         "...",
          "created_at":      "<iso8601>"
        }

    Error frame:
        { "type": "error", "detail": "..." }
    """

    # ── Step 1: Authenticate ──────────────────────────────────────────────────
    if not token:
        await websocket.close(code=4001, reason="Missing auth token")
        return

    try:
        sb = supabase.get_client()
        user_resp = sb.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise ValueError("No user in response")
        current_user = user_resp.user
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # ── Step 2: Authorise ─────────────────────────────────────────────────────
    try:
        _assert_consultation_member(current_user.id, consultation_id)
    except PermissionError:
        await websocket.close(code=4003, reason="Not a participant in this consultation")
        return

    # ── Step 3: Accept ────────────────────────────────────────────────────────
    await registry.connect(websocket, consultation_id)

    # ── Step 4: Push history ──────────────────────────────────────────────────
    try:
        history = _fetch_history(consultation_id, limit=50)
        await websocket.send_json({"type": "history", "messages": history})
    except Exception as exc:
        logger.warning("Failed to send history for consultation %s: %s", consultation_id, exc)
        await websocket.send_json({"type": "error", "detail": "Could not load message history"})

    # ── Step 5: Receive loop ──────────────────────────────────────────────────
    try:
        while True:
            raw = await websocket.receive_text()

            # Parse JSON frame
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON frame"})
                continue

            # Ping / keepalive
            if data.get("ping"):
                await websocket.send_json({"pong": True})
                continue

            # Extract message text
            message_text = (data.get("message") or "").strip()
            if not message_text:
                await websocket.send_json({"type": "error", "detail": "Empty message"})
                continue

            # Persist to Supabase
            try:
                saved = _save_message(consultation_id, current_user.id, message_text)
            except Exception as exc:
                logger.error("DB insert failed consultation=%s: %s", consultation_id, exc)
                await websocket.send_json({"type": "error", "detail": "Failed to save message"})
                continue

            # Broadcast to everyone in the room (including sender)
            broadcast_payload = {
                "type":            "message",
                "id":              saved.get("id"),
                "consultation_id": saved.get("consultation_id"),
                "sender_id":       saved.get("sender_id"),
                "message":         saved.get("message"),
                "created_at":      saved.get("created_at"),
            }
            await registry.broadcast(consultation_id, broadcast_payload)

    # ── Step 6: Disconnection ─────────────────────────────────────────────────
    except WebSocketDisconnect:
        registry.disconnect(websocket, consultation_id)
        logger.info("WS clean disconnect consultation=%s user=%s", consultation_id, current_user.id)
    except Exception as exc:
        logger.error("WS unexpected error consultation=%s: %s", consultation_id, exc)
        registry.disconnect(websocket, consultation_id)
