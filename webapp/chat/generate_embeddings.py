import requests
from django.db.models import Q

OLLAMA_URL = "http://ollama:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text):
    """
    Generate an embedding vector for a given text using nomic-embed-text.
    Returns a list of floats or None if it fails.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding")
        return None
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def generate_embeddings_for_all_pages(batch_size=10):
    """
    Generate and store embeddings for all pages that don't have one yet.
    Processes in batches to avoid memory issues.
    """
    from .models import Page

    pages_without_embeddings = Page.objects.filter(embedding__isnull=True)
    total = pages_without_embeddings.count()

    if total == 0:
        print("All pages already have embeddings!")
        return

    print(f"Generating embeddings for {total} pages...")

    success = 0
    failed = 0

    for i, page in enumerate(pages_without_embeddings, 1):
        # Combine title and first 500 chars of content for embedding
        text = f"{page.title}\n{page.content[:500]}"
        embedding = get_embedding(text)

        if embedding:
            page.embedding = embedding
            page.save(update_fields=["embedding"])
            success += 1
            print(f"[{i}/{total}] ✓ {page.title[:60]}")
        else:
            failed += 1
            print(f"[{i}/{total}] ✗ Failed: {page.title[:60]}")

    print(f"\nDone! Success: {success}, Failed: {failed}")


def generate_embedding_for_question(question):
    """
    Generate an embedding for a user question.
    Used in views.py for semantic search.
    """
    return get_embedding(question)
