from typing import List, Dict
from app.models.chat_model import Chat
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.schemas.chat_schema import LLMProvider


class SummarizationService:
    """
    Handles conversation summarization and title generation.
    Single responsibility: manage LLM-based context compression.
    """

    def __init__(self, get_llm_client):
        """
        Args:
            get_llm_client: Callable that accepts an LLMProvider and returns a BaseLLMClient.
        """
        self._get_llm_client = get_llm_client

    # ----- Public API -----

    def should_generate_summary(self, chat: Chat) -> bool:
        """Determine if we should generate or update a summary."""
        if not chat.summary:
            # Case 1: No summary yet — check threshold for initial summary
            min_total = settings.KEEP_RECENT_MESSAGES + settings.MIN_MESSAGES_TO_SUMMARIZE
            if chat.message_count >= settings.SUMMARIZE_THRESHOLD and chat.message_count >= min_total:
                print(f"Initial summary needed: {chat.message_count} messages >= threshold {settings.SUMMARIZE_THRESHOLD}")
                return True
        elif chat.summary_up_to_message_id:
            # Case 2: Have summary — check if new messages since last summary exceed threshold
            messages_since = [
                msg for msg in chat.messages
                if msg.id > chat.summary_up_to_message_id
            ]
            new_count = len(messages_since)
            min_new = settings.KEEP_RECENT_MESSAGES + settings.MIN_MESSAGES_TO_SUMMARIZE
            if new_count >= settings.SUMMARIZE_THRESHOLD and new_count >= min_new:
                print(f"Summary update needed: {new_count} new messages since last summary")
                return True
        return False

    def generate_summary(self, chat: Chat, provider: LLMProvider, chat_repo) -> None:
        """
        Generate or update a rolling summary for old messages.
        Updates chat in place and persists via chat_repo.
        """
        if chat.summary and chat.summary_up_to_message_id:
            messages_after = [
                msg for msg in chat.messages
                if msg.id > chat.summary_up_to_message_id
            ]
            messages_to_summarize = messages_after[:-settings.KEEP_RECENT_MESSAGES]
        else:
            messages_to_summarize = chat.messages[:-settings.KEEP_RECENT_MESSAGES]

        if not messages_to_summarize or len(messages_to_summarize) < settings.MIN_MESSAGES_TO_SUMMARIZE:
            print(f"Not enough messages to summarize: {len(messages_to_summarize)} < {settings.MIN_MESSAGES_TO_SUMMARIZE}")
            return

        conversation_text = "\n".join(
            f"{msg.role.upper()}: {msg.content}" for msg in messages_to_summarize
        )

        try:
            client = self._get_llm_client(provider)
        except NotFoundException:
            return

        if chat.summary:
            summary_prompt = [{"role": "user", "content": (
                f"You are updating a conversation summary. Here is the previous summary:\n\n"
                f"{chat.summary}\n\nHere are the new messages since that summary:\n\n"
                f"{conversation_text}\n\n"
                f"Write an updated summary from the assistant's perspective, incorporating both the "
                f"previous context and new information. Use \"I\" and \"we\" language. Preserve all "
                f"key facts, names, dates, and context. Keep it under 300 words.\n\nUpdated summary:"
            )}]
        else:
            summary_prompt = [{"role": "user", "content": (
                f"Summarize this conversation from the assistant's perspective. Write as if you (the "
                f"assistant) are recalling what was discussed. Use \"I\" and \"we\" language. Preserve "
                f"all key facts, names, dates, and context. Keep it under 200 words.\n\n"
                f"Conversation:\n{conversation_text}\n\nWrite a first-person summary as the assistant:"
            )}]

        try:
            result = client.chat(messages=summary_prompt, temperature=0.3, max_tokens=400)
            chat.summary = result["text"]
            chat.summary_up_to_message_id = messages_to_summarize[-1].id
            chat_repo.update_chat(chat)
            print(f"Generated summary for chat {chat.id} (summarized {len(messages_to_summarize)} messages up to ID {chat.summary_up_to_message_id})")
        except Exception as e:
            print(f"Failed to generate summary for chat {chat.id}: {e}")

    def generate_chat_title(self, messages: list, provider: LLMProvider) -> str:
        """Generate a short title using the first couple of user messages."""
        user_messages = [m.content for m in messages if m.role.value == "user"][:2]
        if not user_messages:
            return "New Chat"

        conversation = "\n".join(user_messages)
        prompt = [{"role": "user", "content": (
            f"Generate a very short title (max 6 words) for this conversation.\n"
            f"Do NOT use quotes.\nDo NOT include punctuation at the end.\n\n"
            f"Conversation:\n{conversation}\n\nTitle:"
        )}]

        try:
            client = self._get_llm_client(provider)
            result = client.chat(messages=prompt, temperature=0.2, max_tokens=20)
            return result["text"].strip().replace("\n", " ")[:80]
        except Exception:
            return "New Chat"
