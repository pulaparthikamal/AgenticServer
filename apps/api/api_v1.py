from ninja import NinjaAPI, Schema
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from django.conf import settings
from agents.crewai.crew_service import ContentCrewService
from agents.crewai.repository import TopicRepository, ResolvedTopic
from agents.crewai.research import ResearchCollector
from .schemas import ContentGenerationRequest, ContentGenerationResponse, HealthResponse

api = NinjaAPI(title="Agentic Server API", version="1.0.0")

# Load logic using Django settings
repository = TopicRepository(settings)
research_collector = ResearchCollector(settings)
crew_service = ContentCrewService()

@api.get("/health", response=HealthResponse)
def health_check(request):
    llm_base_url = (
        settings.OPENAI_BASE_URL
        if settings.LLM_PROVIDER == "openai"
        else settings.OLLAMA_BASE_URL
    )
    llm_model = settings.LLM_MODEL or (
        "gpt-4o-mini" if settings.LLM_PROVIDER == "openai" else settings.OLLAMA_MODEL
    )
    return {
        "status": "ok",
        "service": "agentic-server-django",
        "llm_provider": settings.LLM_PROVIDER,
        "ollama_reachable": research_collector.check_ollama() if settings.LLM_PROVIDER == "ollama" else True,
        "llm_model": llm_model,
        "llm_base_url": llm_base_url,
        "mongo_configured": repository.enabled,
    }

@api.post("/content/generate", response=ContentGenerationResponse)
def generate_content(request, payload: ContentGenerationRequest):
    request_id = str(uuid4())
    resolved_topic = _resolve_topic(payload)
    research_bundle = research_collector.build_bundle(payload, resolved_topic)

    try:
        crew_result = crew_service.run(payload, research_bundle)
    except Exception as exc:
        return api.create_response(request, {"detail": f"CrewAI execution failed: {exc}"}, status=502)

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
        else settings.SAVE_RESULT_DEFAULT
    )
    should_mark_processed = (
        payload.mark_topic_processed
        if payload.mark_topic_processed is not None
        else settings.MARK_TOPIC_PROCESSED_DEFAULT
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

    return {
        "status": "success",
        "message": "Content generated successfully",
        "request_id": request_id,
        "topic": resolved_topic.topic,
        "title": title,
        "summary": summary,
        "content": final_content,
        "final_content": final_content,
        "hashtags": hashtags,
        "keywords": keywords,
        "source_urls": research_bundle.source_urls,
        "source_count": research_bundle.source_count,
        "image_prompt": image_prompt if image_prompt else None,
        "output_collection_id": output_collection_id,
        "debug": debug,
    }

def _resolve_topic(payload: ContentGenerationRequest) -> ResolvedTopic:
    if payload.topic_id:
        if not repository.enabled:
            return api.create_response(None, {"detail": "MongoDB is not configured for topic_id lookup."}, status=400)
        topic = repository.fetch_topic_by_id(payload.topic_id)
        if topic is None:
            return api.create_response(None, {"detail": "Topic document not found."}, status=404)
        return topic

    if payload.use_topic_queue:
        if not repository.enabled:
            return api.create_response(None, {"detail": "MongoDB is not configured for queue mode."}, status=400)
        topic = repository.fetch_next_topic()
        if topic is None:
            return api.create_response(None, {"detail": "No pending topics found in the queue."}, status=404)
        return topic

    if payload.topic:
        return ResolvedTopic(topic=payload.topic.strip())

    if payload.research_text:
        return ResolvedTopic(topic="Generated Topic")

    if payload.source_urls:
        return ResolvedTopic(topic="Content from provided sources")

    return api.create_response(None, {"detail": "Unable to resolve a topic from the request payload."}, status=400)
