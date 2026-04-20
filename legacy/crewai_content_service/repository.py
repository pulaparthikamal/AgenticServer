from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import MongoClient

from .schemas import ResolvedTopic
from .settings import ServiceSettings


class TopicRepository:
    def __init__(self, settings: ServiceSettings) -> None:
        self.settings = settings
        self._client: MongoClient | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.settings.mongo_uri and self.settings.mongo_db_name)

    def _get_collection(self, collection_name: str):
        if not self.enabled:
            raise RuntimeError("MongoDB is not configured for this service.")
        if self._client is None:
            self._client = MongoClient(self.settings.mongo_uri)
        return self._client[self.settings.mongo_db_name][collection_name]

    def fetch_next_topic(self) -> ResolvedTopic | None:
        collection = self._get_collection(self.settings.mongo_topics_collection)
        query = {
            "$or": [
                {"status": {"$ne": "processed"}},
                {"isContentGenerated": {"$ne": True}},
            ]
        }
        document = collection.find_one(query, sort=[("created", 1), ("_id", 1)])
        return self._to_resolved_topic(document)

    def fetch_topic_by_id(self, topic_id: str) -> ResolvedTopic | None:
        collection = self._get_collection(self.settings.mongo_topics_collection)
        try:
            object_id = ObjectId(topic_id)
        except Exception:
            return None
        document = collection.find_one({"_id": object_id})
        return self._to_resolved_topic(document)

    def mark_processed(self, topic_id: str | None, topic: str) -> None:
        collection = self._get_collection(self.settings.mongo_topics_collection)
        update = {
            "$set": {
                "status": "processed",
                "isContentGenerated": True,
                "processed_at": datetime.now(timezone.utc),
            }
        }
        if topic_id:
            try:
                object_id = ObjectId(topic_id)
            except Exception:
                object_id = None
            if object_id is not None:
                collection.update_one({"_id": object_id}, update)
                return
        collection.update_one({"topic": topic}, update)

    def save_generation(self, payload: dict[str, Any]) -> str:
        collection = self._get_collection(self.settings.mongo_output_collection)
        result = collection.insert_one(payload)
        return str(result.inserted_id)

    def _to_resolved_topic(self, document: dict[str, Any] | None) -> ResolvedTopic | None:
        if not document:
            return None
        topic_value = (
            document.get("topic")
            or document.get("title")
            or document.get("name")
            or document.get("subject")
        )
        if not topic_value:
            return None

        context_parts: list[str] = []
        for field_name in ("description", "notes", "brief", "summary", "keywords"):
            value = document.get(field_name)
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value if item)
            if value:
                context_parts.append(f"{field_name}: {value}")

        return ResolvedTopic(
            topic_id=str(document.get("_id")),
            topic=str(topic_value).strip(),
            mongo_document=document,
            additional_context="\n".join(context_parts) or None,
        )
