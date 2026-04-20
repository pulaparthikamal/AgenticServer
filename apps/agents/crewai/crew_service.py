from __future__ import annotations
from dataclasses import dataclass
from .parser import parse_final_output
from .schemas import ContentGenerationRequest, ResearchBundle
from .settings import ServiceSettings
from .crews.registry import get_crew_class

@dataclass
class CrewExecutionResult:
    parsed_output: dict[str, object]
    raw_final_output: str
    # These fields can be expanded or made generic if needed
    full_output: str 

class ContentCrewService:
    """
    Generic orchestration service that dispatches requests to specialized Crews.
    """
    def __init__(self, settings: ServiceSettings) -> None:
        self.settings = settings

    def run(
        self,
        request: ContentGenerationRequest,
        research: ResearchBundle,
    ) -> CrewExecutionResult:
        # 1. Resolve which Crew class to use based on the request
        crew_class = get_crew_class(request.crew_type)
        
        # 2. Instantiate and run the crew
        crew_instance = crew_class(self.settings)
        
        # 3. Prepare contextual inputs for the agents
        inputs = {
            "request": request,
            "research": research
        }
        
        # 4. Execute
        crew_output = crew_instance.run(inputs)
        
        # 5. Extract results
        raw_final = str(getattr(crew_output, "raw", "") or str(crew_output)).strip()
        parsed = parse_final_output(raw_final)

        return CrewExecutionResult(
            parsed_output=parsed,
            raw_final_output=raw_final,
            full_output=raw_final
        )
