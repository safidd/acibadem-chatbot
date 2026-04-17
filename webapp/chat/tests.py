from django.test import TestCase, Client
from django.urls import reverse
from .models import ChatMessage
import json

class ChatAPITests(TestCase):
    def setUp(self):
        # This runs before every test to set up a fake browser and fake database data
        self.client = Client()
        self.msg = ChatMessage.objects.create(
            question="What is ACU?",
            answer="Acibadem University is a medical university."
        )

    def test_health_check_endpoint(self):
        """Test if the server is awake and healthy."""
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_chat_api_empty_message(self):
        """Test if the bot gracefully handles empty space instead of crashing."""
        response = self.client.post(
            reverse('api_chat'),
            json.dumps({"message": "     "}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['answer'], "Please ask a question!")

    def test_chat_api_wrong_method(self):
        """Test that users cannot use GET requests to send messages."""
        response = self.client.get(reverse('api_chat'))
        self.assertEqual(response.status_code, 405)

    def test_rate_message_success(self):
        """Test if the thumbs-up button correctly updates the database."""
        # Send a POST request to rate the fake message we created in setUp()
        response = self.client.post(reverse('rate_message', args=[self.msg.id]))
        self.assertEqual(response.status_code, 200)
        
        # Pull the message from the database again and verify the switch flipped to True
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_helpful)

    def test_rate_message_not_found(self):
        """Test rating a message ID that does not exist."""
        response = self.client.post(reverse('rate_message', args=[9999]))
        self.assertEqual(response.status_code, 404)