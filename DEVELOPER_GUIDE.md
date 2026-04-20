# 🚀 Developer Guide: Scaling Your Agents

This guide explains the project structure and provides step-by-step examples for adding new agents and automation workflows.

---

## 📂 1. Key File Registry

| File Path | Purpose |
| :--- | :--- |
| `apps/agents/crewai/crews/` | **Put new agent code here.** Any file added here is auto-discovered. |
| `apps/agents/crewai/config/` | **YAML Configs.** Define agents and tasks without writing code. |
| `apps/agents/crewai/tools/` | **Custom Tools.** Put Python scripts for agents to use (browser, database, etc). |
| `apps/api/api_v1.py` | **API Layer.** Handles incoming requests and maps them to agents. |
| `config/settings.py` | **Core Settings.** Django and environment variable configurations. |

---

## 📝 Quick Checklist: Where to make changes?

Depending on your goal, you only need to touch **one or two** specific files:

### ✅ To add a standard agent (YAML):
1.  **`apps/agents/crewai/config/agents.yaml`** (Add Role/Goal)
2.  **`apps/agents/crewai/config/tasks.yaml`** (Add Task description)

### ✅ To add a complex agent (Python):
1.  **`apps/agents/crewai/crews/`** (Create a new `.py` file with `@register_crew`)

### ✅ To give agents new powers:
1.  **`apps/agents/crewai/tools/`** (Add your custom Python tool scripts)

---

## 🎨 2. Adding Agents: The EASY Way (YAML Config)
Use this method if you want to quickly create an agent behavior by just writing plain text.

### Step 1: Update `apps/agents/crewai/config/agents.yaml`
Add your new agent definition:
```yaml
seo_analyst:
  role: >
    SEO Strategy Expert
  goal: >
    Optimize the content for {topic} with high-ranking keywords.
  backstory: >
    You are a veteran SEO specialist. You ensure every piece of content 
    is primed for Google search results.
```

### Step 2: Update `apps/agents/crewai/config/tasks.yaml`
Define what this agent should actually do:
```yaml
seo_task:
  description: >
    Review the draft for {topic} and add 5 relevant meta-tags.
  expected_output: >
    A list of 5 SEO-optimized keywords and a meta-description.
  agent: seo_analyst
```

### Step 3: Trigger via API
In your POST request to `http://localhost:8000/api/v1/content/generate`, use:
```json
{
  "topic": "Blockchain",
  "crew_type": "dynamic"
}
```

---

## 💻 3. Adding Agents: The CODING Way (Python)
Use this method if you need custom logic, specific tools, or complex decision-making.

### Step 1: Create `apps/agents/crewai/crews/research_crew.py`
Create a new file and paste this template:

```python
from crewai import Agent, Task
from .base import BaseCrew
from .registry import register_crew

@register_crew("deep_research")  # <--- THIS REGISTERS IT AUTOMATICALLY
class ResearchCrew(BaseCrew):
    def setup_agents(self, inputs):
        return [
            Agent(
                role="Deep Researcher",
                goal="Find 10 obscure facts about {topic}",
                backstory="You are a data detective...",
                llm=self.llm
            )
        ]

    def setup_tasks(self, agents, inputs):
        return [
            Task(
                description="Scan the web for {topic} insights.",
                expected_output="Top 10 list.",
                agent=agents[0]
            )
        ]
```

### Step 2: Trigger via API
Simply change the `crew_type` in your request:
```json
{
  "topic": "Quantum Computing",
  "crew_type": "deep_research"
}
```

---

## 🔗 4. Testing with n8n / Postman
Always ensure your payload follows the industry-standard structure we've implemented:

**Endpoint**: `POST http://<SERVER_IP>:8000/api/v1/content/generate`

**Body**:
```json
{
  "topic": "Your Topic",
  "crew_type": "content", 
  "tone": "Professional",
  "audience": "CEOs",
  "brand_voice": "Bold",
  "word_count": 500
}
```
