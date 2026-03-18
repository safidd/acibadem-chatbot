from django.core.management.base import BaseCommand
from scraper.scraper import run_scraper

class Command(BaseCommand):
    help = 'Scrape ACU website and store content in database'

    def handle(self, *args, **options):
        self.stdout.write('Starting ACU website scraper...')
        run_scraper()
        self.stdout.write(self.style.SUCCESS('Scraping finished!'))