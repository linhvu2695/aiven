from typing import List
from app.classes.chat import ChatMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


def convert_chat_messages(messages: List[ChatMessage]) -> List[BaseMessage]: 
    lc_messages = []
    for msg in messages:
        # Handle both string and multimodal content
        content = msg.content
        
        # Convert MessageContentItem list to the format expected by LangChain
        if isinstance(content, list):
            langchain_content = []
            for item in content:
                if item.type == "text":
                    langchain_content.append({"type": "text", "text": item.text or ""})
                elif item.type == "image":
                    if item.source_type == "base64":
                        langchain_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": item.mime_type or "image/jpeg", 
                                "data": item.data
                            }
                        })
                    elif item.url:
                        langchain_content.append({
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": item.url
                            }
                        })
                # Add more content types as needed (audio, document, etc.)
            content = langchain_content
        
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=content))
        elif msg.role == "system":
            lc_messages.append(SystemMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))

    return lc_messages