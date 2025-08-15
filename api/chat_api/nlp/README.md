# NLP Module

A unified module for tool selection and argument extraction using configurable NLP models.

## Overview

This module consolidates the previously separate Llama 3.1 and Qwen implementations into a single, configurable solution. Both models were doing the same task - tool selection and argument extraction - so we've unified them into one flexible module.

## Features

- **Configurable Models**: Switch between different NLP models via environment variables
- **Unified Interface**: Same API regardless of the underlying model
- **Environment-based Configuration**: No code changes needed to switch models
- **Backward Compatibility**: Existing code continues to work

## Supported Models

### Llama 3.1:8b
- **Use Case**: Complex queries requiring deep reasoning
- **Speed**: Slow (2-5 minutes per request)
- **Intelligence**: Very High
- **Resource Usage**: High (~8GB RAM)

### Qwen2.5:3b-instruct-q4_K_M
- **Use Case**: Balanced scenarios requiring both speed and intelligence
- **Speed**: Medium (2-5 seconds per request)
- **Intelligence**: High
- **Resource Usage**: Medium (~4GB RAM)

### Custom Models
- Any Ollama model can be used by setting the `NLP_MODEL_NAME` environment variable

## Configuration

### Environment Variables

```bash
# Model selection
export NLP_MODEL_NAME="llama3.1:8b"  # or "qwen2.5:3b-instruct-q4_K_M"

# Timeout (in seconds)
export NLP_TIMEOUT="300.0"  # 5 minutes for llama3.1:8b, 120.0 for qwen2.5:3b

# Temperature (0.0 = deterministic, higher = more creative)
export NLP_TEMPERATURE="0.0"
```

### Default Values

```python
NLP_MODEL_NAME = "llama3.1:8b"  # Default to llama3.1:8b
NLP_TIMEOUT = 300.0             # Default to 5 minutes for llama3.1:8b
NLP_TEMPERATURE = 0.0           # Default to deterministic
```

## Usage

### Basic Usage

```python
from chat_api.nlp import extract_tool_and_args_nlp

# Extract tool and arguments
result = await extract_tool_and_args_nlp("Create a new product called iPhone 15 with price 999")

print(result)
# Output: {
#     "tool_name": "product.create",
#     "tool_args": {
#         "name": "iPhone 15",
#         "price": 999,
#         "description": "new product"
#     },
#     "confidence": 0.9,
#     "method": "llama3.1_8b",
#     "model": "llama3.1:8b"
# }
```

### Model Information

```python
from chat_api.nlp import get_model_info, list_available_models

# Get current model info
current_model = get_model_info()
print(f"Using model: {current_model['model_name']}")

# List all available models
models = list_available_models()
for model in models:
    print(f"- {model['name']}: {model['details']['use_case']}")
```

### Switching Models

```python
import os

# Switch to Qwen model
os.environ["NLP_MODEL_NAME"] = "qwen2.5:3b-instruct-q4_K_M"
os.environ["NLP_TIMEOUT"] = "120.0"

# Now all calls will use Qwen
result = await extract_tool_and_args_nlp("List all products")
```

## API Endpoints

The module is used by the following chat endpoints:

- **`/v1`**: Uses the NLP module with fast fallback
- **`/v4`**: Uses the NLP module (configurable model)

## Migration from Old Implementation

### Before (Separate Modules)

```python
# Old way - separate imports
from chat_api.extract import extract_tool_and_args  # Llama 3.1 (deprecated)
from chat_api.qwen.extractor import extract_tool_and_args_qwen  # Qwen (deprecated)

# Different function calls
result1 = await extract_tool_and_args(message)
result2 = await extract_tool_and_args_qwen(message)
```

### After (Unified NLP Module)

```python
# New way - single import
from chat_api.nlp import extract_tool_and_args_nlp

# Same function call, different model based on environment
result = await extract_tool_and_args_nlp(message)

# Switch models via environment variables
os.environ["NLP_MODEL_NAME"] = "llama3.1:8b"    # Use Llama
os.environ["NLP_MODEL_NAME"] = "qwen2.5:3b-instruct-q4_K_M"  # Use Qwen
```

## Testing

Run the test script to verify the module works:

```bash
cd api/chat_api/nlp
python test_nlp.py
```

## Benefits of Consolidation

1. **Code Reuse**: No more duplicate logic between Llama and Qwen
2. **Easier Maintenance**: Single codebase to maintain
3. **Flexible Deployment**: Switch models without code changes
4. **Consistent Interface**: Same API regardless of model
5. **Better Testing**: Single test suite for all models

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Environment   │    │   NLP Config    │    │   NLP Module    │
│   Variables     │───▶│   (Model Name,  │───▶│   (Extractor,   │
│                 │    │    Timeout,     │    │    Utils)       │
│                 │    │   Temperature)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Ollama API    │    │   Chat Views    │
                       │   (llama3.1:8b, │    │   (v1, v4)     │
                       │    qwen2.5:3b)  │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## Future Enhancements

- Support for additional model providers (not just Ollama)
- Model performance metrics and monitoring
- Automatic model selection based on query complexity
- Model fallback strategies
- Batch processing capabilities
