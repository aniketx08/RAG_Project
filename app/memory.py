from datetime import datetime
from db import chat_memory_collection

def save_message(user_id: str, conversation_id: str, role: str, content: str):

    chat_memory_collection.insert_one({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow()
    })


def get_recent_messages(user_id: str, conversation_id: str, limit: int = 6):
    messages = chat_memory_collection.find(
        {
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    ).sort("created_at", -1).limit(limit)

    return list(reversed(list(messages)))