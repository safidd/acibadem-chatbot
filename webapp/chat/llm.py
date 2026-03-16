import requests

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_URL_LOCAL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"


def _get_ollama_url():
    """Try Docker URL first, fall back to localhost for local testing."""
    try:
        requests.get("http://ollama:11434", timeout=2)
        return OLLAMA_URL
    except:
        return OLLAMA_URL_LOCAL


def ask_ollama(question, context=""):
    """
    Send a question to Ollama with optional context from scraped ACU data.
    Returns the AI's answer as a string.
    """
    if context:
        prompt = f"""You are a helpful assistant for Acibadem University (ACU).
Use ONLY the following information from the ACU website to answer the question.
If the answer is not in the context, say: "I don't have that information available. Please visit acibadem.edu.tr for more details."
Do not make up any information. Be concise and helpful.

Context:
{context}

Question: {question}

Answer:"""
    else:
        prompt = f"""You are a helpful assistant for Acibadem University (ACU).
Answer the following question about Acibadem University.
If you are not sure about something, say so and suggest visiting acibadem.edu.tr.
Be concise and helpful.

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
    Returns combined text from the top matching pages.
    """
    try:
        from .models import Page
        from django.db.models import Q

        # Split question into keywords and search
        keywords = [w for w in question.lower().split() if len(w) > 3]
        
        query = Q()
        for keyword in keywords:
            query |= Q(content__icontains=keyword) | Q(title__icontains=keyword)

        pages = Page.objects.filter(query).distinct()[:3]

        if not pages:
            return ""

        context_parts = []
        for page in pages:
            context_parts.append(f"--- {page.title} ---\n{page.content[:1000]}")

        return "\n\n".join(context_parts)

    except Exception as e:
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
