from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException

from .crew_service import ContentCrewService
from .repository import TopicRepository
from .research import ResearchCollector
from .schemas import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    HealthResponse,
    ResolvedTopic,
)
from .settings import load_settings


settings = load_settings()
repository = TopicRepository(settings)
research_collector = ResearchCollector(settings)
crew_service = ContentCrewService(settings)

app = FastAPI(
    title="CrewAI Ollama Content API",
    version="1.0.0",
    description="Standalone content-generation workflow for n8n, CrewAI, and Ollama.",
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    llm_base_url = (
        settings.openai_base_url
        if settings.llm_provider == "openai"
        else settings.ollama_base_url
    )
    llm_model = settings.llm_model or (
        "gpt-4o-mini" if settings.llm_provider == "openai" else settings.ollama_model
    )
    return HealthResponse(
        status="ok",
        service="crewai-ollama-content-api",
        llm_provider=settings.llm_provider,
        ollama_reachable=research_collector.check_ollama() if settings.llm_provider == "ollama" else True,
        llm_model=llm_model,
        llm_base_url=llm_base_url,
        mongo_configured=repository.enabled,
    )


@app.post(
    f"{settings.api_prefix}/content/generate",
    response_model=ContentGenerationResponse,
)
def generate_content(payload: ContentGenerationRequest) -> ContentGenerationResponse:
    request_id = str(uuid4())
    resolved_topic = _resolve_topic(payload)
    research_bundle = research_collector.build_bundle(payload, resolved_topic)

    try:
        crew_result = crew_service.run(payload, research_bundle)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CrewAI execution failed: {exc}") from exc

    parsed = crew_result.parsed_output
    final_content = str(parsed["content"]).strip()
    title = str(parsed["title"]).strip()
    summary = str(parsed["summary"]).strip()
    hashtags = list(parsed.get("hashtags", []))
    keywords = list(parsed.get("keywords", [])) or payload.keywords
    image_prompt = str(parsed.get("image_prompt", "")).strip()

    output_collection_id = None
    should_save = (
        payload.save_result
        if payload.save_result is not None
        else settings.save_result_by_default
    )
    should_mark_processed = (
        payload.mark_topic_processed
        if payload.mark_topic_processed is not None
        else settings.mark_topic_processed_by_default
    )

    if should_save and repository.enabled:
        record = {
            "request_id": request_id,
            "topic": resolved_topic.topic,
            "topic_id": resolved_topic.topic_id,
            "title": title,
            "summary": summary,
            "content": final_content,
            "hashtags": hashtags,
            "keywords": keywords,
            "image_prompt": image_prompt if image_prompt else None,
            "source_urls": research_bundle.source_urls,
            "source_count": research_bundle.source_count,
            "metadata": payload.metadata,
            "created_at": datetime.now(timezone.utc),
        }
        output_collection_id = repository.save_generation(record)

    if should_mark_processed and repository.enabled and resolved_topic.topic_id:
        repository.mark_processed(resolved_topic.topic_id, resolved_topic.topic)

    debug = None
    if payload.include_debug:
        debug = {
            "full_output": crew_result.full_output,
            "raw_final_output": crew_result.raw_final_output,
            "research_text": research_bundle.research_text,
        }

    extra_kwargs = payload.model_extra or {}

    response_obj = ContentGenerationResponse(
        status="success",
        message="Content generated successfully",
        request_id=request_id,
        topic=resolved_topic.topic,
        title=title,
        summary=summary,
        content=final_content,
        final_content=final_content,
        hashtags=hashtags,
        keywords=keywords,
        source_urls=research_bundle.source_urls,
        source_count=research_bundle.source_count,
        image_prompt=image_prompt if image_prompt else None,
        output_collection_id=output_collection_id,
        debug=debug,
        **extra_kwargs
    )

    return response_obj


@app.post(
    f"{settings.api_prefix}/content/generate/queue",
    response_model=ContentGenerationResponse,
)
def generate_content_from_queue(payload: ContentGenerationRequest) -> ContentGenerationResponse:
    queue_payload = payload.model_copy(update={"use_topic_queue": True})
    return generate_content(queue_payload)


def _resolve_topic(payload: ContentGenerationRequest) -> ResolvedTopic:
    if payload.topic_id:
        if not repository.enabled:
            raise HTTPException(status_code=400, detail="MongoDB is not configured for topic_id lookup.")
        topic = repository.fetch_topic_by_id(payload.topic_id)
        if topic is None:
            raise HTTPException(status_code=404, detail="Topic document not found.")
        return topic

    if payload.use_topic_queue:
        if not repository.enabled:
            raise HTTPException(status_code=400, detail="MongoDB is not configured for queue mode.")
        topic = repository.fetch_next_topic()
        if topic is None:
            raise HTTPException(status_code=404, detail="No pending topics found in the queue.")
        return topic

    if payload.topic:
        return ResolvedTopic(topic=payload.topic.strip())

    if payload.research_text:
        return ResolvedTopic(topic="Generated Topic")

    if payload.source_urls:
        return ResolvedTopic(topic="Content from provided sources")

    raise HTTPException(status_code=400, detail="Unable to resolve a topic from the request payload.")


if __name__ == "__main__":
    uvicorn.run(
        "crewai_content_service.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=False,
    )
