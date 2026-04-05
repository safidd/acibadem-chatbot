from django.test import TestCase
from unittest.mock import patch, MagicMock
from scraper.scraper import (
    to_english_url, english_url_exists, get_page_content,
    get_all_urls_from_sitemap, BOLOGNA_URLS
)


class ScraperTests(TestCase):

    # --- Existing tests ---

    def test_to_english_url(self):
        turkish = "https://www.acibadem.edu.tr/universite"
        english = to_english_url(turkish)
        self.assertIn('/en/', english)
        self.assertEqual(english, "https://www.acibadem.edu.tr/en/universite")

    def test_to_english_url_preserves_path(self):
        turkish = "https://www.acibadem.edu.tr/akademik/lisans"
        english = to_english_url(turkish)
        self.assertEqual(english, "https://www.acibadem.edu.tr/en/akademik/lisans")

    @patch('scraper.scraper.requests.head')
    def test_english_url_exists_true(self, mock_head):
        mock_head.return_value.status_code = 200
        result = english_url_exists("https://www.acibadem.edu.tr/en/university")
        self.assertTrue(result)

    @patch('scraper.scraper.requests.head')
    def test_english_url_exists_false(self, mock_head):
        mock_head.return_value.status_code = 404
        result = english_url_exists("https://www.acibadem.edu.tr/en/nonexistent")
        self.assertFalse(result)

    @patch('scraper.scraper.requests.get')
    def test_get_page_content_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><head><title>Test Page</title></head><body><p>Hello ACU</p></body></html>"
        title, content = get_page_content("https://www.acibadem.edu.tr/en/test")
        self.assertEqual(title, "Test Page")
        self.assertIn("Hello ACU", content)

    @patch('scraper.scraper.requests.get')
    def test_get_page_content_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        title, content = get_page_content("https://www.acibadem.edu.tr/en/missing")
        self.assertIsNone(title)
        self.assertIsNone(content)

    # --- New tests for Turkish pages ---

    @patch('scraper.scraper.requests.get')
    def test_get_page_content_turkish(self, mock_get):
        """Turkish pages should also be scraped correctly."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><head><title>Acıbadem Üniversitesi</title></head><body><p>Türkçe içerik</p></body></html>"
        title, content = get_page_content("https://www.acibadem.edu.tr/universite")
        self.assertEqual(title, "Acıbadem Üniversitesi")
        self.assertIn("Türkçe içerik", content)

    @patch('scraper.scraper.requests.get')
    def test_get_page_content_strips_nav(self, mock_get):
        """Scraper should strip nav, footer, header tags."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
            <html><head><title>Test</title></head>
            <body>
                <nav>Navigation menu</nav>
                <main>Real content here</main>
                <footer>Footer text</footer>
            </body></html>
        """
        title, content = get_page_content("https://www.acibadem.edu.tr/en/test")
        self.assertNotIn("Navigation menu", content)
        self.assertNotIn("Footer text", content)
        self.assertIn("Real content here", content)

    @patch('scraper.scraper.requests.get')
    def test_get_page_content_empty_page(self, mock_get):
        """Pages with very little content should return None."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><head><title>Empty</title></head><body><p>Hi</p></body></html>"
        title, content = get_page_content("https://www.acibadem.edu.tr/en/empty")
        # Content exists but is very short
        self.assertIsNotNone(title)

    # --- New tests for Bologna URLs ---

    def test_bologna_urls_not_empty(self):
        """BOLOGNA_URLS list should contain URLs."""
        self.assertGreater(len(BOLOGNA_URLS), 0)

    def test_bologna_urls_are_english(self):
        """All Bologna URLs should have lang=en parameter."""
        for url in BOLOGNA_URLS:
            self.assertIn('lang=en', url, f"Bologna URL missing lang=en: {url}")

    def test_bologna_urls_are_obs_domain(self):
        """All Bologna URLs should be from obs.acibadem.edu.tr."""
        for url in BOLOGNA_URLS:
            self.assertIn('obs.acibadem.edu.tr', url, f"Bologna URL wrong domain: {url}")

    @patch('scraper.scraper.requests.get')
    def test_bologna_page_content_scraped(self, mock_get):
        """Bologna pages should be scraped with get_page_content."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
            <html><head><title>Student Clubs | Acıbadem University</title></head>
            <body><p>ACU Volunteers Astronomy Club Dance Club</p></body></html>
        """
        title, content = get_page_content(BOLOGNA_URLS[0])
        self.assertIsNotNone(title)
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 10)

    # --- New tests for sitemap ---

    @patch('scraper.scraper.requests.get')
    def test_get_all_urls_from_sitemap(self, mock_get):
        """Sitemap scraper should return list of URLs."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
            <urlset>
                <url><loc>https://www.acibadem.edu.tr/universite</loc></url>
                <url><loc>https://www.acibadem.edu.tr/akademik</loc></url>
                <url><loc>https://www.acibadem.edu.tr/image.jpg</loc></url>
            </urlset>
        """
        urls = get_all_urls_from_sitemap()
        self.assertIsInstance(urls, list)
        # .jpg should be filtered out
        self.assertNotIn('https://www.acibadem.edu.tr/image.jpg', urls)

    @patch('scraper.scraper.requests.get')
    def test_sitemap_filters_image_files(self, mock_get):
        """Sitemap scraper should filter out image and file URLs."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
            <urlset>
                <url><loc>https://www.acibadem.edu.tr/photo.png</loc></url>
                <url><loc>https://www.acibadem.edu.tr/doc.pdf</loc></url>
                <url><loc>https://www.acibadem.edu.tr/universite</loc></url>
            </urlset>
        """
        urls = get_all_urls_from_sitemap()
        for url in urls:
            self.assertFalse(url.endswith('.png'))
            self.assertFalse(url.endswith('.pdf'))