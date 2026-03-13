import requests
from bs4 import BeautifulSoup
import time

URLS = [
    "https://www.acibadem.edu.tr/universite",
    "https://www.acibadem.edu.tr/aday/ogrenci",
    "https://www.acibadem.edu.tr/akademik/lisans",
    "https://www.acibadem.edu.tr/akademik/onlisans",
    "https://www.acibadem.edu.tr/akademik/lisansustu",
    "https://www.acibadem.edu.tr/ogrenci/ogrenci",
    "https://www.acibadem.edu.tr/arastirma",
    "https://www.acibadem.edu.tr/surdurulebilir-kampus",
    "https://www.acibadem.edu.tr/kayit/iletisim/ulasim",
]

def get_page_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} — status {response.status_code}")
            return None, None
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.text.strip() if soup.title else url
        for tag in soup(['nav', 'footer', 'script', 'style', 'header']):
            tag.decompose()
        content = soup.get_text(separator=' ', strip=True)
        content = ' '.join(content.split())
        return title, content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

def run_scraper():
    from chat.models import Page
    print(f"Starting scraper — {len(URLS)} pages to scrape")
    print("=" * 50)
    success = 0
    failed = 0
    for i, url in enumerate(URLS, 1):
        print(f"[{i}/{len(URLS)}] Scraping: {url}")
        title, content = get_page_content(url)
        if title and content and len(content) > 100:
            page, created = Page.objects.update_or_create(
                url=url,
                defaults={
                    'title': title,
                    'content': content,
                }
            )
            if created:
                print(f"  ✓ Saved: {title[:50]}")
            else:
                print(f"  ✓ Updated: {title[:50]}")
            success += 1
        else:
            print(f"  ✗ Failed or empty content")
            failed += 1
        if i < len(URLS):
            print(f"  Waiting 2 seconds...")
            time.sleep(2)
    print("=" * 50)
    print(f"Done! Saved: {success} | Failed: {failed}")