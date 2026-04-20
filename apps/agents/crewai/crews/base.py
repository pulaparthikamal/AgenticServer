from abc import ABC, abstractmethod
from typing import Any
import yaml
import os
from pathlib import Path
from django.conf import settings
from crewai import Agent, Crew, LLM, Process, Task

class BaseCrew(ABC):
    """
    Abstract base class for all Agentic Crews.
    Provides shared LLM initialization and execution logic.
    """
    def __init__(self, service_settings=None, process_type: Process = Process.sequential) -> None:
        # service_settings is kept for backward compat if called from legacy paths
        self.llm = self._build_llm()
        self.config_dir = Path(__file__).resolve().parent.parent / "config"
        self.process_type = process_type

    def _load_config(self, filename: str) -> dict[str, Any]:
        """Loads a YAML configuration file from the config directory."""
        config_path = self.config_dir / filename
        if not config_path.exists():
            return {}
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    @abstractmethod
    def setup_agents(self, inputs: dict[str, Any]) -> list[Agent]:
        """Define and return a list of Agents for this crew."""
        pass

    @abstractmethod
    def setup_tasks(self, agents: list[Agent], inputs: dict[str, Any]) -> list[Task]:
        """Define and return a list of Tasks for this crew."""
        pass

    def run(self, inputs: dict[str, Any]) -> Any:
        """Kicks off the crew execution."""
        agents = self.setup_agents(inputs)
        tasks = self.setup_tasks(agents, inputs)
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=self.process_type,
            verbose=False,
        )
        return crew.kickoff()

    def _build_llm(self) -> LLM:
        provider = settings.LLM_PROVIDER
        if provider == "openai":
            model = settings.LLM_MODEL or "gpt-4o-mini"
            kwargs = {
                "model": model,
                "temperature": settings.OLLAMA_TEMPERATURE,
            }
            if settings.OPENAI_API_KEY:
                kwargs["api_key"] = settings.OPENAI_API_KEY
            if settings.OPENAI_BASE_URL:
                kwargs["base_url"] = settings.OPENAI_BASE_URL
            return LLM(**kwargs)

        model = settings.LLM_MODEL or settings.OLLAMA_MODEL
        return LLM(
            model=model,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.OLLAMA_TEMPERATURE,
        )
