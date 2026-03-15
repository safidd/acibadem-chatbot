from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatMessage
from django.views.decorators.csrf import csrf_exempt
import json

def chat_page(request):
    recent_messages = ChatMessage.objects.all()[:20]
    return render(request, 'chat/chat.html', {
        'messages': recent_messages
    })

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'ACU Chatbot is running!'})

@csrf_exempt
def api_chat(request):
    # Check if the request is a POST request (meaning the user is sending data to us)
    if request.method == 'POST':
        try:
            # Load the JSON data sent by the frontend
            data = json.loads(request.body)
            user_question = data.get('message', '')
            
            # For Week 2, we just return a test response.
            response_data = {
                "answer": f"Backend received your question: '{user_question}'. AI connection coming soon!"
            }
            # Send the answer back to the user
            return JsonResponse(response_data)
            
        except Exception as e:
            # Basic error handling if the data is formatted wrong
            return JsonResponse({"error": "Invalid request format."}, status=400)
            
    # Reject anything that isn't a POST request
    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)