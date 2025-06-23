import pytest
from app.utils.chat.chat_utils import convert_chat_messages
from app.classes.chat import ChatMessage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def test_convert_chat_messages_user():
    messages = [ChatMessage(role="user", content="Hello")] 
    result = convert_chat_messages(messages)
    assert len(result) == 1
    assert isinstance(result[0], HumanMessage)
    assert result[0].content == "Hello"

def test_convert_chat_messages_assistant():
    messages = [ChatMessage(role="assistant", content="Hi, how can I help?")]
    result = convert_chat_messages(messages)
    assert len(result) == 1
    assert isinstance(result[0], AIMessage)
    assert result[0].content == "Hi, how can I help?"

def test_convert_chat_messages_system():
    messages = [ChatMessage(role="system", content="System message")]
    result = convert_chat_messages(messages)
    assert len(result) == 1
    assert isinstance(result[0], SystemMessage)
    assert result[0].content == "System message"

def test_convert_chat_messages_unknown_role():
    messages = [ChatMessage(role="other", content="Fallback to human")]
    result = convert_chat_messages(messages)
    assert len(result) == 1
    assert isinstance(result[0], HumanMessage)
    assert result[0].content == "Fallback to human" 

def test_convert_chat_messages_history():
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant"),
        ChatMessage(role="assistant", content="What can I help you"),
        ChatMessage(role="user", content="Hello")
        ]
    result = convert_chat_messages(messages)
    assert len(result) == 3
    assert isinstance(result[0], SystemMessage)
    assert result[0].content == "You are a helpful assistant"
    assert isinstance(result[1], AIMessage)
    assert result[1].content == "What can I help you"
    assert isinstance(result[2], HumanMessage)
    assert result[2].content == "Hello"