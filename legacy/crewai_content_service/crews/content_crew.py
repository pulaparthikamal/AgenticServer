from __future__ import annotations
from typing import Any
from crewai import Agent, Task
from .base import BaseCrew
from ..prompts import (
    WRITER_BACKSTORY,
    REVIEWER_BACKSTORY,
    OPTIMIZER_BACKSTORY,
    FINAL_OUTPUT_TEMPLATE,
)

class ContentCrew(BaseCrew):
    """
    Standard Content Generation Crew consisting of a Writer, Reviewer, and Optimizer.
    """
    def setup_agents(self, inputs: dict[str, Any]) -> list[Agent]:
        writer = Agent(
            role="Writer Agent",
            goal="Draft clear, compelling, research-grounded professional content.",
            backstory=WRITER_BACKSTORY,
            llm=self.llm,
            allow_delegation=False,
        )
        reviewer = Agent(
            role="Reviewer Agent",
            goal="Critique the draft for accuracy, structure, repetition, and clarity.",
            backstory=REVIEWER_BACKSTORY,
            llm=self.llm,
            allow_delegation=False,
        )
        optimizer = Agent(
            role="Optimizer Agent",
            goal="Produce the final publication-ready version optimized for automation.",
            backstory=OPTIMIZER_BACKSTORY,
            llm=self.llm,
            allow_delegation=False,
        )
        return [writer, reviewer, optimizer]

    def setup_tasks(self, agents: list[Agent], inputs: dict[str, Any]) -> list[Task]:
        writer, reviewer, optimizer = agents
        
        # Extract inputs (request/research data)
        request = inputs.get("request")
        research = inputs.get("research")
        
        keywords = ", ".join(request.keywords) if request.keywords else "None provided"
        brand_voice = request.brand_voice or "Balanced, trustworthy, and useful"
        call_to_action = request.call_to_action or "Close with one practical call to action."

        writer_task = Task(
            description=(
                f"Create a first draft about the topic '{research.topic}'.\n"
                f"Audience: {request.audience}\n"
                f"Tone: {request.tone}\n"
                f"Brand voice: {brand_voice}\n"
                f"Desired length: {request.word_count} words\n"
                f"Priority keywords: {keywords}\n"
                f"Use only the provided material when making specific claims.\n\n"
                f"Research material:\n{research.research_text}"
            ),
            expected_output="A well-structured draft with a working title and hashtags.",
            agent=writer,
        )

        reviewer_task = Task(
            description="Review the writer draft. Identify factual overreach and repetition.",
            expected_output="Editorial review notes.",
            agent=reviewer,
            context=[writer_task],
        )

        optimizer_task = Task(
            description=(
                "Rewrite into the final version.\n"
                f"{call_to_action}\n"
                f"{FINAL_OUTPUT_TEMPLATE}"
            ),
            expected_output=FINAL_OUTPUT_TEMPLATE,
            agent=optimizer,
            context=[writer_task, reviewer_task],
        )

        return [writer_task, reviewer_task, optimizer_task]
