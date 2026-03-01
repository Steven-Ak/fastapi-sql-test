from typing import List, Dict
from app.models.chat_model import Chat
from app.core.config import settings


def build_optimized_context(chat: Chat) -> List[Dict[str, str]]:
    """
    Build an optimized LLM context list using a summary + recent messages.
    Saves tokens by not sending the full conversation history each time.
    """
    context = []

    if chat.summary:
        context.append({
            "role": "system",
            "content": f"Previous conversation summary:\n{chat.summary}"
        })
        # Only include messages after the last summarized message
        recent_messages = [
            msg for msg in chat.messages
            if msg.id > (chat.summary_up_to_message_id or 0)
        ]
    else:
        # No summary yet — use all messages
        recent_messages = chat.messages

    # Safety net: cap at KEEP_RECENT_MESSAGES in case of runaway history
    if len(recent_messages) > settings.KEEP_RECENT_MESSAGES:
        recent_messages = recent_messages[-settings.KEEP_RECENT_MESSAGES:]

    for msg in recent_messages:
        context.append({"role": msg.role, "content": msg.content})

    return context
