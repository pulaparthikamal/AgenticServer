# 🔗 Agentic Server (Django + CrewAI)

This project is a professional, containerized backend for orchestrating **CrewAI** agents. It follows industry standards for modularity and scalability.

---

## 🛠 PHASE 1: Initial Setup (One-Time Only)
Follow these steps strictly when setting up the project for the first time.

### Step 1: Prepare Environment Variables
Configure your credentials for LLMs (OpenAI or Ollama).
1.  Locate the `.env` file in the root directory.
2.  Ensure it contains your keys:
    ```bash
    # For OpenAI
    OPENAI_API_KEY=sk-xxxx
    
    # For Ollama (Local)
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    ```

### Step 2: Build the Docker Image
This installs Python, Django, CrewAI, and all required tools.
1.  Run the build command:
    ```bash
    docker compose build --no-cache
    ```

### Step 3: Initialize the Database
This creates the internal structure needed for logs and metadata.
1.  Run migrations:
    ```bash
    docker compose run --rm agent_server python manage.py migrate
    ```

---

## 🚀 PHASE 2: Normal Operation (Daily Use)
Follow these steps every time you want to start working.

### Step 1: Start the Server
1.  Run the server in the background:
    ```bash
    docker compose up -d
    ```

### Step 2: Verify it's Running
1.  Check the container status:
    ```bash
    docker ps
    ```
2.  Open your browser and visit:
    - **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
    - **API Documentation**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### Step 3: Watch the Agents Think
1.  To see the real-time research and writing process of your agents:
    ```bash
    docker compose logs -f agent_server
    ```

---

## 🛑 PHASE 3: Stopping the Project
1.  When you are finished, stop and remove the containers:
    ```bash
    docker compose down
    ```

---

## 📈 PHASE 4: Adding "Many Agents" (Scalability)
This project is built to grow. Here is how to add more agents:

### Step 1: Easy Config (No Code)
1.  Navigate to `apps/agents/crewai/config/`.
2.  Add a new agent in `agents.yaml`.
3.  Add a new task in `tasks.yaml`.
4.  Call the API with `"crew_type": "dynamic"`.

### Step 2: Custom Logic (Developer)
1.  Add a new `.py` file into `apps/agents/crewai/crews/`.
2.  Decorate your class with `@register_crew("your_name")`.
3.  The API registers it automatically upon start.

---

## 📂 Project Structure
*   **`config/`**: Django system settings.
*   **`apps/api/`**: API endpoints (Django Ninja).
*   **`apps/agents/crewai/`**: The core multi-agent engine.
*   **`apps/agents/crewai/config/`**: YAML agent/task definitions.
*   **`legacy/`**: Your original unstructured code (for reference).
