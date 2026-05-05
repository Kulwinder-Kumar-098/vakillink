"""
Messaging Router — /api/messages
==================================
Provides room-based direct messaging between clients and lawyers.

REST endpoints
--------------
GET  /api/messages/rooms                  — list all rooms for current user
POST /api/messages/rooms/{other_user_id}  — get (or derive) room_id with another user
GET  /api/messages/{room_id}              — fetch paginated messages in a room
POST /api/messages/{room_id}              — send a message to a room

WebSocket
---------
WS   /api/messages/ws/{room_id}          — real-time message delivery
     • On connect: authenticates via ?token= query param (Supabase JWT)
     • Broadcasts any message sent to the room to all connected clients
       sharing the same room_id.
"""

import asyncio
import json
from collections import defaultdict
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase
from app.services.messaging_service import messaging_service

router = APIRouter()


# ------------------------------------------------------------------
# WebSocket connection manager
# ------------------------------------------------------------------

class ConnectionManager:
    """Tracks active WebSocket connections keyed by room_id."""

    def __init__(self):
        # room_id → list of connected WebSocket objects
        self._rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        self._rooms[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        room = self._rooms.get(room_id, [])
        if websocket in room:
            room.remove(websocket)

    async def broadcast(self, room_id: str, payload: dict):
        """Send a JSON payload to every client in the room."""
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(room_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, room_id)


manager = ConnectionManager()


# ------------------------------------------------------------------
# Pydantic schemas
# ------------------------------------------------------------------

class SendMessageRequest(BaseModel):
    message: str


# ------------------------------------------------------------------
# REST routes
# ------------------------------------------------------------------

@router.get("/rooms", summary="List all chat rooms for the authenticated user")
def list_rooms(user=Depends(get_current_user)):
    """
    Returns all rooms the current user participates in, with a preview of
    the latest message and the other participant's user ID.
    """
    return messaging_service.list_rooms(user_id=user.id)


@router.post(
    "/rooms/{other_user_id}",
    summary="Derive the canonical room_id for a conversation with another user",
)
def get_room(
    other_user_id: str = Path(..., description="UUID of the other participant"),
    user=Depends(get_current_user),
):
    """
    Returns the deterministic `room_id` for the pair (current_user, other_user).
    Room IDs follow the format `{smaller_uuid}_{larger_uuid}` so the same pair
    always resolves to the same room regardless of who initiates.
    """
    if other_user_id == user.id:
        raise HTTPException(status_code=422, detail="Cannot create a room with yourself.")
    return messaging_service.get_or_create_room(user.id, other_user_id)


@router.get("/{room_id}", summary="Fetch paginated messages in a room")
def get_messages(
    room_id: str = Path(..., description="Room ID (format: uuid_uuid)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Messages per page"),
    user=Depends(get_current_user),
):
    """
    Returns messages for a room in ascending chronological order.
    Only members of the room (user IDs encoded in `room_id`) can access it.
    Supports pagination via **page** / **limit**.
    """
    return messaging_service.get_messages(
        room_id=room_id,
        current_user_id=user.id,
        page=page,
        limit=limit,
    )


@router.post("/{room_id}", summary="Send a message to a room", status_code=201)
async def send_message(
    body: SendMessageRequest,
    room_id: str = Path(..., description="Room ID (format: uuid_uuid)"),
    user=Depends(get_current_user),
):
    """
    Persists a message and **broadcasts** it in real-time to all WebSocket
    clients currently connected to the same `room_id`.
    """
    saved = messaging_service.send_message(
        room_id=room_id,
        sender_id=user.id,
        message=body.message,
    )
    # Broadcast to WS clients (fire-and-forget — REST caller doesn't wait)
    asyncio.create_task(manager.broadcast(room_id, saved))
    return saved


# ------------------------------------------------------------------
# WebSocket endpoint
# ------------------------------------------------------------------

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str] = Query(None, description="Supabase JWT for authentication"),
):
    """
    WebSocket endpoint for real-time messaging.

    **Authentication**: Pass the Supabase JWT as `?token=<jwt>` in the URL.
    The connection is rejected with code 4001 if the token is missing or invalid.

    **Protocol**:
    - After connecting, send JSON: `{"message": "your text here"}`
    - Any message saved via POST /api/messages/{room_id} is also pushed here.
    - Send `{"ping": true}` to keep the connection alive; server echoes `{"pong": true}`.
    """
    # --- Authenticate via token query param ---
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    try:
        sb_client = supabase.get_client()
        user_response = sb_client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid user")
        current_user = user_response.user
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # --- Guard: user must be a member of the room ---
    if current_user.id not in room_id.split("_"):
        await websocket.close(code=4003, reason="You are not a member of this room")
        return

    await manager.connect(websocket, room_id)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            # Ping/pong keepalive
            if data.get("ping"):
                await websocket.send_json({"pong": True})
                continue

            message_text = data.get("message", "").strip()
            if not message_text:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Persist and broadcast
            try:
                saved = messaging_service.send_message(
                    room_id=room_id,
                    sender_id=current_user.id,
                    message=message_text,
                )
            except HTTPException as e:
                await websocket.send_json({"error": e.detail})
                continue

            await manager.broadcast(room_id, saved)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
