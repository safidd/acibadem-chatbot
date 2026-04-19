import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .models import FavoritePrompt
# Assuming your main chatbot function is importable here
from .llm import answer_question 

@csrf_exempt
def chat_endpoint(request):
    """Handles chat requests with Redis caching for scalability."""
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')

        # 1. Scalability: Check Redis Cache First
        cache_key = f"qa_{question.replace(' ', '_')}"
        cached_answer = cache.get(cache_key)
        
        if cached_answer:
            return JsonResponse({'answer': cached_answer, 'source': 'cache'})

        # 2. Generate Answer if not cached
        answer = answer_question(question)
        
        # 3. Store in cache for 1 hour (3600 seconds)
        cache.set(cache_key, answer, timeout=3600)
        
        return JsonResponse({'answer': answer, 'source': 'ai'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def favorites_endpoint(request):
    """Saves a new favorite or retrieves the list of favorites."""
    if request.method == 'POST':
        data = json.loads(request.body)
        fav = FavoritePrompt.objects.create(
            question=data.get('question'),
            answer=data.get('answer')
        )
        return JsonResponse({'status': 'success', 'id': fav.id})
    
    elif request.method == 'GET':
        # Return the 10 most recent favorites
        favs = list(FavoritePrompt.objects.values('id', 'question', 'answer').order_by('-id')[:10])
        return JsonResponse({'favorites': favs})
