# FROM python:3.13-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1

# WORKDIR /app

# # System deps for VCS installs and install uv
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends git curl \
#     && curl -LsSf https://astral.sh/uv/install.sh | sh \
#     && rm -rf /var/lib/apt/lists/*

# # Add uv to PATH
# ENV PATH="/root/.cargo/bin:${PATH}"

# # Copy the API source code
# COPY api /app/api

# RUN uv pip install -e api/pyproject.toml


# EXPOSE 8000

# # Run your FastAPI app
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps + install uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# uv installs to ~/.local/bin
ENV PATH="/root/.local/bin:${PATH}"

# Copy the API source (you can optimize caching later by copying pyproject first)
COPY api /app/api

# Install your app (editable) and its deps into the system interpreter (no venv)
# If your project has optional dev deps, keep them out via --no-deps flags on extras, etc.
RUN uv pip install --system -e /app/api

# Train the CSV classifier before starting the server
RUN python api/train_in_container.py

EXPOSE 8000

# Run the FastAPI app with reload for development
# (Since we installed into the system site-packages, calling uvicorn directly is fine.)
CMD ["uvicorn", "chat_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
