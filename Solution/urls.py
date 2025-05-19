

# Solution/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import verify_otp
from django.contrib.auth import views as auth_views
from .views import send_contact_email




urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('', views.home, name='home'),
    path('questions/', views.questions, name='questions'),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('logout/', views.logoutview, name='logout'),
    path('about/', views.about_view, name='about'),
    # path('generate-audio/', views.generate_audio, name='generate_audio'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),

    # Password reset flows
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # OCR
    path('extract-text/', views.extract_text, name='extract_text'),

    # RAG (Document upload + ask)
    path('rag/', views.upload_document, name='rag'),  # ✅ Only one time
    path('upload_document/', views.upload_document, name='upload_document'),
    path('ask_question_document/', views.ask_question_document, name='ask_question_document'),
    path('load_documents/', views.load_documents, name='load_documents'),  # 🔥 for sidebar document list
    path('load_document_chat/<int:document_id>/', views.load_document_chat, name='load_document_chat'),  # 🔥 for loading document chats
    path('delete_document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('send-message/', send_contact_email, name='send_message'),
    path('rag/', views.rag_view, name='rag'),
    path('llama3_inference/', views.llama3_inference, name='llama3_inference'),
    path('llama3/', views.llama3_view, name='llama3'),
    path('llama3/infer/', views.llama3_inference, name='llama3_inference'),
    path('delete-model-chat/<int:chat_id>/', views.delete_model_chat, name='delete_model_chat'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
