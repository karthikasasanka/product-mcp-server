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

- `POST /chat/v1` - Uses configurable NLP model (llama3.1:8b, qwen2.5:3b-instruct-q4_K_M, etc.) for tool selection and argument extraction
- `POST /chat/v2` - Uses joint intent-slot classification with advanced ML approach
- `POST /chat/v3` - Uses CSV-based ML classifier with dynamic argument extraction
- `GET /chat/tools` - List available tools
- `GET /chat/test` - Health check

### Endpoint Evolution: v1 → v2 → v3

The chat endpoints represent an evolution in classification approaches:

**v1 (Configurable NLP)**: 
- **Why**: Unified approach using configurable NLP models via environment variables
- **Pros**: Flexible model selection (llama3.1:8b, qwen2.5:3b-instruct-q4_K_M, etc.), handles all scenarios
- **Cons**: Speed depends on chosen model (llama3.1:8b = slow, qwen2.5:3b = fast)
- **Use case**: All scenarios - model choice based on requirements

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

2. **Test the v1 endpoint (configurable NLP model):**
   ```bash
   curl -X POST "http://localhost:8000/chat/v1" \
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
- **v1**: Configurable NLP model classification (llama3.1:8b, qwen2.5:3b-instruct-q4_K_M, etc.) with configurable timeout
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
- ✅ **Optimized timeouts**: 300-second timeout for Llama 3.1 operations
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

## Performance Comparison

### Response Time Analysis (Query: "add Ismartphone Xy5, best one yet and price is $1592")

| Endpoint | Method | Response Time | Status | Product Created | Features | Best For |
|----------|--------|---------------|--------|-----------------|----------|----------|
| `/v1` | Llama 3.1 | ~3m 1s | ✅ Success | ID 34 (name: ✓, price: ✓, desc: ✓) | Full LLM reasoning | Complex queries |
| `/v2` | Joint Intent-Slot | ~0.21s | ✅ Success | ID 35 (name: ✓, price: ✓, desc: ✗) | Advanced ML classification | Research/advanced |
| `/v3` | CSV-based ML | ~0.19s | ✅ Success | ID 36 (name: ✓, price: ✓, desc: ✗) | Pattern matching + regex | Production use |
| `/v4` | Qwen2.5-3B (q4) | ~1m 36s | ✅ Success | ID 37 (name: ✓, price: ✓, desc: ✓) | Balanced intelligence/speed | Balanced scenarios |

### Performance Characteristics

**v1 (Llama 3.1)**:
- **Response Time**: ~3m 1s
- **Status**: ✅ Success (with 5-minute timeout)
- **Product Accuracy**: Perfect (name: ✓, price: ✓, description: ✓)
- **Use Case**: Complex queries requiring deep reasoning
- **Trade-off**: Maximum intelligence, slowest speed

**v2 (Joint Intent-Slot)**:
- **Response Time**: ~0.21s
- **Status**: ✅ Success
- **Product Accuracy**: Good (name: ✓, price: ✓, description: ✗ - includes price info)
- **Use Case**: Standard queries with predictable patterns
- **Trade-off**: Fast, requires pattern training

**v3 (CSV-based ML)**:
- **Response Time**: ~0.19s
- **Status**: ✅ Success
- **Product Accuracy**: Good (name: ✓, price: ✓, description: ✗ - includes price info)
- **Use Case**: High-throughput production scenarios
- **Trade-off**: Fastest, least flexible

**v4 (Qwen2.5-3B q4)**:
- **Response Time**: ~1m 36s
- **Status**: ✅ Success
- **Product Accuracy**: Perfect (name: ✓, price: ✓, description: ✓)
- **Use Case**: Balanced scenarios requiring both speed and intelligence
- **Trade-off**: Moderate speed, good flexibility, reasonable resource usage

### Product Creation Analysis

**Query**: "add Ismartphone Xy5, best one yet and price is $1592"

| Endpoint | Name Extraction | Price Extraction | Description Extraction | Overall Accuracy |
|----------|----------------|------------------|----------------------|------------------|
| **v1** | ✅ "Ismartphone Xy5" | ✅ 1592.0 | ✅ "best one yet" | 100% |
| **v2** | ✅ "Ismartphone Xy5" | ✅ 1592.0 | ❌ "best one yet and price is $1592" (includes price) | 67% |
| **v3** | ✅ "Ismartphone Xy5" | ✅ 1592.0 | ❌ "best one yet and price is $1592" (includes price) | 67% |
| **v4** | ✅ "Ismartphone Xy5" | ✅ 1592.0 | ✅ "best one yet" | 100% |

**Note**: All endpoints successfully created products in the database. v1 and v4 correctly extracted the description as "best one yet". v2 and v3 incorrectly included price information in the description.

### Endpoint Evolution Summary

| Version | Evolution Reason | Performance | Intelligence | Flexibility |
|---------|------------------|-------------|--------------|-------------|
| v1 | Started with LLM for maximum flexibility | Slow (3m 1s) | High | High |
| v2 | Needed faster, structured approach | Fast (0.21s) | Medium | Medium |
| v3 | Needed fastest possible response | Fastest (0.19s) | Medium | Low |
| v4 | Balanced approach between speed and intelligence | Medium (1m 36s) | High | High |

## Troubleshooting

### Common Issues
1. **Model not found**: Ensure Ollama is running and `llama3.1:8b` is pulled
2. **Timeout errors**: v1 endpoint has 300-second timeout for complex queries
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
