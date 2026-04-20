FROM python:3.10-slim

WORKDIR /app

COPY requirements-crewai-ollama.txt /app/requirements-crewai-ollama.txt
RUN pip install --no-cache-dir -r /app/requirements-crewai-ollama.txt

COPY crewai_content_service /app/crewai_content_service

EXPOSE 8090

CMD ["uvicorn", "crewai_content_service.main:app", "--host", "0.0.0.0", "--port", "8090"]
