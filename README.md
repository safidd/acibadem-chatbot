# 🎓 ACU AI Chatbot

A Django-based AI chatbot that answers questions about Acıbadem University using a locally running LLM (phi3 via Ollama), containerized with Docker & Docker Compose.

**Course:** CSE 322 – Cloud Computing | Acıbadem University | Spring 2026  
**GitHub:** https://github.com/safidd/acibadem-chatbot

---

## 🚀 Quick Start

```bash
git clone https://github.com/safidd/acibadem-chatbot
cd acibadem-chatbot
docker compose up -d
```

Then open your browser and go to: **http://localhost:8000**

> ⚠️ On first run, pull the AI model into the Ollama container:
> ```bash
> docker exec acibadem-chatbot-main-ollama-1 ollama pull phi3
> ```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│                Docker Compose                    │
│                                                 │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐  │
│  │  Django  │───▶│PostgreSQL│    │  Ollama   │  │
│  │  :8000   │    │  :5432   │    │  :11434   │  │
│  └──────────┘    └──────────┘    └───────────┘  │
│       │                               ▲          │
│       └───────────────────────────────┘          │
│              HTTP API (prompts)                  │
└─────────────────────────────────────────────────┘
```

**Containers:**
- `web` — Django 4.x application (chat interface + REST API)
- `db` — PostgreSQL 15 (stores scraped pages + chat history)
- `ollama` — Local LLM service running phi3 model

**How it works:**
1. User types a question in the chat interface
2. Django searches the database for relevant ACU content
3. The matched content + question are sent to Ollama as a prompt
4. Ollama generates an answer which is displayed to the user and saved to chat history

---

## 📁 Project Structure

```
acibadem-chatbot/
├── docker-compose.yml          # Orchestrates all containers
├── README.md
├── webapp/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/                 # Django settings, urls, wsgi
│   ├── chat/                   # Main app
│   │   ├── models.py           # Page, ChatMessage models
│   │   ├── views.py            # chat_page, api_chat, health_check
│   │   ├── llm.py              # Ollama integration & prompt engineering
│   │   ├── api_urls.py         # /api/chat/ endpoint
│   │   ├── urls.py
│   │   └── sample_qa.md        # 10 sample Q&As for report
│   ├── scraper/                # Data collection scripts
│   └── templates/
│       └── chat/
│           └── chat.html       # Chat UI
└── docs/
    └── report.pdf
```

---

## 🔌 API

### `POST /api/chat/`

Send a question and receive an AI-generated answer.

**Request:**
```json
{
  "question": "What faculties does Acibadem University have?"
}
```

**Response:**
```json
{
  "question": "What faculties does Acibadem University have?",
  "answer": "Acibadem University has the following faculties: Medicine, Dentistry, Pharmacy, Engineering and Natural Sciences, Health Sciences, and Economics and Administrative Sciences.",
  "id": 1
}
```

### `GET /health/`

Health check endpoint — returns `{"status": "ok"}`.

---

## 🤖 AI Integration

- **Model:** phi3 (Microsoft) via Ollama
- **Serving:** Ollama Docker container on port 11434
- **Strategy:** Retrieval-Augmented Generation (RAG)
  - Keywords extracted from the user's question
  - Top 3 matching pages retrieved from PostgreSQL
  - Context injected into a structured system prompt
  - phi3 generates answer based only on provided context

**Key prompt rules enforced:**
- Answer ONLY using provided context — no training knowledge
- Copy contact details exactly with no modifications
- Redirect to acibadem.edu.tr if information is unavailable
- Maximum 3 sentences per answer

---

## 📅 What Was Built Each Week

### Week 1 — Setup & Foundation
- Repository created with full project structure
- Docker Compose skeleton with Django and PostgreSQL working
- Ollama installed and phi3 model tested locally
- All team members onboarded to the repo

### Week 2 — Add AI Container
- Ollama service added to docker-compose.yml
- `llm.py` created with Ollama HTTP integration and prompt engineering
- `api_chat` view and `/api/chat/` endpoint added
- Error handling added for LLM unavailability and timeouts

### Week 3 — Scrape University Data
- Web scraper built using requests + BeautifulSoup
- ACU pages scraped from acibadem.edu.tr and stored in the `Page` model
- Django management command `python manage.py scrape` added
- AI prompts tested with real scraped content

### Week 4 — Connect Everything
- `get_context_from_db()` built to search database by keyword
- `answer_question()` function built as the main AI entry point
- Full pipeline tested: user question → DB search → context injection → Ollama → answer
- Chat frontend connected to the REST API
- Chat history saved to PostgreSQL on every question

### Week 5 — Demo Preparation
- Keyword stopword filtering added to improve context retrieval
- Prompt rules strengthened to eliminate hallucinations on contact details
- 10 sample questions tested and documented
- Admin panel verified to show scraped pages and chat history
- Full Docker flow tested from zero

---

## 🧪 Sample Q&A Results

| # | Question | Result |
|---|----------|--------|
| 1 | What faculties does Acibadem University have? | ✅ Accurate |
| 2 | Where is Acibadem University located? | ✅ Accurate |
| 3 | What programs does the Faculty of Engineering offer? | ✅ Accurate |
| 4 | How can I apply to Acibadem University? | ✅ Accurate |
| 5 | What are the admission requirements for international students? | ✅ Accurate |
| 6 | Does Acibadem University have exchange programs? | ✅ Accurate |
| 7 | What is the language of instruction? | ✅ Accurate |
| 8 | How many campuses does Acibadem University have? | ✅ Accurate |
| 9 | What research centers does Acibadem University have? | ⚠️ Limited data |
| 10 | How can I contact the student affairs office? | ✅ Accurate |

> Full answers available in `webapp/chat/sample_qa.md`

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `db` | PostgreSQL host |
| `DB_NAME` | `acudb` | Database name |
| `DB_USER` | `acuuser` | Database user |
| `DB_PASSWORD` | `acupass` | Database password |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama service URL |
| `DJANGO_SECRET_KEY` | change-this | Django secret key |
| `DEBUG` | `True` | Debug mode |

---

## 📚 Useful Commands

```bash
# Start all containers
docker compose up -d

# Stop all containers
docker compose down

# View logs
docker compose logs -f web

# Run scraper
docker exec acibadem-chatbot-main-web-1 python manage.py scrape

# Access Django shell
docker exec acibadem-chatbot-main-web-1 python manage.py shell

# Check pages in DB
docker exec acibadem-chatbot-main-web-1 python manage.py shell -c "from chat.models import Page; print(Page.objects.count(), 'pages')"

# Pull AI model (first time only)
docker exec acibadem-chatbot-main-ollama-1 ollama pull phi3
```

---

## 👥 Team

Bartu · Betul · Safiye · Mina

---

## 📖 Resources

- [Docker Compose Docs](https://docs.docker.com/compose)
- [Django Documentation](https://docs.djangoproject.com)
- [Ollama](https://ollama.ai/docs)
- [Acıbadem University](https://www.acibadem.edu.tr)
