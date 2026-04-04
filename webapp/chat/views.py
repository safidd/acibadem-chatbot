from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pgvector.django import CosineDistance  # <-- NEW IMPORT FOR VECTOR MATH
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


PROGRAM_URLS = [
    'https://www.acibadem.edu.tr/en/akademik/lisans/muhendislik-ve-doga-bilimleri-fakultesi',
    'https://www.acibadem.edu.tr/en/akademik/lisans/saglik-bilimleri-fakultesi',
    'https://www.acibadem.edu.tr/en/akademik/lisans/tip-fakultesi',
    'https://obs.acibadem.edu.tr/oibs/bologna/index.aspx?lang=en&curOp=showPac&curUnit=04&curSunit=6166',
]

TRANSPORT_URLS = [
    'https://www.acibadem.edu.tr/en/kayit/iletisim/ulasim',
]

STUDENT_LIFE_URLS = [
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=305&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=301&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=309&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=304&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=302&lang=en',
    'https://obs.acibadem.edu.tr/oibs/bologna/dynConPage.aspx?curPageId=303&lang=en',
]

PROGRAM_KEYWORDS = ['program', 'faculty', 'course', 'study', 'degree',
                    'undergraduate', 'graduate', 'master', 'phd', 'offer', 'school',
                    'department', 'head', 'director', 'chair', 'engineering', 'computer',
                    'doctorate', 'doctoral']

TRANSPORT_KEYWORDS = ['bus', 'metro', 'transport', 'reach', 'get to',
                      'direction', 'how to come', 'located', 'campus', 'ulasim']

STUDENT_LIFE_KEYWORDS = ['club', 'clubs', 'accommodation', 'dormitory', 'dorm',
                          'sport', 'fitness', 'food', 'cafeteria',
                          'social', 'housing', 'health service']


@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_question = data.get('message', '')

            if not user_question.strip():
                return JsonResponse({"answer": "Please ask a question!"})

            # --- START OF WEEK 7 SEMANTIC SEARCH UPGRADE ---
            
            # 1. Ask Ollama to turn the user's question into a mathematical vector
            question_vector = None
            try:
                embed_response = requests.post(
                    "http://ollama:11434/api/embeddings",
                    json={"model": "phi3", "prompt": user_question},
                    timeout=10
                )
                if embed_response.status_code == 200:
                    question_vector = embed_response.json().get('embedding')
            except requests.exceptions.RequestException:
                pass # If it fails, question_vector remains None

            # 2. Search PostgreSQL for the closest matching page vectors using Cosine Distance
            if question_vector:
                # This mathematically sorts the pages by closest meaning, grabbing the top 3
                pages = Page.objects.filter(embedding__isnull=False).order_by(
                    CosineDistance('embedding', question_vector)
                )[:3]
            else:
                pages = []

            # --- END OF UPGRADE ---

            # Build the context string from the retrieved pages
            if pages:
                context_parts = []
                for page in pages:
                    limit = 1500 if is_program_question else 500
                    context_parts.append(f"--- {page.title} ---\n{page.content[:limit]}")
                context = "\n\n".join(context_parts)
            else:
<<<<<<< HEAD
                # If no relevant pages are found or vector search fails, provide an empty context
                context = "No specific context found in the database."
=======
                all_pages = Page.objects.filter(
                    Q(url__icontains='/en/') | Q(url__icontains='lang=en')
                )[:2]
                context_parts = [f"--- {p.title} ---\n{p.content[:500]}" for p in all_pages]
                context = "\n\n".join(context_parts)
>>>>>>> 104d697d56acabe9c3fc9253070debfd0433648a

            full_prompt = f"""You are a helpful assistant for Acibadem University (ACU) in Istanbul, Turkey.
Use the following information from ACU's website to answer the question accurately.
Always respond in English regardless of the language of the context.
Be specific — list actual names, bus numbers, locations, and details mentioned in the context.
Do not give vague summaries. Answer directly and concisely.
Only answer based on the provided context. If the context doesn't contain the answer, say so politely.

Context:
{context}

Question: {user_question}

Answer:"""

<<<<<<< HEAD
            # Call Ollama to generate the final chat answer
=======
>>>>>>> 104d697d56acabe9c3fc9253070debfd0433648a
            ai_answer = "Sorry, I am having trouble connecting to my AI brain right now."
            try:
                response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={"model": "phi3", "prompt": full_prompt, "stream": False},
                    timeout=180
                )
                if response.status_code == 200:
                    ai_answer = response.json().get('response', '')
                else:
                    ai_answer = f"The AI service returned an error (Code: {response.status_code})."

            except requests.exceptions.Timeout:
                ai_answer = "I am taking too long to think! Please try asking again."
            except requests.exceptions.ConnectionError:
                ai_answer = "My AI server is currently offline. Please check Docker!"

            ChatMessage.objects.create(question=user_question, answer=ai_answer)

            return JsonResponse({"answer": ai_answer})

        except json.JSONDecodeError:
            return JsonResponse({"answer": "There was an error reading your message."}, status=400)
        except Exception as e:
            return JsonResponse({"answer": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)