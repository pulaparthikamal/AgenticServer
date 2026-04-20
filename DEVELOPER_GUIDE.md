# 🚀 Developer Guide: Scaling Your Agents

This guide provides the technical knowledge needed to expand your fleet of agents and manage the project logic.

---

## 📂 1. The "Whose File is it Anyway?" Map (Visual)

| Component                | Files                        | Purpose                                |
| :----------------------- | :--------------------------- | :------------------------------------- |
| **Simple Agent Scaling** | `apps/agents/crewai/config/` | YAML agent/task definitions (No-Code). |
| **Complex Agent Logic**  | `apps/agents/crewai/crews/`  | Advanced Python logic Classes (Code).  |
| **API Layer**            | `apps/api/schemas.py`        | JSON request/response formats.         |
| **Observability**        | `apps/api/models.py`         | Generation history & audit trail.      |
| **Brain Config**         | `config/settings.py`         | LLM providers, temperatures, & keys.   |
| **Extra Powers**         | `apps/agents/crewai/tools/`  | Custom Python tools (Scrapers, DBs).   |

---

## 📝 2. Quick Checklist: Where to make changes?

### ✅ To add a standard Research/Writer Agent:

1.  Add the Role/Goal to **`apps/agents/crewai/config/agents.yaml`**.
2.  Add the Task to **`apps/agents/crewai/config/tasks.yaml`**.
3.  Request using `"crew_type": "dynamic"` in your API call.

### ✅ To add a specialized Python-based Crew:

1.  Create a new file in **`apps/agents/crewai/crews/`** (e.g. `market_crew.py`).
2.  Use the `@register_crew("market")` decorator on your class.
3.  The system finds it **automatically**—no other files need changing!

---

## 🎨 3. Example: Adding a "SEO Optimizer" Agent (YAML)

**Step 1**: Edit `apps/agents/crewai/config/agents.yaml`:

```yaml
seo_agent:
  role: SEO Specialist
  goal: Research top 5 keywords for {topic}
  backstory: You are an expert in Google search algorithms...
```

**Step 2**: Edit `apps/agents/crewai/config/tasks.yaml`:

```yaml
optimization_task:
  description: Find keywords for {topic}
  expected_output: List of 5 keywords
  agent: seo_agent
```

---

## 💻 4. Example: Adding a "Finance" Crew (Python)

Create `apps/agents/crewai/crews/finance_crew.py`:

```python
from .base import BaseCrew
from .registry import register_crew
from crewai import Agent, Task

@register_crew("finance")  # Registers the 'finance' crew_type
class FinanceCrew(BaseCrew):
    def setup_agents(self, inputs):
        return [Agent(role="Analyst", goal="Check stock for {topic}", llm=self.llm)]

    def setup_tasks(self, agents, inputs):
        return [Task(description="Fetch prices", agent=agents[0], expected_output="Price table")]
```

---

## 🔗 5. Testing your API

**Endpoint**: `POST http://localhost:8000/api/v1/content/generate`

**Payload**:

```json
{
  "topic": "Bitcoin",
  "crew_type": "dynamic",
  "tone": "Academic",
  "word_count": 500
}
```

---

## 📊 6. Observability

Use `docker compose logs -f` to track every step of the agent's workflow. Every request is tagged with a unique **ID** (e.g., `[92164c64]`) that you can find in the Django Admin for audit later.
