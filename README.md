# Aevor AI

AI microservice within the Aevor platform powering repository intelligence, diff summarization, and contribution assistance.

---

## Architecture & Service Contract

Aevor AI operates as an independent microservice that communicates with the **Aevor Platform** over HTTP REST APIs.

### Canonical Route Contract

All versioned endpoints use the **`/v1`** prefix directly to align with the Aevor Platform client:

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `GET /v1/health` | `GET` | **Canonical Liveness Probe**: Verifies the service is healthy. |
| `GET /v1/ready` | `GET` | **Canonical Readiness Probe**: Confirms the service is ready for traffic. |
| `POST /v1/summarize-diff` | `POST` | **Diff Summarization**: Accepts a Git diff and returns a structured `PRSummary`. |
| `GET /` | `GET` | Service root status check. |

---

## Two-Service Local Setup

The local development environment consists of the Aevor Platform and the Aevor AI microservice:

| Component | Repository | Runtime | Default Port | Default Config / Address |
| :--- | :--- | :--- | :--- | :--- |
| **Aevor Platform** | `Aevor/platform` | Go | `8080` | `AI_SERVICE_URL=http://localhost:11434` |
| **Aevor AI** | `Aevor/ai` | Python / FastAPI | `11434` | `HOST=0.0.0.0`, `PORT=11434` |

### Running Locally

1. **Clone and setup virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` and provide your Gemini API key:
   ```bash
   cp .env.example .env
   ```

3. **Start the AI service**:
   Run via the module entrypoint:
   ```bash
   python -m services.main
   ```
   Or using Uvicorn directly:
   ```bash
   uvicorn services.main:app --host 0.0.0.0 --port 11434
   ```

4. **Verify service readiness**:
   ```bash
   curl http://localhost:11434/v1/health
   # Returns: {"status":"healthy","environment":"development","app_name":"Aevor AI"}
   ```

---

## Running with Docker

To build and run the containerized service locally:

```bash
# Build the Docker image
docker build -t aevor-ai .

# Run the container on port 11434
docker run -p 11434:11434 --env-file .env aevor-ai
```

---

## Environment Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HOST` / `AI_SERVICE_HOST` | `0.0.0.0` | Bind network host address. |
| `PORT` / `AI_SERVICE_PORT` | `11434` | Bind network port (aligns with Platform default `11434`). |
| `GEMINI_API_KEY` | `""` | Google Gemini API key. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name for structured inference. |
| `MAX_DIFF_SIZE_CHARS` | `100000` | Maximum character length allowed for incoming Git diffs. |
| `LOG_LEVEL` | `INFO` | Application log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `DEBUG` | `false` | Enable FastAPI debug mode. |

---

## Running Tests

Run the full automated test suite:

```bash
pytest
```
