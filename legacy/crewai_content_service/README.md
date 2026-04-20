# CrewAI Ollama Content Service

This is a standalone service that operates alongside the main Django workflow for automated content generation.

## Key Features

- **Multi-Agent Pipeline**: sequential workflow using three specialized agents:
  - `Writer Agent`: Drafts professional, research-grounded content.
  - `Reviewer Agent`: Critiques for accuracy, structure, and clarity.
  - `Optimizer Agent`: Finalizes content for publication and automation.
- **LLM Support**: Built for **Ollama** (Llama 3) but supports OpenAI as a fallback.
- **MongoDB Integration**: Supports topic queueing from the `topics` collection and saves generated output.
- **n8n Ready**: Designed to be triggered by n8n cron jobs or workflows.

## Setup Guides

### Local Setup
1. **Initialize Environment**:
   ```bash
   cd RAG
   python3 -m venv .venv-crewai
   source .venv-crewai/bin/activate
   pip install -r requirements-crewai-ollama.txt
   ```
2. **Configure Environment**:
   Copy `crewai_content_service/.env.example` to `crewai_content_service/.env` and set your provider:
   - **Ollama**: `CREWAI_CONTENT_LLM_PROVIDER=ollama`
   - **OpenAI**: `CREWAI_CONTENT_LLM_PROVIDER=openai`
3. **Run Service**:
   ```bash
   uvicorn crewai_content_service.main:app --host 0.0.0.0 --port 8090
   ```

### Docker Setup
```bash
cd RAG
cp crewai_content_service/.env.example crewai_content_service/.env
docker compose -f docker-compose.crewai-content.yml up --build -d
```

## API Usage Examples

### Generate Content (Direct)
```bash
curl -X POST http://localhost:8090/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI copilots in document management",
    "audience": "Operations leaders",
    "tone": "Professional",
    "saveResult": true
  }'
```

### Process Topic Queue (MongoDB)
```bash
curl -X POST http://localhost:8090/api/v1/content/generate/queue \
  -H "Content-Type: application/json" \
  -d '{"useTopicQueue": true, "saveResult": true}'
```

## n8n Integration
Import the workflow from `n8n/crewai_ollama_content_workflow.json`. The workflow is configured to call the `/generate/queue` endpoint to automate batch processing.

## Service Isolation
This service is intentionally isolated from the main Django app to avoid dependency conflicts. It uses its own virtual environment and requirements file.
