# 🎓 ACU AI Chatbot

A Django-based AI chatbot that answers questions about Acıbadem University using a RAG (Retrieval-Augmented Generation) pipeline with pgvector semantic search and a locally running LLM (phi3 via Ollama), containerized with Docker & Docker Compose.

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

> ⚠️ On first run, pull the AI models:
> ```bash
> docker compose exec ollama ollama pull phi3
> docker compose exec ollama ollama pull nomic-embed-text
> ```

> ⚠️ Then scrape the data and generate embeddings:
> ```bash
> docker compose exec web python manage.py scrape
> docker compose exec web python manage.py generate_embeddings
> ```

> ⚠️ Warm up phi3 before testing (takes ~30 seconds):
> ```bash
> docker compose exec ollama ollama run phi3 "hello"
> ```

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                         │
│  ┌──────────┐    ┌─────────────────┐    ┌───────────┐  │
│  │  Django  │───▶│   PostgreSQL 15  │    │  Ollama   │  │
│  │  :8000   │    │  + pgvector ext  │    │  :11434   │  │
│  └──────────┘    └─────────────────┘    └───────────┘  │
│       │                  ▲                    ▲          │
│       └──────────────────┼────────────────────┘         │
│              RAG Pipeline (semantic search + LLM)        │
└─────────────────────────────────────────────────────────┘
**Containers:**
- `web` — Django 4.2 application (chat interface + REST API + scraper)
- `db` — PostgreSQL 15 with pgvector extension (stores scraped pages + embeddings + chat history)
- `ollama` — Local LLM service running phi3 (chat) and nomic-embed-text (embeddings)

**RAG Pipeline:**
1. User types a question in the chat interface
2. Question is embedded using `nomic-embed-text`
3. pgvector finds the most semantically similar pages using CosineDistance
4. Matched content + question are sent to phi3 as a structured prompt
5. phi3 generates a factual answer based only on the provided context
6. Answer is displayed to the user and saved to chat history

---

## 📁 Project Structure

acibadem-chatbot/
├── docker-compose.yml              # Orchestrates all containers
├── README.md
└── webapp/
├── Dockerfile
├── requirements.txt
├── manage.py
├── config/                     # Django settings, urls, wsgi
├── chat/                       # Main app
│   ├── models.py               # Page (with embedding), ChatMessage models
│   ├── views.py                # chat_page, api_chat, health_check
│   ├── management/
│   │   └── commands/
│   │       └── generate_embeddings.py  # Generate pgvector embeddings
│   ├── migrations/             # DB migrations including pgvector
│   ├── api_urls.py
│   └── urls.py
├── scraper/                    # Data collection
│   ├── scraper.py              # BeautifulSoup + Selenium scraper
│   ├── tests.py                # 15 scraper tests
│   └── management/
│       └── commands/
│           └── scrape.py       # Django management command
└── templates/
└── chat/
└── chat.html           # Chat UI
---

## 🗄️ Data Pipeline

### Sources
- **ACU Website** — All 4,880 sitemap URLs (Turkish + English pages)
- **Bologna/OBS** — 48 pages from obs.acibadem.edu.tr ECTS catalog (programs, departments, student life)

### Processing
1. **Scrape** — BeautifulSoup for static pages, Selenium for JavaScript-rendered pages
2. **Clean** — Remove pages under 300 chars (boilerplate, old events)
3. **Embed** — Generate 768-dimensional vectors with `nomic-embed-text`
4. **Store** — Save to PostgreSQL with pgvector extension

### Statistics
| Metric | Value |
|--------|-------|
| Total pages scraped | 3,245 |
| Turkish pages | ~2,750 |
| English pages | ~457 |
| Bologna/OBS pages | 38 |
| Average content length | 2,078 chars |
| Embedding dimensions | 768 |
| Scrape schedule | Every Sunday (django-crontab) |

---

## 🔍 Search Strategy

The chatbot uses a hybrid routing strategy:

