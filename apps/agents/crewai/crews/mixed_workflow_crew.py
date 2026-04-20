from crewai import Agent, Task
from .base import BaseCrew
from .registry import register_crew

@register_crew("mixed_example")
class MixedWorkflowCrew(BaseCrew):
    """
    Industry Standard Example: Mixed Parallel & Serial Workflow.
    
    Workflow Pattern: Fan-Out (Parallel) -> Fan-In (Serial/Consolidation)
    """
    def setup_agents(self, inputs):
        # Workers (To run in Parallel)
        self.market_analyst = Agent(
            role="Market Data Analyst",
            goal="Extract raw financial data for {topic}",
            backstory="You are a data crawler specializing in hard numbers.",
            llm=self.llm
        )
        
        self.sentiment_analyst = Agent(
            role="Social Sentiment Analyst",
            goal="Gauge public opinion on {topic}",
            backstory="You are an expert in social psychology and trend mapping.",
            llm=self.llm
        )
        
        # Manager/Consolidator (To run in Serial after workers finish)
        self.writer = Agent(
            role="Chief Editor",
            goal="Consolidate all findings into a master report for {topic}",
            backstory="You are a veteran editor who excels at critical synthesis.",
            llm=self.llm
        )
        
        return [self.market_analyst, self.sentiment_analyst, self.writer]

    def setup_tasks(self, agents, inputs):
        # --- PARALLEL TASKS (Fan-Out) ---
        # These two tasks run simultaneously to save time.
        market_task = Task(
            description="Fetch prices and volume for {topic}.",
            expected_output="A table of market metrics.",
            agent=self.market_analyst,
            async_execution=True  # ⚡ Parallel Execution Mode
        )
        
        sentiment_task = Task(
            description="Fetch social sentiment and mentions for {topic}.",
            expected_output="A sentiment score map.",
            agent=self.sentiment_analyst,
            async_execution=True  # ⚡ Parallel Execution Mode
        )

        # --- SERIAL TASK (Fan-In / Synthesis) ---
        # This task waits for the parallel tasks and combines them.
        summary_task = Task(
            description="Merge the market data and sentiment data into a final analysis.",
            expected_output="A professional 2-page research report.",
            agent=self.writer,
            context=[market_task, sentiment_task]  # 🧩 Merges outputs from previous tasks
        )
        
        return [market_task, sentiment_task, summary_task]
