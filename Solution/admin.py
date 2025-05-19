

from django.contrib import admin
from .models import Chat, UploadedDocument, DocumentQA

admin.site.register(Chat)
admin.site.register(UploadedDocument)
admin.site.register(DocumentQA)
