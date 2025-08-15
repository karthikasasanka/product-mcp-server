# Product MCP Server

A microservice-based product management system using MCP (Model Context Protocol) with intelligent tool selection and argument extraction.

## Architecture

- **MCP Server**: FastAPI-based product CRUD operations (Port 9000)
- **Chat API**: Natural language interface with multiple classification methods (Port 8000)
- **Ollama**: Local LLM server for embeddings and text generation (Port 11434)
- **PostgreSQL**: Database for product storage (Port 5432)

## Models Used

- **nomic-embed-text**: For vector embeddings and semantic search
- **llama3.1:8b**: For tool selection and argument extraction from natural language
- **CSV-based ML Classifier**: Fast pattern-based classification with dynamic argument extraction
- **Joint Intent-Slot Classifier**: Advanced ML-based classification for complex queries

## API Endpoints

### Chat API (Port 8000)

- `POST /chat/v1` - Uses Llama 3.1 for tool selection and argument extraction
- `POST /chat/v2` - Uses joint intent-slot classification with advanced ML approach
- `POST /chat/v3` - Uses CSV-based ML classifier with dynamic argument extraction
- `GET /chat/tools` - List available tools
- `GET /chat/test` - Health check

### Endpoint Evolution: v1 → v2 → v3

The chat endpoints represent an evolution in classification approaches:

**v1 (Llama 3.1)**: 
- **Why**: Started with LLM-based approach for maximum flexibility
- **Pros**: Most intelligent, handles complex queries
- **Cons**: Slow (120s timeout), resource-intensive
- **Use case**: Complex queries requiring deep understanding

**v2 (Joint Intent-Slot Classification)**:
- **Why**: Needed faster, more structured approach than v1
- **Pros**: Fast, handles intent classification and argument extraction simultaneously
- **Cons**: Requires pattern training, less flexible than LLM
- **Use case**: Standard queries with predictable patterns

**v3 (CSV-based ML Classifier)**:
- **Why**: Needed fastest possible response for production use
- **Pros**: Sub-second response, rule-based with ML fallback
- **Cons**: Requires explicit pattern training, least flexible
- **Use case**: High-throughput production scenarios

### MCP Server (Port 9000)

- Product CRUD operations via MCP protocol
- OpenAPI spec available at `/openapi.json`
- Health check at `/health`

## Quick Start

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Test the v3 endpoint (recommended for speed):**
   ```bash
   curl -X POST "http://localhost:8000/chat/v3" \
     -H "Content-Type: application/json" \
     -d '{"message": "add Smartphone Pro, with touchscreen, price $1249"}'
   ```

3. **Expected response (minimal format for all endpoints):**
   ```json
   {
     "message": "product created",
     "data": {
       "id": 1,
       "name": "Smartphone Pro",
       "price": 1249.0,
       "description": "with touchscreen"
     }
   }
   ```

## Features

### Multiple Classification Methods
- **v1**: Llama 3.1-based classification with 120-second timeout
- **v2**: Joint intent-slot classification with advanced ML approach
- **v3**: CSV-based ML classifier with dynamic argument extraction (fastest)

### Response Formats
All endpoints now use the **minimal format** for clean, consistent responses:
```json
{
  "message": "product created|updated|deleted|retrieved|products retrieved",
  "data": { /* actual product data */ }
}
```

### Tool Selection Capabilities
- ✅ **Intelligent tool selection** using multiple ML approaches
- ✅ **Automatic argument extraction** from natural language
- ✅ **Dynamic argument extraction** with regex patterns
- ✅ **Recent product filtering** for "show recent" queries
- ✅ **Fast CSV-based classification** for quick responses
- ✅ **Advanced joint classification** for complex queries

### Supported Operations
- **product.create**: Add new products with name, price, description
- **product.list**: List all products (with pagination and recent_only filter)
- **product.get**: Get specific product by ID
- **product.update**: Update existing products
- **product.delete**: Delete products

### Special Features
- **Recent Products**: Queries like "show recent product created" return only the most recent product
- **Dynamic Extraction**: Automatically extracts names, prices, IDs, and descriptions from natural language
- **Fallback Handling**: Graceful fallbacks when primary classification methods fail

## Performance Optimizations

### Recent Improvements
- ✅ **Unified response format**: All endpoints use minimal response format
- ✅ **Automated model training**: CSV classifier trained during Docker build
- ✅ **Dynamic argument extraction**: Enhanced with regex-based extraction
- ✅ **Recent product support**: Special handling for "recent" queries
- ✅ **Optimized timeouts**: 120-second timeout for Llama 3.1 operations
- ✅ **Pre-trained models**: Uses existing `csv_classifier.pkl` with latest patterns

### Build Performance
- **Model Training**: Automated during container build process
- **Pattern Updates**: Latest patterns automatically included in builds
- **Fast Startup**: Pre-loaded models for immediate availability

## Development

### Rebuilding after changes:
```bash
# Stop and rebuild specific service
docker-compose stop chat-api
docker-compose build chat-api
docker-compose up -d chat-api

# Or rebuild all services
docker-compose down
docker-compose up --build -d
```

### Testing:
```bash
# Test v2 endpoint (fastest, recommended)
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "add Smartphone Pro, with touchscreen, price $1249"}'

# Test v3 endpoint (advanced ML)
curl -X POST "http://localhost:8000/chat/v3" \
  -H "Content-Type: application/json" \
  -d '{"message": "show me recent products"}'

# Test v1 endpoint (Llama 3.1)
curl -X POST "http://localhost:8000/chat/v1" \
  -H "Content-Type: application/json" \
  -d '{"message": "create a new product called Ultrabook Pro"}'


# List available tools
curl "http://localhost:8000/chat/tools"

# Health checks
curl "http://localhost:8000/chat/test"
curl "http://localhost:9000/health"
```

### Example Queries
```bash
# Create product
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "add Ultrabook Pro, price $1999, description premium laptop"}'

# List all products
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "show me all products"}'

# Show recent products (returns only the most recent)
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "show recent product created"}'

# Update product
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "update product 1, change price to $1899"}'

# Delete product
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "delete product with id 1"}'

# Get specific product
curl -X POST "http://localhost:8000/chat/v2" \
  -H "Content-Type: application/json" \
  -d '{"message": "get product with id 1"}'
```

## Endpoint Comparison

| Endpoint | Method | Speed | Features | Best For |
|----------|--------|-------|----------|----------|
| `/v1` | Llama 3.1 | Slow (120s) | Full LLM reasoning | Complex queries |
| `/v2` | CSV + Dynamic Extraction | Fast | Pattern matching + regex | Production use |
| `/v3` | Joint Intent-Slot | Medium | Advanced ML | Research/advanced |

## Troubleshooting

### Common Issues
1. **Model not found**: Ensure Ollama is running and `llama3.1:8b` is pulled
2. **Timeout errors**: v1 endpoint has 120-second timeout for complex queries
3. **Build issues**: Check that all services are properly stopped before rebuilding

### Logs
```bash
# View chat-api logs
docker-compose logs -f chat-api

# View mcp-api logs
docker-compose logs -f mcp-api

# View ollama logs
docker-compose logs -f ollama
```
