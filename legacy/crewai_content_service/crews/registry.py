from __future__ import annotations
from typing import Type
from .base import BaseCrew
from .content_crew import ContentCrew
from .linkedin_crew import LinkedInCrew

# Registry of available crews
# Developers can add new crews here
CREW_REGISTRY: dict[str, Type[BaseCrew]] = {
    "content": ContentCrew,
    "linkedin_trends": LinkedInCrew,
}

def get_crew_class(crew_type: str = "content") -> Type[BaseCrew]:
    """Returns the Class for the requested crew type."""
    return CREW_REGISTRY.get(crew_type.lower(), ContentCrew)
