# Aevor AI

AI microservice within the Aevor platform powering repository intelligence, diff summarization, and contribution assistance.

---

## Architecture & Service Contract

Aevor AI operates as an independent microservice that communicates with the **Aevor Platform** over HTTP REST APIs.

### Currently Implemented Routes

All currently implemented versioned endpoints use the shared `/v1` prefix.

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `GET /v1/health` | GET | Liveness probe: verifies that the service is healthy. |
| `GET /v1/ready` | GET | Readiness probe: confirms that the service is ready for traffic. |
| `POST /v1/summarize-diff` | POST | Accepts a Git diff and returns a structured `PRSummary`. |
| `GET /` | GET | Service root status check. |

### Planned Platform Inference Operations

The following API operations are planned for future implementation and are not yet available in the current service:

- `/v1/analyze`
- `/v1/analyze-repository`
- `/v1/analyze-issue`
- `/v1/propose-solution`
- `/v1/generate-changes`
- `/v1/analyze-impact`
- `/v1/analyze-pr-feedback`
- `/v1/analyze-validation`

---

## Two-Service Local Setup

The local development environment consists of the Aevor Platform and the Aevor AI microservice:

| Component | Repository | Runtime | Default Port | Default Config / Address |
| :--- | :--- | :--- | :--- | :--- |
| **Aevor Platform** | `Aevor/platform` | Go | `8080` | `AI_SERVICE_URL=http://localhost:11434` |
| **Aevor AI** | `Aevor/ai` | Python / FastAPI | `11434` | `HOST=0.0.0.0`, `PORT=11434` |

### Running Locally

1. **Clone the repository and set up a virtual environment:**

   ```bash
   python -m venv .venv

   # Windows:
   .venv\Scripts\activate

   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configure environment variables:**

   Copy `.env.example` to `.env` and replace the placeholder Gemini API key with your own key.

   ```bash
   cp .env.example .env
   ```

   Keep your `.env` file private. Never commit API keys or other secrets to the repository.

3. **Start the AI service:**

   Run using the module entrypoint:

   ```bash
   python -m services.main
   ```

   Or use Uvicorn directly:

   ```bash
   uvicorn services.main:app --host 0.0.0.0 --port 11434
   ```

4. **Verify service readiness:**

   ```bash
   curl http://localhost:11434/v1/health
   ```

   Expected response:

   ```json
   {
     "status": "healthy",
     "environment": "development",
     "app_name": "Aevor AI"
   }
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
The `.dockerignore` file excludes environment secrets, Git metadata, virtual environments, and unnecessary development files from the Docker build context.

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
