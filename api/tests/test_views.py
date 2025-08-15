import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from chat_api.chat.views import chat, choose_tool, chat_router
from chat_api.chat.schemas import ChatIn


class TestChooseTool:
    """Test choose_tool function."""

    def test_choose_tool_success(self, mock_vector_store):
        """Test successful tool selection."""
        result = choose_tool(mock_vector_store, "list all products")
        
        assert result == {"operationId": "product.list", "method": "GET", "path": "/products"}
        mock_vector_store.similarity_search_with_score.assert_called_once_with("list all products", k=1)

    def test_choose_tool_no_vector_store(self):
        """Test choose_tool with no vector store."""
        with pytest.raises(RuntimeError, match="Vector store not initialized"):
            choose_tool(None, "list all products")

    def test_choose_tool_empty_results(self):
        """Test choose_tool with empty search results."""
        mock_vs = Mock()
        mock_vs.similarity_search_with_score.return_value = []
        
        with pytest.raises(IndexError):
            choose_tool(mock_vs, "list all products")


class TestChatEndpoint:
    """Test chat endpoint."""

    @pytest.mark.asyncio
    @patch('chat_api.chat.views.streamablehttp_client')
    @patch('chat_api.chat.views.ClientSession')
    async def test_chat_success(self, mock_client_session, mock_streamablehttp_client, mock_vector_store, 
                               mock_mcp_session, mock_mcp_client):
        """Test successful chat request."""
        # Setup mocks
        mock_streamablehttp_client.return_value = mock_mcp_client
        mock_client_session.return_value.__aenter__.return_value = mock_mcp_session
        
        # Create mock request
        mock_request = Mock()
        mock_request.state.vector_store = mock_vector_store
        
        # Test data
        test_input = ChatIn(message="list all products")
        
        # Call the endpoint
        result = await chat(test_input, mock_request, mock_vector_store)
        
        # Verify result
        expected_result = json.dumps([{"id": 1, "name": "Test Product"}])
        assert result == expected_result
        
        # Verify MCP client was called correctly
        mock_streamablehttp_client.assert_called_once()
        mock_mcp_session.initialize.assert_called_once()
        mock_mcp_session.call_tool.assert_called_once_with("product.list", {})

    @pytest.mark.asyncio
    @patch('chat_api.chat.views.streamablehttp_client')
    async def test_chat_mcp_error(self, mock_streamablehttp_client, mock_vector_store):
        """Test chat request with MCP error."""
        # Setup mocks to raise exception
        mock_streamablehttp_client.side_effect = Exception("MCP connection failed")
        
        # Create mock request
        mock_request = Mock()
        mock_request.state.vector_store = mock_vector_store
        
        # Test data
        test_input = ChatIn(message="list all products")
        
        # Call the endpoint and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await chat(test_input, mock_request, mock_vector_store)
        
        assert exc_info.value.status_code == 500
        assert "Error processing request" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('chat_api.chat.views.streamablehttp_client')
    async def test_chat_vector_store_error(self, mock_streamablehttp_client, mock_vector_store):
        """Test chat request with vector store error."""
        # Setup vector store to raise exception
        mock_vector_store.similarity_search_with_score.side_effect = Exception("Vector store error")
        
        # Create mock request
        mock_request = Mock()
        mock_request.state.vector_store = mock_vector_store
        
        # Test data
        test_input = ChatIn(message="list all products")
        
        # Call the endpoint and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await chat(test_input, mock_request, mock_vector_store)
        
        assert exc_info.value.status_code == 500
        assert "Error processing request" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('chat_api.chat.views.streamablehttp_client')
    @patch('chat_api.chat.views.ClientSession')
    async def test_chat_different_tool(self, mock_client_session, mock_streamablehttp_client, mock_vector_store, 
                                     mock_mcp_session, mock_mcp_client):
        """Test chat request with different tool selection."""
        # Setup vector store to return different tool
        mock_doc = Mock()
        mock_doc.metadata = {"operationId": "product.get", "method": "GET", "path": "/products/{id}"}
        mock_vector_store.similarity_search_with_score.return_value = [(mock_doc, 0.95)]
        
        # Setup mocks
        mock_streamablehttp_client.return_value = mock_mcp_client
        mock_client_session.return_value.__aenter__.return_value = mock_mcp_session
        
        # Create mock request
        mock_request = Mock()
        mock_request.state.vector_store = mock_vector_store
        
        # Test data
        test_input = ChatIn(message="get product by id")
        
        # Call the endpoint
        result = await chat(test_input, mock_request, mock_vector_store)
        
        # Verify MCP client was called with correct tool
        mock_mcp_session.call_tool.assert_called_once_with("product.get", {})

    @pytest.mark.asyncio
    @patch('chat_api.chat.views.streamablehttp_client')
    async def test_chat_mcp_session_error(self, mock_streamablehttp_client, mock_vector_store, 
                                        mock_mcp_client):
        """Test chat request with MCP session error."""
        # Setup mocks
        mock_streamablehttp_client.return_value = mock_mcp_client
        
        # Setup session to raise exception
        mock_session = AsyncMock()
        mock_session.initialize.side_effect = Exception("Session initialization failed")
        mock_mcp_client.__aenter__.return_value = (Mock(), Mock(), None)
        
        # Create mock request
        mock_request = Mock()
        mock_request.state.vector_store = mock_vector_store
        
        # Test data
        test_input = ChatIn(message="list all products")
        
        # Call the endpoint and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await chat(test_input, mock_request, mock_vector_store)
        
        assert exc_info.value.status_code == 500
        assert "Error processing request" in str(exc_info.value.detail)


class TestChatRouter:
    """Test chat router configuration."""

    def test_router_configuration(self):
        """Test router is properly configured."""
        assert chat_router.prefix == "/chat"
        assert "Chat" in chat_router.tags
        assert len(chat_router.routes) > 0
