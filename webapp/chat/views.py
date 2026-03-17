from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage, Page
import json
import requests

# 1. Page view - Restored to normal
def chat_page(request):
    recent_messages = ChatMessage.objects.all()[:20]
    return render(request, 'chat/chat.html', {
        'messages': recent_messages
    })

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'ACU Chatbot is running!'})

# 2. API view - Your Week 4 Task
@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_question = data.get('message', '')

            # Search Database (Context Retrieval)
            related_content = Page.objects.filter(content__icontains=user_question[:20]).first()
            context = related_content.content if related_content else "No specific university data found."

            # Build the prompt for the AI
            full_prompt = f"Use this context to answer: {context}\n\nQuestion: {user_question}"

            # Talk to AI container
            ai_answer = "I'm having trouble reaching the AI service right now."
            try:
                response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={"model": "phi3", "prompt": full_prompt, "stream": False},
                    timeout=10
                )
                if response.status_code == 200:
                    ai_answer = response.json().get('response', '')
            except requests.exceptions.RequestException:
                pass 

            ChatMessage.objects.create(question=user_question, answer=ai_answer)

            return JsonResponse({"answer": ai_answer})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)