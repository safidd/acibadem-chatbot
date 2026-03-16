import requests
import json

OLLAMA_URL = "http://ollama:11434/api/generate"  # uses Docker service name
MODEL_NAME = "phi3"

def ask_ollama(question, context=""):
    """
    Send a question to Ollama with optional context from scraped ACU data.
    Returns the AI's answer as a string.
    """

    if context:
        prompt = f"""You are a helpful assistant for Acibadem University (ACU).
Use the following information from the ACU website to answer the question.
Only answer based on the provided context. If the answer is not in the context, say you don't have that information.

Context:
{context}

Question: {question}

Answer:"""
    else:
        prompt = f"""You are a helpful assistant for Acibadem University (ACU).
Answer the following question about Acibadem University as best you can.

Question: {question}

Answer:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
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

def check_ollama_connection():
    """
    Returns True if Ollama is reachable, False otherwise.
    """
    try:
        response = requests.get("http://ollama:11434", timeout=5)
        return True
    except:
        return False


def list_available_models():
    """
    Returns a list of models available in Ollama.
    Useful for debugging and checking what models are pulled.
    """
    try:
        response = requests.get("http://ollama:11434/api/tags", timeout=5)
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except:
        return []
