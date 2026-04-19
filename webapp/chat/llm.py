import os
import requests

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_URL_LOCAL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"
EMBED_MODEL = "nomic-embed-text" # Added the embedding model you pulled earlier

def _get_ollama_url():
    """Try Docker URL first, fall back to localhost for local testing."""
    try:
        requests.get("http://ollama:11434", timeout=2)
        return OLLAMA_URL
    except:
        return OLLAMA_URL_LOCAL

def get_embedding(text):
    """Generate a vector embedding for the search query."""
    url = _get_ollama_url().replace("/api/generate", "/api/embeddings")
    try:
        response = requests.post(
            url,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("embedding")
    except Exception as e:
        print(f"Embedding Error: {e}")
        return None

def ask_ollama(question, context=""):
    """
    Send a question to Ollama with optional context from scraped ACU data.
    Updated for Week 9: Handles empty context and Turkish language requests.
    """
    # Edge Case: The database semantic search found no relevant pages
    if not context:
        return "I couldn't find any specific information about that in the Acıbadem University database. Could you try rephrasing your question?"

    # Fine-tuned Prompt: Strict context boundaries and multi-language support
    prompt = f"""You are the official AI assistant for Acıbadem University (ACU).
You must answer the user's query strictly using ONLY the provided Context Information below.
If the context does not contain the answer, politely say: "I don't have that information available based on the current data. Please visit acibadem.edu.tr for more details."
If the user asks a question in Turkish, you MUST reply entirely in Turkish, but still base your facts strictly on the provided context.
Do not make up any information. Be concise, professional, and helpful.

Context Information:
{context}

Question: {question}

Answer:"""

    try:
        url = _get_ollama_url()
        response = requests.post(
            url,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Sorry, I could not generate an answer.")

    except requests.exceptions.ConnectionError:
        return "AI service is currently unavailable. Please try again later."
    except requests.exceptions.Timeout:
        return "The AI took too long to respond. Please try again."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_context_from_db(question):
    """
    Search the database for pages relevant to the question.
    Updated to use pgvector semantic search instead of basic keyword matching.
    """
    try:
        from .models import Page

        import importlib
        try:
            pgvector_django = importlib.import_module("pgvector.django")
            L2Distance = pgvector_django.L2Distance
        except (ImportError, ModuleNotFoundError):
            print("pgvector package is not installed; semantic search unavailable.")
            return ""

        # 1. Convert the user's question into a 768-dimensional vector
        query_embedding = get_embedding(question)
        if not query_embedding:
            return ""

        # 2. Perform a semantic distance search in PostgreSQL
        # This calculates the cosine distance between the question and the database pages
        pages = Page.objects.exclude(embedding__isnull=True).order_by(
            L2Distance('embedding', query_embedding)
        )[:3]

        if not pages:
            return ""

        context_parts = []
        for page in pages:
            # Safely get title if it exists, otherwise fall back to URL
            page_identifier = getattr(page, 'title', getattr(page, 'url', 'ACU Page'))
            context_parts.append(f"--- {page_identifier} ---\n{page.content[:1000]}")

        return "\n\n".join(context_parts)

    except Exception as e:
        print(f"Database Search Error: {e}")
        return ""

def answer_question(question):
    """
    Main function — get context from DB and ask Ollama.
    This is what views.py will call.
    """
    context = get_context_from_db(question)
    return ask_ollama(question, context)

def check_ollama_connection():
    """Returns True if Ollama is reachable, False otherwise."""
    try:
        requests.get(_get_ollama_url().replace("/api/generate", ""), timeout=5)
        return True
    except:
        return False

def list_available_models():
    """Returns a list of models available in Ollama."""
    try:
        url = _get_ollama_url().replace("/api/generate", "/api/tags")
        response = requests.get(url, timeout=5)
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except:
        return [] 