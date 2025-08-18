"""
Harmony Client for communicating with gpt-oss using openai-harmony format
"""

from openai_harmony import SystemContent, DeveloperContent, Message, Conversation, Role, load_harmony_encoding, HarmonyEncodingName, ReasoningEffort
from typing import List

class HarmonyClient:
    def __init__(self, reasoning_effort: str = "medium"):
        self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
        # Use ReasoningEffort enum: ReasoningEffort.LOW, MEDIUM, HIGH
        effort_enum = ReasoningEffort[reasoning_effort.upper()]
        self.reasoning_effort = effort_enum.value
        self.system_content = SystemContent.new().with_conversation_start_date("2025-08-17").with_reasoning_effort(effort_enum)


    def build_system_message(self, developer_message: str = "") -> Message:
        system_content = self.system_content
        if developer_message:
            # DeveloperContent should be used in developer messages, not system
            return Message.from_role_and_content(Role.SYSTEM, system_content)
        else:
            return Message.from_role_and_content(Role.SYSTEM, system_content)

    def build_conversation(self, user_messages: List[str], developer_message: str = "") -> Conversation:
        messages = [self.build_system_message(developer_message)]
        for msg in user_messages:
            messages.append(Message.from_role_and_content(Role.USER, msg))
        return Conversation.from_messages(messages)

    def encode_conversation(self, conversation: Conversation):
        return self.encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

