from typing import List
from app.classes.chat import ChatMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


def convert_chat_messages(messages: List[ChatMessage]) -> List[BaseMessage]: 
    lc_messages = []
    for msg in messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
        elif msg.role == "system":
            lc_messages.append(SystemMessage(content=msg.content))
        else:
            lc_messages.append(HumanMessage(content=msg.content))

    return lc_messages