# Email Triage POC

An AI-powered email triaging and auto-ticketing pipeline, running entirely on a local machine.

---

## Prerequisites

Install these before starting:

1. Python 3.11+ from https://python.org (check Add Python to PATH during install)
2. Node.js 20.19+ from https://nodejs.org (download LTS version)
3. Git Bash from https://git-scm.com (Windows users only)
4. Ollama from https://ollama.com/download (install with default settings)

---

## Step by Step Setup

### Step 1 - Open terminal and go to project folder

    cd /d/Projects/email-triage-poc/email-triage-poc

### Step 2 - Create and activate virtual environment

    python -m venv .venv
    source .venv/bin/activate

You should see (.venv) at the start of your prompt.

### Step 3 - Install Python dependencies

    pip install -r requirements.txt
    pip install sqlalchemy watchdog requests pyyaml chromadb sentence-transformers rapidfuzz reportlab pillow faker uvicorn fastapi pydantic-settings

### Step 4 - Pull AI models (large download, ~5GB each)

    ollama pull llama3.1
    ollama pull llava

### Step 5 - Set up environment file

    cp .env.example .env

No changes needed. Default settings work out of the box.

### Step 6 - Create the database

    python backend/app/create_db.py

You should see: Database created successfully

### Step 7 - Generate sample emails

    python sample_data/generate.py

You should see: Generated 45 emails in sample_data/emails

### Step 8 - Install frontend dependencies

    cd frontend
    npm install
    cd ..

---

## Running the System

You need 6 terminals. In every new terminal first run:

    cd /d/Projects/email-triage-poc/email-triage-poc
    source .venv/bin/activate

Terminal 1 - ITSM-A Mock (port 8001)

    python -m uvicorn mock_services.itsm_a.main:app --port 8001 --reload

Terminal 2 - ITSM-B Mock (port 8002)

    python -m uvicorn mock_services.itsm_b.main:app --port 8002 --reload

Terminal 3 - Directory Mock (port 8003)

    python -m uvicorn mock_services.directory.main:app --port 8003 --reload

Terminal 4 - Backend API (port 8000)

    python -m uvicorn backend.app.main:app --port 8000 --reload

Terminal 5 - Pipeline Runner

    python backend/app/pipeline/runner.py

Wait until you see: Watching all 4 inboxes for new emails

Terminal 6 - Frontend

    cd frontend
    npm run dev

Wait until you see: Local: http://localhost:5173

Then open http://localhost:5173 in your browser.

---

## Demo Walkthrough

1. Open http://localhost:5173
2. Click Mail Simulator in the nav
3. Fill in From, To, Subject, Body and click Send Email
4. Click Monitor - watch the email process through all 8 stages (about 60 seconds)
5. Click Tickets - see tickets created in both ITSM-A and ITSM-B with AI fields
6. Send the same email again - it will be flagged as a duplicate
7. Click Review Queue - confirm or reject the duplicate
8. Click Config - view all configuration files and thresholds

---

## Switching LLM Provider

Change one line in .env:

    LLM_PROVIDER=hosted

No code changes required anywhere in the pipeline.

---

## Project Structure

    email-triage-poc/
    backend/app/
        pipeline/     8 pipeline stages (stage1 through stage8)
        interfaces/   abstraction layer
        adapters/     Ollama, ChromaDB, mock clients
        parsing/      email, PDF, image parsers
    mock_services/
        itsm_a/       ServiceNow-style API on port 8001
        itsm_b/       Jira-style API on port 8002
        directory/    User directory API on port 8003
    mailboxes/        watched inbox folders
    config/           YAML and CSV configuration files
    sample_data/      45 synthetic emails
    frontend/         React dashboard
