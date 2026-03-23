from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatMessage
from .llm import answer_question

def chat_page(request):
    recent_messages = ChatMessage.objects.all().order_by('-created_at')[:20]
    return render(request, 'chat/chat.html', {
        'messages': recent_messages
    })

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'ACU Chatbot is running!'})

@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()

            if not question:
                return JsonResponse({'error': 'No question provided'}, status=400)

            # Get answer from Ollama with DB context
            answer = answer_question(question)

            # Save to chat history
            chat_message = ChatMessage.objects.create(
                question=question,
                answer=answer
            )

            return JsonResponse({
                'question': question,
                'answer': answer,
                'id': chat_message.id
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST request required'}, status=405)