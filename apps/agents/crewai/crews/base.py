from abc import ABC, abstractmethod
from typing import Any
import yaml
import os
from pathlib import Path
from crewai import Agent, Crew, LLM, Process, Task
from ..settings import ServiceSettings

class BaseCrew(ABC):
    """
    Abstract base class for all Agentic Crews.
    Provides shared LLM initialization and execution logic.
    """
    def __init__(self, settings: ServiceSettings) -> None:
        self.settings = settings
        self.llm = self._build_llm()
        self.config_dir = Path(__file__).resolve().parent.parent / "config"

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
            process=Process.sequential,
            verbose=False,
        )
        return crew.kickoff()

    def _build_llm(self) -> LLM:
        provider = self.settings.llm_provider
        if provider == "openai":
            model = self.settings.llm_model or "gpt-4o-mini"
            kwargs = {
                "model": model,
                "temperature": self.settings.ollama_temperature,
            }
            if self.settings.openai_api_key:
                kwargs["api_key"] = self.settings.openai_api_key
            if self.settings.openai_base_url:
                kwargs["base_url"] = self.settings.openai_base_url
            return LLM(**kwargs)

        model = self.settings.llm_model or self.settings.ollama_model
        return LLM(
            model=model,
            base_url=self.settings.ollama_base_url,
            temperature=self.settings.ollama_temperature,
        )
