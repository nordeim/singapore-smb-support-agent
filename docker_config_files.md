# File: `Dockerfile`
```text
FROM python:3.13-trixie AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY uv* /usr/bin
RUN uv init --bare
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN pip install --no-cache-dir pytest pytest-asyncio

FROM python:3.13-trixie

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000))" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

# File: `docker-compose.yml`
```yaml
# ══════════════════════════════════════════════════════════════════════════════
# Singapore SMB Support Agent - Docker Compose (Development)
# ══════════════════════════════════════════════════════════════════════════════

version: "3.8"

services:
  # ─────────────────────────────────────────────────────────────────────────────
  # PostgreSQL - Long-term Memory Storage
  # ─────────────────────────────────────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: smb_support_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-support_agent}
      POSTGRES_USER: ${POSTGRES_USER:-agent_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-your_secure_password_here}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/init-scripts/postgres:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-support_agent} -d ${POSTGRES_DB:-support_agent}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Redis - Short-term Memory & Session Storage
  # ─────────────────────────────────────────────────────────────────────────────
  redis:
    image: redis:7.4-alpine
    container_name: smb_support_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Qdrant - Vector Database for RAG
  # ─────────────────────────────────────────────────────────────────────────────
  qdrant:
    image: qdrant/qdrant:gpu-nvidia-latest
    container_name: smb_support_qdrant
    restart: unless-stopped
    ports:
      - "${QDRANT_PORT:-6333}:6333"
      - "6334:6334"  # gRPC port
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
      QDRANT__LOG_LEVEL: INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Backend API (Optional - for full containerized development)
  # ─────────────────────────────────────────────────────────────────────────────
  # Uncomment to run backend in Docker instead of locally
  # backend:
  #   build:
  #     context: ./backend
  #     dockerfile: Dockerfile
  #   container_name: smb_support_backend
  #   restart: unless-stopped
  #   ports:
  #     - "${API_PORT:-8000}:8000"
  #   volumes:
  #     - ./backend:/app
  #   environment:
  #     - POSTGRES_HOST=postgres
  #     - REDIS_HOST=redis
  #     - QDRANT_HOST=qdrant
  #   depends_on:
  #     postgres:
  #       condition: service_healthy
  #     redis:
  #       condition: service_healthy
  #     qdrant:
  #       condition: service_healthy
  #   networks:
  #     - smb_support_network

# ─────────────────────────────────────────────────────────────────────────────
# Volumes
# ─────────────────────────────────────────────────────────────────────────────
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  qdrant_data:
    driver: local

# ─────────────────────────────────────────────────────────────────────────────
# Networks
# ─────────────────────────────────────────────────────────────────────────────
networks:
  smb_support_network:
    driver: bridge
```