| Question Type | Strategy | Example |
|--------------|----------|---------|
| Transport | Hardcoded URL | "Which buses go to ACU?" |
| Student Life | Hardcoded URLs | "What clubs does ACU have?" |
| Programs/Faculty | Hardcoded URLs | "What programs does ACU offer?" |
| General | pgvector semantic search | "Tell me about ACU" |

---

## 🔌 API

### `POST /api/chat/`

**Request:**
```json
{ "message": "What programs does ACU offer?" }
```

**Response:**
```json
{ "answer": "ACU offers programs in Engineering, Health Sciences, Medicine..." }
```

### `GET /health/`
Returns `{"status": "ok", "message": "ACU Chatbot is running!"}`.

---

## 📅 What Was Built Each Week

### Weeks 1-5 — Foundation
- Docker Compose setup with Django, PostgreSQL, Ollama
- Basic chat interface and REST API
- Initial scraper with BeautifulSoup
- phi3 integration and prompt engineering

### Week 6 — Sitemap Scraper (Safiye)
- Sitemap-based scraping of 4,880 URLs with HEAD request validation
- 141 English pages scraped and stored
- Automatic weekly scraping with django-crontab
- 6 passing scraper tests

### Week 7 — pgvector + Bologna Scraping (Betül + Safiye)
- pgvector extension added to PostgreSQL
- VectorField added to Page model (768 dimensions)
- Bologna/OBS pages scraped using Selenium to extract JavaScript onclick URLs
- 38 Bologna pages added (programs, student life, campus info)

### Week 8 — Data Enrichment (Safiye)
- Expanded scraper to include all Turkish pages (4,880 → 4,456 pages saved)
- Cleaned 1,211 poor quality pages → 3,245 clean pages
- Generated nomic-embed-text embeddings for all 3,245 pages
- Implemented hybrid search routing in views.py

### Week 9 — Search Quality + Tests (Safiye + Betül)
- Keyword routing for transport, student life, and program questions
- Semantic search with pgvector CosineDistance for general questions
- Content limit tuning to prevent phi3 timeouts
- 15 passing scraper tests (up from 6)

---

## 🧪 Demo Questions

| Question | Answer |
|----------|--------|
| What programs does ACU offer? | Lists all faculties and departments |
| Who is the head of Computer Engineering? | Prof. Dr. Ahmet Bulut |
| Which buses can I take to ACU? | 19K, 19Y, 19V, 19S, 19T, 14A, 11T, 320A |
| Where is ACU located? | Kayışdağı Cad. No:32, Ataşehir/Istanbul |
| What student clubs does ACU have? | Full list of 30+ clubs |
| Is there accommodation at ACU? | Yes, Kerem Aydınlar Dormitories |
| What sports facilities does ACU have? | Pool, gym, courts, studios |
| What doctorate programs are available? | Full PhD program list |
| Tell me about Acibadem University | Detailed overview |

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

# Warm up phi3 before testing
docker compose exec ollama ollama run phi3 "hello"

# Run scraper
docker compose exec web python manage.py scrape

# Generate embeddings
docker compose exec web python manage.py generate_embeddings

# Run tests
docker compose exec web python manage.py test scraper

# Check DB stats
docker compose exec web python manage.py shell -c "
from chat.models import Page
print('Pages:', Page.objects.count())
print('Embedded:', Page.objects.filter(embedding__isnull=False).count())
"

# View logs
docker compose logs -f web

# Access Django shell
docker compose exec web python manage.py shell
```

---

## 👥 Team

| Name | Role |
|------|------|
| Bartu | DevOps — Docker, pgvector setup, cloud deployment |
| Betül | Backend — API, semantic search, caching |
| Safiye | Data — Scraping, cleaning, embeddings |
| Mina | AI — Embeddings, prompt engineering |

---

## 📖 Resources

- [Docker Compose Docs](https://docs.docker.com/compose)
- [Django Documentation](https://docs.djangoproject.com)
- [pgvector](https://github.com/pgvector/pgvector)
- [Ollama](https://ollama.ai/docs)
- [nomic-embed-text](https://ollama.com/library/nomic-embed-text)
- [Acıbadem University](https://www.acibadem.edu.tr)