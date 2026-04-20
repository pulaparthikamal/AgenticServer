# 🔗 Agentic Server (Django + CrewAI)

A professional, industry-standard backend for orchestrating **CrewAI** multi-agent systems. Built for scalability, observability, and high-performance automation.

---

## 🚀 PHASE 1: Execution (Choose your path)

### Option A: Using Docker (Professional/Recommended)

Best for production-like consistency and ease of deployment.

```bash
# 1. Build and Start
docker compose up -d --build

# 2. Setup Database (First time only)
docker compose run --rm agent_server python manage.py migrate

# 3. Watch Agents Thinking
docker compose logs -f agent_server
```

### Option B: Running Locally (Non-Docker)

Best for fast iteration and local experimentation.

```bash
# 1. Environment Configuration
# Create .env file with your OPENAI_API_KEY and OLLAMA_BASE_URL

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Initialize Database
python manage.py migrate

# 4. Start Server
python manage.py runserver
```

---

## 📊 PHASE 2: Monitoring & Audit

### 🕒 Generation History

Every time an agent runs, the result is saved internally. You can view these in the **Django Admin**:

1.  **Create Admin User**: `docker compose run --rm agent_server python manage.py createsuperuser`
2.  **Login**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
3.  **Browse History**: View topics, content, execution time, and LLM metadata in the "Generation Histories" section.

## 📂 Project Structure

- **`config/`**: Django system settings & global configurations.
- **`apps/api/`**: API endpoints & request schemas (Django Ninja).
- **`apps/agents/crewai/`**: The core multi-agent engine (Crews, Tools, Logic).
- **`apps/agents/crewai/config/`**: YAML agent/task definitions for scaling.

---

### 📁 Detailed Folder Structure

```text
AgenticServer/
├── config/                 # ⚙️ Django Core
│   ├── settings.py         # Unified Config
│   └── urls.py             # Main Routing
├── apps/
│   ├── api/                # 🌐 Web Layer
│   │   ├── api_v1.py       # Endpoints
│   │   ├── schemas.py      # Data Models
│   │   └── models.py       # History DB
│   └── agents/             # 🧠 Brain Layer
│       └── crewai/
│           ├── crews/      # Agent Classes
│           ├── config/     # YAML Definitions
│           └── tools/      # Custom Powers
├── Dockerfile              # 🐳 Packaging
└── docker-compose.yml      # 📦 Orchestration
```
