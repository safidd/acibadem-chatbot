from django.test import TestCase
from unittest.mock import patch, MagicMock
from scraper.scraper import to_english_url, english_url_exists, get_page_content

class ScraperTests(TestCase):

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
