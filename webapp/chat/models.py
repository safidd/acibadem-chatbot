from django.db import models
from pgvector.django import VectorField

class Page(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, unique=True)
    content = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    embedding = VectorField(dimensions=768, null=True, blank=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_helpful = models.BooleanField(default=False)
    context_pages = models.ManyToManyField(Page, blank=True)

    def __str__(self):
        return f"Q: {self.question[:60]}"
class FavoritePrompt(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]
