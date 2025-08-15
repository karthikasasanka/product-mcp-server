FROM ollama/ollama

EXPOSE 11434

# Create an entrypoint script to start Ollama and pull the models
RUN echo '#!/bin/bash\n\
# Start Ollama server in background\n\
ollama serve &\n\
\n\
# Wait for server to be ready\n\
sleep 10\n\
\n\
# Pull the Nomic embedding model\n\
echo "Pulling nomic-embed-text model..."\n\
ollama pull nomic-embed-text\n\
\n\
# Pull the Llama 3.1 model for tool selection and argument extraction\n\
echo "Pulling llama3.1:8b model..."\n\
ollama pull llama3.1:8b\n\
\n\
# Pull the Qwen2.5-3B Instruct (q4 quant) model for v4 endpointc
echo "Pulling qwen2.5:3b-instruct-q4_K_M model..."\n\
ollama pull qwen2.5:3b-instruct-q4_K_M\n\
\n\
echo "All models pulled successfully!"\n\
\n\
# Keep the container running\n\
wait' > /entrypoint.sh && chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
