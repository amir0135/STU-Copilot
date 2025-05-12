from datetime import datetime, timezone
from typing import Optional, List

class ChatMessage:
    def __init__(self, id: str, user_id: str, message: str, thread_id: str, timestamp: Optional[str] = None, role: str = "user"):
        self.id = id  # Unique identifier for Cosmos DB
        self.thread_id = thread_id  # Thread identifier
        self.user_id = user_id  # User identifier        
        self.message = message  # Message content
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()  # ISO 8601 format
        self.role = role  # 'user' or 'assistant'

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "user_id": self.user_id,            
            "message": self.message,
            "timestamp": self.timestamp,
            "role": self.role
        }

    @staticmethod
    def from_dict(data: dict):
        return ChatMessage(
            id=data.get("id"),
            user_id=data.get("user_id"),
            thread_id=data.get("thread_id"),
            message=data.get("message"),
            timestamp=data.get("timestamp"),
            role=data.get("role", "user")
        )

class ChatThread:
    def __init__(self, thread_id: str, user_id: str, messages: Optional[List[ChatMessage]] = None, created_at: Optional[str] = None):
        self.thread_id = thread_id  # Unique thread identifier
        self.user_id = user_id  # User identifier
        self.messages = messages or []  # List of ChatMessage objects
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data: dict):
        messages = [ChatMessage.from_dict(msg) for msg in data.get("messages", [])]
        return ChatThread(
            thread_id=data.get("thread_id"),
            user_id=data.get("user_id"),
            messages=messages,
            created_at=data.get("created_at")
        )