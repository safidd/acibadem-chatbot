import time
import schedule
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Runs the ACU web scraper automatically every Sunday'

    def job(self):
        self.stdout.write(self.style.SUCCESS('\nStarting scheduled Sunday scraper job...'))
        try:
            # This calls the team's existing scraper command (assuming it's named 'scrape')
            call_command('scrape') 
            self.stdout.write(self.style.SUCCESS('Scraping finished successfully!\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Scraper failed: {e}\n'))

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Background Scheduler started. Waiting for Sunday at 00:00...'))
        
        # Schedule the job for every Sunday at midnight
        schedule.every().sunday.at("00:00").do(self.job)
        
        # NOTE FOR TESTING: Uncomment the line below to run it every 1 minute instead
        # schedule.every(1).minutes.do(self.job)

        # Infinite loop that checks the clock every 60 seconds
        while True:
            schedule.run_pending()
            time.sleep(60)
