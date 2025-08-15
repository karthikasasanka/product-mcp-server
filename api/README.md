# AI Chat API Service

A FastAPI-based chat service that integrates with MCP (Model Context Protocol) tools for intelligent conversation capabilities.

## Features

- **Chat Interface**: RESTful API for chat interactions
- **MCP Integration**: Seamless integration with MCP tools and servers
- **Tool Selection**: AI-powered tool selection based on user input
- **Async Operations**: Full async/await support for high performance

## Project Structure

```
api/
├── __init__.py
├── main.py              # FastAPI app entry point
├── app.py               # App factory and configuration
├── init.py              # Router initialization and tool indexing
├── config.py            # Configuration settings
├── chat/
│   ├── views.py         # Chat API endpoints
│   ├── schemas.py       # Pydantic models
│   └── nlp.py           # NLP utilities
├── pyproject.toml       # Project dependencies
├── Dockerfile           # Container configuration
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **httpx**: Async HTTP client
- **MCP**: Model Context Protocol client
- **Pydantic**: Data validation and settings management
- **Starlette**: ASGI toolkit (FastAPI dependency)

## Development

### Local Development

1. Install dependencies:
   ```bash
   cd api
   uv sync
   ```

2. Run the development server:
   ```bash
   uv run uvicorn api.main:app --reload --port 8001
   ```

### Docker

Build and run with Docker:

```bash
docker build -t ai-chat-api .
docker run -p 8001:8001 ai-chat-api
```

## API Endpoints

### POST /chat/

Send a chat message and get AI-powered responses with tool integration.

**Request:**
```json
{
  "message": "Show me all products"
}
```

**Response:**
```json
{
  "tool": "get_products",
  "result": {
    "content": [
      {"id": 1, "name": "Product 1", "price": 29.99}
    ]
  }
}
```

## Environment Variables

- `OLLAMA_URL`: Ollama server URL (default: `http://ollama:11434/api/chat`)
- `MCP_API_URL`: MCP API server URL (default: `http://mcp-api:8000`)

## Integration

This API service is designed to work with:
- **MCP Server**: For tool execution
- **Ollama**: For AI model inference
- **Product Database**: For data retrieval operations
