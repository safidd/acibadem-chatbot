import requests
from bs4 import BeautifulSoup
import time

SITEMAP_URLS = [
    "https://www.acibadem.edu.tr/sitemap.xml?page=1",
    "https://www.acibadem.edu.tr/sitemap.xml?page=2",
]

def to_english_url(url):
    """Convert Turkish URL to potential English URL"""
    return url.replace(
        'https://www.acibadem.edu.tr/',
        'https://www.acibadem.edu.tr/en/'
    )

def english_url_exists(url):
    """Quick HEAD request — no page download, just checks if URL works"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def get_english_urls_from_sitemap():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        all_turkish_urls = []

        for sitemap_url in SITEMAP_URLS:
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            urls = [loc.text.strip() for loc in soup.find_all('loc')]
            all_turkish_urls.extend(urls)
            print(f"Found {len(urls)} URLs in {sitemap_url}")

        print(f"Total URLs: {len(all_turkish_urls)} — checking English versions...")

        english_urls = []
        for i, url in enumerate(all_turkish_urls, 1):
            en_url = to_english_url(url)
            if english_url_exists(en_url):
                english_urls.append(en_url)
            if i % 50 == 0:
                print(f"  Checked {i}/{len(all_turkish_urls)} — found {len(english_urls)} English pages so far...")
            time.sleep(0.3)

        print(f"Total valid English pages found: {len(english_urls)}")
        return english_urls

    except Exception as e:
        print(f"Error: {e}")
        return []

def get_page_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
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
    urls = get_english_urls_from_sitemap()
    if not urls:
        print("No English URLs found!")
        return
    print(f"Starting scraper — {len(urls)} English pages to scrape")
    print("=" * 50)
    success = 0
    failed = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping: {url}")
        title, content = get_page_content(url)
        if title and content and len(content) > 100:
            page, created = Page.objects.update_or_create(
                url=url,
                defaults={'title': title, 'content': content}
            )
            if created:
                print(f"  ✓ Saved: {title[:50]}")
            else:
                print(f"  ✓ Updated: {title[:50]}")
            success += 1
        else:
            print(f"  ✗ Failed or empty")
            failed += 1
        time.sleep(0.5)
    print("=" * 50)
    print(f"Done! Saved: {success} | Failed: {failed}")