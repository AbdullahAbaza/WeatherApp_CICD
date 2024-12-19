# stage 1: build
FROM python:3.10-alpine3.21 AS builder

WORKDIR /app

COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# stage 2: Production stage
FROM python:3.10-alpine3.21

# Create a non-root user
RUN adduser --disabled-password appuser

WORKDIR /app

# Copy only the necessary files
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY /app/ .

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

EXPOSE 5001

# Add a health check
HEALTHCHECK CMD curl --fail http://localhost:5001/health || exit 1

CMD [ "python", "app.py"]