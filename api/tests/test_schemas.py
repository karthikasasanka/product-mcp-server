import pytest
from pydantic import ValidationError

from chat_api.chat.schemas import ChatIn


class TestChatIn:
    """Test ChatIn schema."""

    def test_chat_in_valid(self):
        """Test valid ChatIn data."""
        data = {"message": "list all products"}
        chat_in = ChatIn(**data)
        assert chat_in.message == "list all products"

    def test_chat_in_empty_message(self):
        """Test ChatIn with empty message."""
        data = {"message": ""}
        chat_in = ChatIn(**data)
        assert chat_in.message == ""

    def test_chat_in_long_message(self):
        """Test ChatIn with long message."""
        long_message = "a" * 1000
        data = {"message": long_message}
        chat_in = ChatIn(**data)
        assert chat_in.message == long_message

    def test_chat_in_missing_message(self):
        """Test ChatIn with missing message field."""
        data = {}
        with pytest.raises(ValidationError):
            ChatIn(**data)

    def test_chat_in_wrong_type(self):
        """Test ChatIn with wrong message type."""
        data = {"message": 123}
        with pytest.raises(ValidationError):
            ChatIn(**data)

    def test_chat_in_none_message(self):
        """Test ChatIn with None message."""
        data = {"message": None}
        with pytest.raises(ValidationError):
            ChatIn(**data)

    def test_chat_in_model_dump(self):
        """Test ChatIn model dump."""
        data = {"message": "test message"}
        chat_in = ChatIn(**data)
        dumped = chat_in.model_dump()
        assert dumped == data

    def test_chat_in_model_json(self):
        """Test ChatIn model JSON serialization."""
        data = {"message": "test message"}
        chat_in = ChatIn(**data)
        json_str = chat_in.model_dump_json()
        assert '"message":"test message"' in json_str
