from django.core.management.base import BaseCommand
from chat.models import Page
import requests

class Command(BaseCommand):
    help = 'Generates vector embeddings for all scraped pages using Ollama'

    def handle(self, *args, **kwargs):
        pages = Page.objects.filter(embedding__isnull=True)
        
        if not pages.exists():
            self.stdout.write(self.style.SUCCESS("All pages already have embeddings!"))
            return

        self.stdout.write(f"Found {pages.count()} pages needing embeddings. Starting generation...")

        success = 0
        failed = 0
        for page in pages:
            try:
                # Only send first 500 chars — enough for embedding, avoids timeouts
                text = f"{page.title}. {page.content[:500]}"
                
                response = requests.post(
                    "http://ollama:11434/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": text},
                    timeout=120
                )
                
                if response.status_code == 200:
                    embedding = response.json().get('embedding')
                    if embedding:
                        page.embedding = embedding
                        page.save()
                        self.stdout.write(f"✓ {page.title[:60]}")
                        success += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"✗ No embedding: {page.title[:60]}"))
                        failed += 1
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Error {response.status_code}: {page.title[:60]}"))
                    failed += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Failed {page.title[:60]}: {str(e)}"))
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"Done! Success: {success} | Failed: {failed}"))