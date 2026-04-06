from django.core.management.base import BaseCommand
from chat.generate_embeddings import generate_embeddings_for_all_pages

class Command(BaseCommand):
    help = 'Generate embeddings for all pages without embeddings'

    def handle(self, *args, **options):
        self.stdout.write('Starting embedding generation...')
        generate_embeddings_for_all_pages()
        self.stdout.write(self.style.SUCCESS('Embedding generation complete!'))
