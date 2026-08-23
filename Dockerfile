# Use slim Python 3.10 image for lightweight deployment
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies manifest and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend, frontend, and runner files
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY run_app.py /app/run_app.py

# Expose backend (8000) and Streamlit dashboard (8501)
EXPOSE 8000 8501

# Health check for container readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Launch unified application runner
CMD ["python", "run_app.py"]
