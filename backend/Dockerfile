# -----------------------------------------------------------------------------
# STAGE 1: BUILDER
# Use Python 3.11 (Stable AI Standard) on Debian Bookworm (Reliable)
# -----------------------------------------------------------------------------
FROM python:3.13-trixie AS builder

WORKDIR /app

# Install build dependencies (needed for some AI wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (The Astral fast package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/uv

# Create virtual environment
ENV VIRTUAL_ENV=/app/.venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
# Note: We use --no-cache to keep image size down, though uv manages cache well
COPY pyproject.toml .
# Assuming you might have a lock file later, but for now:
RUN uv pip install --no-cache-dir -e .
RUN uv pip install --no-cache-dir pytest pytest-asyncio uvicorn

# -----------------------------------------------------------------------------
# STAGE 2: RUNTIME
# Slim, secure, and minimal
# -----------------------------------------------------------------------------
FROM python:3.13-trixie

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the Virtual Environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy Application Code
COPY --chown=appuser:appuser . .

# Set Environment
USER appuser
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Healthcheck: Verify TCP socket availability
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000))" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
