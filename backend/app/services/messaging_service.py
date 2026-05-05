"""
MessagingService
================
Handles room-based direct messaging between a client (user) and a lawyer.

Room ID convention (enforced here, never trusted from the client):
    "{user_id}_{lawyer_id}"   — always smaller UUID first alphabetically
    so that the same pair always maps to the same room regardless of
    which side initiates.
"""

from fastapi import HTTPException
from supabase import Client
from app.core.supabase_client import supabase


def _canonical_room_id(uid_a: str, uid_b: str) -> str:
    """Return a deterministic room id for any two user IDs."""
    pair = sorted([uid_a, uid_b])
    return f"{pair[0]}_{pair[1]}"


class MessagingService:
    def __init__(self):
        # Admin client so backend can insert/read without relying on RLS.
        self.client: Client = supabase.get_admin_client()

    # ------------------------------------------------------------------
    # Rooms
    # ------------------------------------------------------------------

    def get_or_create_room(self, current_user_id: str, other_user_id: str) -> dict:
        """
        Return the canonical room_id for two participants.
        Does NOT create a DB row — room identity lives entirely in the
        room_id field of chat_messages (schema-free rooms).
        """
        room_id = _canonical_room_id(current_user_id, other_user_id)
        return {"room_id": room_id}

    def list_rooms(self, user_id: str) -> list[dict]:
        """
        Return all distinct rooms the user participates in, along with the
        latest message preview and unread count.

        Relies on a simple GROUP BY via RPC or a post-processed query.
        We use a basic approach: fetch all messages where the room_id
        contains the user's id, then collapse by room.
        """
        try:
            response = (
                self.client.table("chat_messages")
                .select("room_id, message, created_at, sender_id")
                .ilike("room_id", f"%{user_id}%")
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Collapse to one row per room (latest message is first due to ordering)
        seen: set[str] = set()
        rooms: list[dict] = []
        for row in (response.data or []):
            rid = row["room_id"]
            if rid not in seen:
                seen.add(rid)
                # Derive the other participant's id from room_id
                parts = rid.split("_")
                other_id = parts[1] if parts[0] == user_id else parts[0]
                rooms.append({
                    "room_id":       rid,
                    "other_user_id": other_id,
                    "last_message":  (row.get("message") or "")[:80],
                    "last_at":       row.get("created_at"),
                    "is_mine":       row.get("sender_id") == user_id,
                })
        return rooms

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def get_messages(
        self,
        room_id: str,
        current_user_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> dict:
        """
        Return paginated messages for a room.
        Access guard: current_user_id must appear in the room_id.
        """
        self._assert_room_member(room_id, current_user_id)

        offset = (page - 1) * limit
        try:
            response = (
                self.client.table("chat_messages")
                .select("id, room_id, sender_id, message, created_at", count="exact")
                .eq("room_id", room_id)
                .order("created_at", desc=False)
                .range(offset, offset + limit - 1)
                .execute()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        total = (
            response.count
            if hasattr(response, "count") and response.count is not None
            else len(response.data or [])
        )
        return {
            "room_id":     room_id,
            "data":        response.data or [],
            "total_count": total,
            "page":        page,
            "limit":       limit,
            "has_more":    (offset + limit) < total,
        }

    def send_message(
        self,
        room_id: str,
        sender_id: str,
        message: str,
    ) -> dict:
        """
        Insert a new message into chat_messages.
        Validates that sender_id is a member of the room.
        """
        self._assert_room_member(room_id, sender_id)

        if not message or not message.strip():
            raise HTTPException(status_code=422, detail="Message cannot be empty.")

        payload = {
            "room_id":   room_id,
            "sender_id": sender_id,
            "message":   message.strip(),
        }
        try:
            response = self.client.table("chat_messages").insert(payload).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to persist message.")

        return response.data[0]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _assert_room_member(self, room_id: str, user_id: str) -> None:
        """Raise 403 if user_id is not encoded in room_id."""
        if user_id not in room_id.split("_"):
            raise HTTPException(
                status_code=403,
                detail="You are not a participant in this chat room.",
            )


# Singleton
messaging_service = MessagingService()
