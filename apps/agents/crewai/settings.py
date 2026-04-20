from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVICE_DIR = Path(__file__).resolve().parent


def _load_env_files() -> None:
    load_dotenv(SERVICE_DIR / ".env", override=False)
    load_dotenv(ROOT_DIR / ".env_variables", override=False)


def _load_legacy_config() -> dict[str, Any]:
    try:
        from RAG_Llama3.config import config as legacy_config

        return legacy_config
    except Exception:
        return {}


def _env(name: str, default: Any = None) -> Any:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    value = _env(name)
    if value is None:
        return default
    return float(value)


def _env_int(name: str, default: int) -> int:
    value = _env(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class ServiceSettings:
    service_host: str
    service_port: int
    api_prefix: str
    request_timeout_seconds: int
    max_search_results: int
    max_scrape_sources: int
    max_chars_per_source: int
    user_agent: str
    llm_provider: str
    llm_model: str
    openai_api_key: str | None
    openai_base_url: str | None
    ollama_base_url: str
    ollama_model: str
    ollama_temperature: float
    ollama_timeout_seconds: int
    google_cse_api_key: str | None
    google_cse_id: str | None
    mongo_uri: str | None
    mongo_db_name: str | None
    mongo_topics_collection: str
    mongo_output_collection: str
    save_result_by_default: bool
    mark_topic_processed_by_default: bool


def load_settings() -> ServiceSettings:
    _load_env_files()
    legacy_config = _load_legacy_config()

    mongo_default = legacy_config.get("mongodb_config", {})
    mongo_content_default = legacy_config.get("mongodb_config_content_generation", {})

    mongo_uri = _env(
        "CREWAI_CONTENT_MONGO_URI",
        mongo_content_default.get("mongo_connection")
        or mongo_default.get("mongo_connection_string"),
    )
    mongo_db_name = _env(
        "CREWAI_CONTENT_MONGO_DB",
        mongo_content_default.get("db_name") or mongo_default.get("db_name"),
    )

    return ServiceSettings(
        service_host=_env("CREWAI_CONTENT_HOST", "0.0.0.0"),
        service_port=_env_int("CREWAI_CONTENT_PORT", 8090),
        api_prefix=_env("CREWAI_CONTENT_API_PREFIX", "/api/v1"),
        request_timeout_seconds=_env_int("CREWAI_CONTENT_REQUEST_TIMEOUT", 45),
        max_search_results=_env_int("CREWAI_CONTENT_MAX_SEARCH_RESULTS", 5),
        max_scrape_sources=_env_int("CREWAI_CONTENT_MAX_SCRAPE_SOURCES", 4),
        max_chars_per_source=_env_int("CREWAI_CONTENT_MAX_CHARS_PER_SOURCE", 6000),
        user_agent=_env(
            "CREWAI_CONTENT_USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ),
        llm_provider=_env("CREWAI_CONTENT_LLM_PROVIDER", "ollama").strip().lower(),
        llm_model=_env("CREWAI_CONTENT_LLM_MODEL", ""),
        openai_api_key=_env("CREWAI_CONTENT_OPENAI_API_KEY", _env("OPENAI_API_KEY")),
        openai_base_url=_env("CREWAI_CONTENT_OPENAI_BASE_URL", None),
        ollama_base_url=_env(
            "CREWAI_CONTENT_OLLAMA_BASE_URL",
            legacy_config.get("ollamaUrl", "http://localhost:11434"),
        ),
        ollama_model=_env("CREWAI_CONTENT_OLLAMA_MODEL", "ollama/llama3.1:8b"),
        ollama_temperature=_env_float("CREWAI_CONTENT_OLLAMA_TEMPERATURE", 0.4),
        ollama_timeout_seconds=_env_int("CREWAI_CONTENT_OLLAMA_TIMEOUT", 180),
        google_cse_api_key=_env("GOOGLE_CSE_API_KEY", _env("API_KEY")),
        google_cse_id=_env("GOOGLE_CSE_ID", _env("CX")),
        mongo_uri=mongo_uri,
        mongo_db_name=mongo_db_name,
        mongo_topics_collection=_env("CREWAI_CONTENT_TOPICS_COLLECTION", "topics"),
        mongo_output_collection=_env("CREWAI_CONTENT_OUTPUT_COLLECTION", "generated_content_runs"),
        save_result_by_default=_env_bool("CREWAI_CONTENT_SAVE_RESULT", True),
        mark_topic_processed_by_default=_env_bool(
            "CREWAI_CONTENT_MARK_TOPIC_PROCESSED",
            True,
        ),
    )
