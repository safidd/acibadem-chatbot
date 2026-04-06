# 🎓 ACU AI Chatbot

A Django-based AI chatbot that answers questions about Acıbadem University using a RAG pipeline with pgvector semantic search and a locally running LLM (phi3 via Ollama), containerized with Docker & Docker Compose.

**Course:** CSE 322 – Cloud Computing | Acıbadem University | Spring 2026
**GitHub:** https://github.com/safidd/acibadem-chatbot

---

## 🚀 Quick Start
```bash
git clone https://github.com/safidd/acibadem-chatbot
cd acibadem-chatbot
docker compose up -d
```

Open your browser at **http://localhost:8000**

On first run, pull the AI models and scrape data:
```bash
docker compose exec ollama ollama pull phi3
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec web python manage.py scrape
docker compose exec web python manage.py generate_embeddings
docker compose exec ollama ollama run phi3 "hello"
```

---

## 🏗️ System Architecture

| Container | Technology | Purpose |
|-----------|-----------|---------|
| web | Django 4.2 | Chat interface + REST API + scraper |
| db | PostgreSQL 15 + pgvector | Pages, embeddings, chat history |
| ollama | phi3 + nomic-embed-text | LLM chat and embedding generation |

**RAG Pipeline:**
1. User types a question
2. Question is embedded using nomic-embed-text
3. pgvector finds the most similar pages using CosineDistance
4. Matched content + question sent to phi3 as a structured prompt
5. phi3 generates a factual answer based only on the provided context
6. Answer is displayed and saved to chat history

---

## 🗄️ Data Pipeline

| Metric | Value |
|--------|-------|
| Total pages | 3,245 |
| Turkish pages | ~2,750 |
| English pages | ~457 |
| Bologna/OBS pages | 38 |
| Average content length | 2,078 chars |
| Embedding dimensions | 768 |
| Scrape schedule | Every Sunday |

**Sources:**
- ACU Website — All 4,880 sitemap URLs (Turkish + English)
- Bologna/OBS — 48 pages from obs.acibadem.edu.tr ECTS catalog

---

## 🔍 Search Strategy

| Question Type | Strategy | Example |
|--------------|----------|---------|
| Transport | Keyword routing | "Which buses go to ACU?" |
| Student Life | Keyword routing | "What clubs does ACU have?" |
| Programs/Faculty | Keyword routing | "What programs does ACU offer?" |
| General | pgvector semantic search | "Tell me about ACU" |

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

---

## 📅 What Was Built Each Week

**Weeks 1–5 — Foundation**
Docker Compose setup, basic chat interface, REST API, initial scraper, phi3 integration.

**Week 6 — Sitemap Scraper**
Sitemap-based scraping of 4,880 URLs, 141 English pages stored, weekly auto-scraping with django-crontab, 6 passing tests.

**Week 7 — pgvector + Bologna Scraping**
pgvector added to PostgreSQL, VectorField on Page model (768 dims), 38 Bologna/OBS pages scraped with Selenium.

**Week 8 — Data Enrichment**
Expanded to all Turkish pages (141 → 4,456), cleaned 1,211 poor quality pages → 3,245 clean pages, embeddings generated.

**Week 9 — Search Quality + Tests**
Hybrid keyword routing + semantic search, content limit tuning, 15 passing scraper tests.

---

## 📚 Useful Commands
```bash
docker compose up -d
docker compose down
docker compose exec ollama ollama run phi3 "hello"
docker compose exec web python manage.py scrape
docker compose exec web python manage.py generate_embeddings
docker compose exec web python manage.py test scraper
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | db | PostgreSQL host |
| DB_NAME | acudb | Database name |
| DB_USER | acuuser | Database user |
| DB_PASSWORD | acupass | Database password |
| OLLAMA_URL | http://ollama:11434 | Ollama service URL |
| DJANGO_SECRET_KEY | change-this | Django secret key |

---

## 👥 Team

| Name | Role | Responsibility |
|------|------|---------------|
| Bartu | DevOps | Docker, pgvector, cloud deployment |
| Betül | Backend | API, semantic search, caching |
| Safiye | Data | Scraping, cleaning, embeddings |
| Mina | AI | Embeddings, prompt engineering |

---

## 📖 Resources

- [Docker Compose](https://docs.docker.com/compose)
- [Django](https://docs.djangoproject.com)
- [pgvector](https://github.com/pgvector/pgvector)
- [Ollama](https://ollama.ai/docs)
- [Acıbadem University](https://www.acibadem.edu.tr)
