from django.core.management.base import BaseCommand
from chat.models import Page
import requests

class Command(BaseCommand):
    help = 'Generates vector embeddings for all scraped pages using Ollama'

    def handle(self, *args, **kwargs):
        # Find all pages that don't have an embedding yet
        pages = Page.objects.filter(embedding__isnull=True)
        
        if not pages.exists():
            self.stdout.write(self.style.SUCCESS("All pages already have embeddings!"))
            return

        self.stdout.write(f"Found {pages.count()} pages needing embeddings. Starting generation...")

        for page in pages:
            try:
                # Send the page content to Ollama
                response = requests.post(
                    "http://ollama:11434/api/embeddings",
                    json={"model": "phi3", "prompt": page.content},
                    timeout=60  # Give it a minute to process large pages
                )
                
                if response.status_code == 200:
                    embedding = response.json().get('embedding')
                    if embedding:
                        # Save the vector to the database
                        page.embedding = embedding
                        page.save()
                        self.stdout.write(self.style.SUCCESS(f"Successfully embedded: {page.title}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"No embedding returned for: {page.title}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Ollama error {response.status_code} for: {page.title}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to embed {page.title}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Embedding generation complete!"))