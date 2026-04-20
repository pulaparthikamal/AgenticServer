from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, HttpUrl, model_validator

class ContentGenerationRequest(BaseModel):
    topic_id: str | None = Field(default=None, alias="topicId")
    topic: str | None = None
    use_topic_queue: bool = Field(default=False, alias="useTopicQueue")
    research_text: str | None = Field(default=None, alias="researchText")
    source_urls: list[HttpUrl] = Field(default_factory=list, alias="sourceUrls")
    search_enabled: bool = Field(default=True, alias="searchEnabled")
    audience: str = "Business and LinkedIn readers"
    tone: str = "Professional, practical, and confident"
    brand_voice: str | None = Field(default=None, alias="brandVoice")
    keywords: list[str] = Field(default_factory=list)
    call_to_action: str | None = Field(default=None, alias="callToAction")
    word_count: int = Field(default=800, alias="wordCount", ge=250, le=1800)
    save_result: bool | None = Field(default=None, alias="saveResult")
    mark_topic_processed: bool | None = Field(default=None, alias="markTopicProcessed")
    metadata: dict[str, Any] = Field(default_factory=dict)
    crew_type: str = Field(default="content", alias="crewType")
    include_debug: bool = Field(default=False, alias="includeDebug")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @model_validator(mode="after")
    def validate_input_sources(self) -> "ContentGenerationRequest":
        has_source = any(
            [
                self.topic_id,
                self.topic,
                self.use_topic_queue,
                self.research_text,
                self.source_urls,
            ]
        )
        if not has_source:
            raise ValueError(
                "Provide at least one of topic_id, topic, use_topic_queue, research_text, or source_urls."
            )
        return self

class ResolvedTopic(BaseModel):
    topic_id: str | None = None
    topic: str
    mongo_document: dict[str, Any] | None = None
    additional_context: str | None = None

class ResearchBundle(BaseModel):
    topic: str
    research_text: str
    source_urls: list[str] = Field(default_factory=list)
    source_count: int = 0

class ContentGenerationResponse(BaseModel):
    status: str
    message: str
    request_id: str
    topic: str
    title: str
    summary: str
    content: str
    final_content: str
    hashtags: list[str]
    keywords: list[str]
    source_urls: list[str]
    source_count: int
    image_prompt: str | None = Field(default=None, alias="imagePrompt")
    output_collection_id: str | None = None
    debug: dict[str, Any] | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class HealthResponse(BaseModel):
    status: str
    service: str
    llm_provider: str
    ollama_reachable: bool
    llm_model: str
    llm_base_url: str | None
    mongo_configured: bool
