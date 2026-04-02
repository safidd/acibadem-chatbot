import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

SITEMAP_URLS = [
    "https://www.acibadem.edu.tr/sitemap.xml?page=1",
    "https://www.acibadem.edu.tr/sitemap.xml?page=2",
]

BOLOGNA_URLS = [
    # General info pages
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=100&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=101&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=102&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=103&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=104&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=300&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=301&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=302&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=303&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=304&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=305&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=309&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=311&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=400&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=401&lang=en',
    # Unit selection pages
    'https://obs.acibadem.edu.tr/oibs/bologna/unitSelection.aspx?type=myo&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/unitSelection.aspx?type=lis&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/unitSelection.aspx?type=yls&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/unitSelection.aspx?type=dok&lang=en',
    # Department pages
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=11&curSunit=50',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=11&curSunit=6230',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=11&curSunit=48',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=07&curSunit=23',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=04&curSunit=6166',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=04&curSunit=16',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=14&curSunit=6247',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=01&curSunit=11',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=01&curSunit=12',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=01&curSunit=5946',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=05&curSunit=5',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=05&curSunit=3',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=05&curSunit=6108',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=05&curSunit=4',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=05&curSunit=2',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=12&curSunit=17',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=06&curSunit=1',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=6187',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=56',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=74',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=61',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=6267',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=08&curSunit=6066',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=08&curSunit=6366',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=10&curSunit=76',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=54',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=09&curSunit=6026',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=08&curSunit=6067',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=08&curSunit=6486',
]

SELENIUM_URLS = [
    "https://obs.acibadem.edu.tr",
]

def get_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_with_selenium(url):
    try:
        driver = get_selenium_driver()
        driver.get(url)
        time.sleep(3)
        title = driver.title
        content = driver.find_element(By.TAG_NAME, "body").text
        content = ' '.join(content.split())
        driver.quit()
        return title, content
    except Exception as e:
        print(f"Selenium error for {url}: {e}")
        return None, None

def to_english_url(url):
    return url.replace(
        'https://www.acibadem.edu.tr/',
        'https://www.acibadem.edu.tr/en/'
    )

def english_url_exists(url):
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
    print("\nScraping OBS pages with Selenium...")
    for url in SELENIUM_URLS:
        print(f"Selenium scraping: {url}")
        title, content = scrape_with_selenium(url)
        if title and content and len(content) > 100:
            Page.objects.update_or_create(
                url=url,
                defaults={'title': title, 'content': content}
            )
            print(f"  ✓ Saved: {title[:50]}")
            success += 1
        else:
            print(f"  ✗ Failed")
            failed += 1
    print("\nScraping Bologna/OBS pages...")
    for url in BOLOGNA_URLS:
        print(f"Scraping: {url}")
        title, content = get_page_content(url)
        if title and content and len(content) > 100:
            Page.objects.update_or_create(
                url=url,
                defaults={'title': title, 'content': content}
            )
            print(f"  ✓ Saved: {title[:50]}")
            success += 1
        else:
            print(f"  ✗ Failed or empty")
            failed += 1
        time.sleep(0.3)
    print("=" * 50)
    print(f"Done! Saved: {success} | Failed: {failed}")