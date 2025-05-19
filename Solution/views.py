
# ///////////////////////////////////////////////////////////////////////////
import os
import random
import tempfile
import pytesseract
import docx2txt
from io import BytesIO
from PIL import Image
from gtts import gTTS
import base64

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from dotenv import load_dotenv
from .models import CustomUser, Chat, Message, UploadedDocument, DocumentQA
from .forms import SignupForm

# LangChain (updated imports)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb.config import Settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize models
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=GOOGLE_API_KEY)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=False)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
CHROMA_DIR = os.path.join(settings.BASE_DIR, "chroma_db")
chroma_client = chromadb.Client(Settings(
    persist_directory=CHROMA_DIR,
    anonymized_telemetry=False
))

def rag_view(request):
    return render(request, 'rag.html')


@csrf_exempt
def send_contact_email(request):
    if request.method == "POST":
        name = request.POST.get("name", "Anonymous")
        email = request.POST.get("email", "")
        message = request.POST.get("message", "")

        subject = f"New Contact Message from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                ['mathsolvexpert@gmail.com'],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ///////////////////////////////////////////////////////////////////////////
def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            otp = random.randint(1000, 9999)

            request.session['otp'] = otp
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password

            try:
                send_mail(
                    "Your OTP Code for Signup",
                    f"Your OTP code is: {otp}",
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                messages.success(request, "OTP sent to your email. Please verify.")
                return redirect('verify_otp')
            except Exception as e:
                messages.error(request, f"Failed to send OTP: {e}")
                return redirect('signup')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if int(entered_otp) == request.session.get('otp'):
            user = User.objects.create_user(
                username=request.session['username'],
                email=request.session['email'],
                password=request.session['password']
            )
            login(request, user)
            request.session.flush()
            messages.success(request, "Account created successfully!")
            return redirect('questions')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'verify_otp.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('about/')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect('questions/')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")


def logoutview(request):
    logout(request)
    return redirect('login')


class CustomLoginView(LoginView):
    template_name = 'login.html'


def about_view(request):
    return render(request, 'about.html')


# ///////////////////////////////////////////////////////////////////////////
# OCR
@csrf_exempt
def extract_text(request):
    if request.method == 'POST':
        try:
            image = Image.open(request.FILES['image'])
            extracted_text = pytesseract.image_to_string(image)
            return JsonResponse({"success": True, "text": extracted_text})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


# ///////////////////////////////////////////////////////////////////////////
# ChatGPT-like (text question) with Memory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# @login_required(login_url='login')
# def questions(request):
#     if request.method == 'POST':
#         user_input = request.POST.get('question', '').strip()
#         chat_id = request.POST.get('chat_id')
        
#         # prompt = f"Response in Markdown format, Solve the following query concisely using step-by-step explanations and if you were asked anything except the math don't explain.. and line break when there is mathametical expression.(i mean proper well structured)keep it in mind you will not respond any query that is not related to the math.. .\nQuery: {user_input}"
#         prompt = (
#             "You are a helpful AI assistant. You are only allowed to respond to queries that are mathematical in nature. "
#             "but if the user say hi,hey  or hello, don't say sorry .... say like math solver here  repsond like this,ask any math question "
#             "If the user asks about anything unrelated to math (e.g., politics, history, religion, etc.), respond with:\n\n"
#             "\"Sorry, I can only help with math-related questions. Please ask a math problem or concept.\"\n\n"
#             "Now respond strictly in Markdown format with step-by-step explanation and clearly formatted math expressions "
#             "using line breaks.\n\nQuery: " + user_input
#         )

#         try:
#             # chat_history = [SystemMessage(content='You are a helpful AI assistant')]  # Start with SystemMessage
#             chat_history = [SystemMessage(content="""
#                             You are a helpful AI assistant that only answers questions strictly related to mathematics.
#                             but if the user say hi,hey  or hello, don't say sorry .... say like math solver here  repsond like this,ask any math question
#                             You must refuse any question that is not related to math, with the reply:
#                             "Sorry, I can only help with math-related questions. Please ask a math problem or concept."

#                             Only use Markdown formatting. Structure your answers with step-by-step explanations and format math clearly.
#                             """)]
#             if chat_id:
#                 chat_instance = get_object_or_404(Chat, id=chat_id, user=request.user)
#                 messages_in_chat = chat_instance.messages.order_by('created_at')

#                 for msg in messages_in_chat:
#                     if msg.is_user:
#                         chat_history.append(HumanMessage(content=msg.content))
#                     else:
#                         chat_history.append(AIMessage(content=msg.content))
#             else:
#                 # If no chat_id, create new chat
#                 short_title = user_input.split("\n")[0][:50]
#                 chat_instance = Chat.objects.create(
#                     user=request.user,
#                     question=user_input,
#                     short_title=short_title
#                 )

#             # Add the current user question
#             chat_history.append(HumanMessage(content=user_input))

#             # Call Gemini model
#             result = llm.invoke(chat_history)

#             # Save messages
#             Message.objects.create(chat=chat_instance, is_user=True, content=user_input)
#             Message.objects.create(chat=chat_instance, is_user=False, content=result.content)

#             chat_instance.answer = result.content
#             chat_instance.save()

#             return JsonResponse({"success": True, "output": result.content, "chat_id": chat_instance.id})

#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})


#     else:
#         chat_id = request.GET.get('chat_id')
#         selected_chat = None
#         chat_messages = []

#         if chat_id:
#             selected_chat = get_object_or_404(Chat, id=chat_id, user=request.user)
#             memory.clear()
#             for msg in selected_chat.messages.order_by('created_at'):
#                 if msg.is_user:
#                     memory.chat_memory.add_user_message(msg.content)
#                 else:
#                     memory.chat_memory.add_ai_message(msg.content)
#             chat_messages = selected_chat.messages.order_by('created_at')

#         chat_history = Chat.objects.filter(user=request.user).order_by('-created_at')
#         return render(request, 'questions.html', {
#             'chat_history': chat_history,
#             'chat_messages': chat_messages,
#             'selected_chat': selected_chat
#         })








from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


import base64


from .models import Chat, Message
from PIL import Image as PILImage
import mimetypes
from io import BytesIO

@login_required(login_url='login')
def questions(request):
    if request.method == 'POST':
        user_input = request.POST.get('question', '').strip()
        chat_id = request.POST.get('chat_id')
        uploaded_image = request.FILES.get('image')

        prompt = (
            "You are a helpful AI assistant. You are only allowed to respond to queries that are mathematical in nature. "
            "but if the user say hi,hey  or hello, don't say sorry .... say like math solver here  respond like this, ask any math question. "
            "If the user asks about anything unrelated to math (e.g., politics, history, religion, etc.), respond with:\n\n"
            "\"Sorry, I can only help with math-related questions. Please ask a math problem or concept.\"\n\n"
            "Now respond strictly in Markdown format with step-by-step explanation and clearly formatted math expressions "
            "using line breaks.\n\nQuery: " + user_input
        )

        try:
            image = None
            if uploaded_image:
                image = PILImage.open(uploaded_image)

            # Initialize chat history with system prompt
            chat_history = [SystemMessage(content="""
                You are a helpful AI assistant that only answers questions strictly related to mathematics.
                but if the user say hi, hey or hello, don't say sorry .... say like math solver here respond like this, ask any math question.
                You must refuse any question that is not related to math, with the reply:
                "Sorry, I can only help with math-related questions. Please ask a math problem or concept."

                Only use Markdown formatting. Structure your answers with step-by-step explanations and format math clearly.
            """)]

            # Load existing chat or create a new one
            if chat_id:
                chat_instance = get_object_or_404(Chat, id=chat_id, user=request.user)
                messages_in_chat = chat_instance.messages.order_by('created_at')
                for msg in messages_in_chat:
                    if msg.is_user:
                        chat_history.append(HumanMessage(content=msg.content))
                    else:
                        chat_history.append(AIMessage(content=msg.content))
            else:
                short_title = user_input.split("\n")[0][:50]
                chat_instance = Chat.objects.create(user=request.user, question=user_input, short_title=short_title)

            chat_history.append(HumanMessage(content=user_input))

            # import base64
            # from langchain_core.messages import HumanMessage

            if image:
                # Convert image to base64 data URL
                buffer = BytesIO()
                image.save(buffer, format='PNG')
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

                human_message = HumanMessage(
                    content=[
                        {"type": "text", "text": user_input},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                )

                result = llm.invoke([human_message])
            else:
                result = llm.invoke(chat_history)



            # Save messages
            Message.objects.create(chat=chat_instance, is_user=True, content=user_input)
            Message.objects.create(chat=chat_instance, is_user=False, content=result.content)

            chat_instance.answer = result.content
            chat_instance.save()

            return JsonResponse({"success": True, "output": result.content, "chat_id": chat_instance.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # ✅ GET request — Load chat page
    else:
        chat_id = request.GET.get('chat_id')
        selected_chat = None
        chat_messages = []

        if chat_id:
            selected_chat = get_object_or_404(Chat, id=chat_id, user=request.user)
            from langchain.memory import ConversationBufferMemory
            memory = ConversationBufferMemory()
            memory.clear()
            for msg in selected_chat.messages.order_by('created_at'):
                if msg.is_user:
                    memory.chat_memory.add_user_message(msg.content)
                else:
                    memory.chat_memory.add_ai_message(msg.content)
            chat_messages = selected_chat.messages.order_by('created_at')

        chat_history = Chat.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'questions.html', {
            'chat_history': chat_history,
            'chat_messages': chat_messages,
            'selected_chat': selected_chat
        })



















@login_required(login_url='login')
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    messages.success(request, "Chat deleted successfully.")
    return redirect('questions')


# ///////////////////////////////////////////////////////////////////////////
# Upload Document
@login_required(login_url='login')
def upload_document(request):
    if request.method == 'POST':
        file = request.FILES.get('document')
        if not file:
            return JsonResponse({'success': False, 'error': 'No file uploaded.'})

        file_extension = os.path.splitext(file.name)[1].lower()
        text = ""

        try:
            if file_extension == '.pdf':
                from PyPDF2 import PdfReader
                reader = PdfReader(file)
                text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            elif file_extension == '.docx':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name
                text = docx2txt.process(tmp_path)
                os.remove(tmp_path)
            elif file_extension == '.txt':
                text = file.read().decode('utf-8')
            else:
                return JsonResponse({'success': False, 'error': 'Unsupported file format.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

        if not text.strip():
            return JsonResponse({'success': False, 'error': 'No text extracted from document.'})

        document = UploadedDocument.objects.create(
            user=request.user,
            title=file.name,
            content=text
        )

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)

        vectordb = Chroma(
            collection_name=f"doc_{document.id}",
            embedding_function=embedding_model,
            persist_directory=CHROMA_DIR
        )
        vectordb.add_texts(chunks)
        vectordb.persist()

        return JsonResponse({'success': True, 'document_id': document.id})

    return render(request, 'rag.html')


# ///////////////////////////////////////////////////////////////////////////
# Ask Question from Uploaded Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



# ///////////////////////////////////////////////////////////////////////////
@login_required(login_url='login')
def load_documents(request):
    documents = UploadedDocument.objects.filter(user=request.user).order_by('-uploaded_at')
    document_list = [
        {
            'id': doc.id,
            'title': doc.title
        }
        for doc in documents
    ]
    return JsonResponse({'success': True, 'documents': document_list})

# Load Document Chat History
@login_required(login_url='login')
def load_document_chat(request, document_id):
    try:
        document = UploadedDocument.objects.get(id=document_id, user=request.user)
        qa_pairs = document.qa_pairs.order_by('created_at')
        chat_data = [
            {
                'question': qa.question,
                'answer': qa.answer,
                'created_at': qa.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for qa in qa_pairs
        ]
        return JsonResponse({'success': True, 'chat': chat_data})
    except UploadedDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Document not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ///////////////////////////////////////////////////////////////////// //////
# Update ask_question_document to FALLBACK if document context is empty
@login_required(login_url='login')
def ask_question_document(request):
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        document_id = request.POST.get('document_id')

        if not question or not document_id:
            return JsonResponse({'success': False, 'error': 'Question and document ID required.'})

        try:
            document = UploadedDocument.objects.get(id=document_id, user=request.user)
            full_text = document.content

            prompt = PromptTemplate(
                template="Use the following document context to answer the question if not found then answer as best as you can no irrelevant answer:\n\n{context}\n\nQuestion: {question}",
                input_variables=["context", "question"]
            )
            parser = StrOutputParser()
            chain = prompt | llm | parser
            result = chain.invoke({
                "context": full_text,
                "question": question
            })

            # ✅ Check if answer is meaningful
            if not result or result.strip().lower() in ["", "i don't know", "not found", "no information available"]:
                # If not meaningful, fallback to model directly
                fallback_prompt = f"Provide a brief answer to: {question}"
                fallback_result = llm.invoke([HumanMessage(content=fallback_prompt)])
                answer = fallback_result.content
            else:
                answer = result

            # Save the question and answer
            DocumentQA.objects.create(
                document=document,
                user=request.user,
                question=question,
                answer=answer
            )

            # Generate TTS
            tts = gTTS(answer, lang='en')
            temp_audio_path = os.path.join(tempfile.gettempdir(), f"tts_{random.randint(1,99999)}.mp3")
            tts.save(temp_audio_path)

            audio_file = open(temp_audio_path, 'rb')
            # response = FileResponse(audio_file, content_type='audio/mpeg')
            # response['Content-Disposition'] = 'inline; filename="response.mp3"'
            # response['X-Text-Response'] = answer  # Important! frontend reads this 
            from django.http import JsonResponse
            import base64

            # Encode audio to base64
            with open(temp_audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            return JsonResponse({
                'success': True,
                'answer': answer,
                'audio_base64': audio_base64
            })


            # return response

        except UploadedDocument.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Document not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})





# to delete rag chat..






@login_required(login_url='login')
def delete_document(request, document_id):
    try:
        doc = UploadedDocument.objects.get(id=document_id, user=request.user)
        doc.delete()
        messages.success(request, "Document deleted.")
    except UploadedDocument.DoesNotExist:
        messages.error(request, "Document not found.")
    return redirect('rag')





from django.views.decorators.csrf import csrf_exempt
import requests
@login_required(login_url='login')
def llama3_view(request):
    chat_id = request.GET.get("chat_id")
    selected_chat = None
    chat_messages = []

    if chat_id:
        selected_chat = get_object_or_404(OurModelChat, id=chat_id, user=request.user)
        chat_messages = selected_chat.messages.order_by('created_at')

    chat_history = OurModelChat.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'llama3.html', {
        'chat_history': chat_history,
        'chat_messages': chat_messages,
        'selected_chat': selected_chat
    })

from .models import OurModelChat, OurModelMessage  # make sure this is imported

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import OurModelChat, OurModelMessage
import requests

# Assuming you have this already configured
from langchain_core.messages import SystemMessage, HumanMessage
from Solution.views import llm  # reuse the same llm instance from questions view
from langchain_core.messages import SystemMessage, HumanMessage
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import OurModelChat, OurModelMessage

@csrf_exempt
@login_required(login_url='login')
def llama3_inference(request):
    if request.method == "POST":
        user_input = request.POST.get("question", "").strip()
        chat_id = request.POST.get("chat_id")

        if not user_input:
            return JsonResponse({"success": False, "error": "Empty question."})

        try:
            # Build a pseudo-conversational history (if needed)
            messages = []
            if chat_id:
                chat_instance = get_object_or_404(OurModelChat, id=chat_id, user=request.user)
                previous_messages = chat_instance.messages.order_by('created_at')
                for msg in previous_messages:
                    if msg.is_user:
                        messages.append(HumanMessage(content=msg.content))
                    else:
                        messages.append(SystemMessage(content=msg.content))
            else:
                short_title = user_input.split("\n")[0][:50]
                chat_instance = OurModelChat.objects.create(
                    user=request.user,
                    question=user_input,
                    short_title=short_title
                )

            # Add current user message
            messages.append(HumanMessage(content=user_input))

            # Step 1: Query Colab model
            colab_api_url = "https://5dc4-34-125-207-203.ngrok-free.app/generate"
            colab_response = requests.post(colab_api_url, json={"problem": user_input}, timeout=15)
            colab_response.raise_for_status()
            raw_answer = colab_response.json().get("response", "No response from model.")

            # Step 2: Pass raw_answer to Gemini for correction + formatting
            gemini_prompt = [
                SystemMessage(content="""
                    You are a math assistant. Your job is to take raw responses related to mathematical problems and do the following:
                    
                    1. Correct any logical or mathematical errors.
                    2. Apply proper step-by-step explanation where needed.
                    3. Format the final response strictly in **Markdown** using line breaks and math expressions (\\( \\) or $$ $$).

                    Only answer if the input is math-related. If not, say:
                    "Sorry, I can only help with math-related questions. Please ask a math problem or concept.  but if the user say hi,hey  or hello, don't say sorry .... say like math solver here  repsond like this,ask any math question"
                """),
                HumanMessage(content=raw_answer)
            ]
            gemini_response = llm.invoke(gemini_prompt)
            if not hasattr(gemini_response, 'content'):
                raise ValueError("Gemini response is missing 'content'.")
            formatted_answer = gemini_response.content.strip()

            # Step 3: Save conversation
            OurModelMessage.objects.create(chat=chat_instance, is_user=True, content=user_input)
            OurModelMessage.objects.create(chat=chat_instance, is_user=False, content=formatted_answer)
            chat_instance.answer = formatted_answer
            chat_instance.save()

            return JsonResponse({
                "success": True,
                "output": formatted_answer,
                "chat_id": chat_instance.i
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({"success": False, "error": f"Colab request failed: {str(e)}"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import OurModelChat


@login_required(login_url='login')
def delete_model_chat(request, chat_id):
    chat = get_object_or_404(OurModelChat, id=chat_id, user=request.user)
    chat.delete()
    return redirect('llama3')




