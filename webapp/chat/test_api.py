from django.test import TestCase, Client
from .models import FavoritePrompt
import json

class APIEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Bypassing the reverse() lookup to avoid namespace headaches.
        # We know exactly where this lives now!
        self.favorites_url = '/api/favorites/'

    def test_save_favorite_prompt(self):
        """Test that a user can save a favorite question and answer."""
        payload = {
            "question": "What is the capital of Turkey?",
            "answer": "The capital of Turkey is Ankara."
        }
        response = self.client.post(
            self.favorites_url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FavoritePrompt.objects.count(), 1)
        self.assertEqual(FavoritePrompt.objects.first().question, "What is the capital of Turkey?")

    def test_get_favorite_prompts(self):
        """Test that the endpoint returns saved favorites."""
        FavoritePrompt.objects.create(question="Test Q", answer="Test A")
        
        response = self.client.get(self.favorites_url)
        data = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('favorites' in data)
        self.assertEqual(len(data['favorites']), 1)
        self.assertEqual(data['favorites'][0]['question'], "Test Q")
