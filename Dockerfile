FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=11434

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source code
COPY . .

# Expose default service port (matches Aevor Platform default AI_SERVICE_URL: http://localhost:11434)
EXPOSE 11434

# Run the FastAPI server
CMD ["python", "-m", "services.main"]
