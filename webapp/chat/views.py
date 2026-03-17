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

# 2. API view - Added error handling and better responses for edge cases
@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_question = data.get('message', '')

            # Polish 1: Check if the user sent an empty message
            if not user_question.strip():
                return JsonResponse({"answer": "Please ask a question!"})

            # Search Database (Context Retrieval)
            related_content = Page.objects.filter(content__icontains=user_question[:20]).first()
            if related_content:
                context = related_content.content
            else:
                context = "No specific Acibadem University data found for this topic."

            # Build the prompt for the AI
            full_prompt = f"Use this context to answer: {context}\n\nQuestion: {user_question}"

            # Talk to AI container
            ai_answer = "Sorry, I am having trouble connecting to my AI brain right now."
            try:
                response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={"model": "phi3", "prompt": full_prompt, "stream": False},
                    timeout=15 # Polish 2: Gave the AI a little more time to think
                )
                if response.status_code == 200:
                    ai_answer = response.json().get('response', '')
                else:
                    ai_answer = f"The AI service returned an error (Code: {response.status_code})."
                    
            # Polish 3: Catch specific connection errors so the app doesn't crash
            except requests.exceptions.Timeout:
                ai_answer = "I am taking too long to think! Please try asking again."
            except requests.exceptions.ConnectionError:
                ai_answer = "My AI server is currently offline. Please ask Bartu to check Docker!"

            # Save Chat History
            ChatMessage.objects.create(question=user_question, answer=ai_answer)

            return JsonResponse({"answer": ai_answer})

        # Polish 4: Catch bad data from the frontend
        except json.JSONDecodeError:
            return JsonResponse({"answer": "There was an error reading your message format."}, status=400)
        except Exception as e:
            # Catch-all for any other unexpected backend crashes
            return JsonResponse({"answer": "An unexpected server error occurred. Please try again later."}, status=500)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)