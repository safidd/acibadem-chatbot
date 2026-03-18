from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import ChatMessage, Page
import json
import requests


def chat_page(request):
    recent_messages = ChatMessage.objects.all()[:20]
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
            user_question = data.get('message', '')

            if not user_question.strip():
                return JsonResponse({"answer": "Please ask a question!"})

            # Search database for relevant context
            keywords = [w for w in user_question.lower().split() if len(w) > 3]
            query = Q()
            for keyword in keywords:
                query |= Q(content__icontains=keyword) | Q(title__icontains=keyword)

            pages = Page.objects.filter(query).distinct()[:3]

            if pages:
                context_parts = []
                for page in pages:
                    context_parts.append(f"--- {page.title} ---\n{page.content[:1000]}")
                context = "\n\n".join(context_parts)
            else:
                all_pages = Page.objects.all()[:2]
                context_parts = [f"--- {p.title} ---\n{p.content[:500]}" for p in all_pages]
                context = "\n\n".join(context_parts)

            # Build prompt
            full_prompt = f"""You are a helpful assistant for Acibadem University (ACU) in Istanbul, Turkey.
Use the following information from ACU's website to answer the question accurately.
Always respond in English regardless of the language of the context.
Only answer based on the provided context. If the context doesn't contain the answer, say so politely.

Context:
{context}

Question: {user_question}

Answer:"""

            # Call Ollama
            ai_answer = "Sorry, I am having trouble connecting to my AI brain right now."
            try:
                response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={"model": "phi3", "prompt": full_prompt, "stream": False},
                    timeout=120
                )
                if response.status_code == 200:
                    ai_answer = response.json().get('response', '')
                else:
                    ai_answer = f"The AI service returned an error (Code: {response.status_code})."

            except requests.exceptions.Timeout:
                ai_answer = "I am taking too long to think! Please try asking again."
            except requests.exceptions.ConnectionError:
                ai_answer = "My AI server is currently offline. Please check Docker!"

            # Save to chat history
            ChatMessage.objects.create(question=user_question, answer=ai_answer)

            return JsonResponse({"answer": ai_answer})

        except json.JSONDecodeError:
            return JsonResponse({"answer": "There was an error reading your message."}, status=400)
        except Exception as e:
            return JsonResponse({"answer": "An unexpected error occurred. Please try again."}, status=500)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)