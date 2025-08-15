# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps + uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# uv installs to ~/.local/bin
ENV PATH="/root/.local/bin:${PATH}"

# Work inside your project (pyproject.toml lives under mcp/)
WORKDIR /app/mcp

# Copy project
COPY mcp /app/mcp

# Install app + deps into system site-packages (editable)
RUN uv pip install --system -e .

EXPOSE 9000

# Run FastAPI
CMD ["uvicorn", "mcp_api.main:app", "--host", "0.0.0.0", "--port", "9000"]
