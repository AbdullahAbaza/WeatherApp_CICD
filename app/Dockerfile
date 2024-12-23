# stage 1: builder
FROM python:3.10-slim-buster AS builder

# Set build environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# stage 2: final
FROM python:3.10-slim-buster

# Create non-root user
RUN useradd --create-home appuser && \
    mkdir -p /app/logs /app/static && \
    chown -R appuser:appuser /app

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    GUNICORN_CMD_ARGS="--workers=4 --bind=0.0.0.0:5001 --timeout=120 --access-logfile=/app/logs/access.log --error-logfile=/app/logs/error.log"

WORKDIR /app

# Install runtime dependencies
# In the runtime stage, after apt-get install:
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    python3-tk \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

RUN touch weather_data.db && \
    chown appuser:appuser weather_data.db && \
    chmod 664 weather_data.db

# Copy wheels from builder and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir --no-deps /wheels/* && \
    rm -rf /wheels && \
    rm -rf /root/.cache/pip/*

# Copy application
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app


# Switch to non-root user
USER appuser

EXPOSE 5001

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# After USER appuser but before CMD
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_CMD_ARGS="--log-level debug"
# Use gunicorn for production
CMD ["gunicorn", "app:app", "--workers=4", "--bind=0.0.0.0:5001", "--timeout=120"]
