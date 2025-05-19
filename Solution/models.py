
# Solution/models.py

from django.db import models
from django.contrib.auth.models import User

class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

class Chat(models.Model):
    # Change the foreign key to use the built-in User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    short_title = models.CharField(max_length=3000, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_title:
            truncated_question = (self.question[:18] + "...") if len(self.question) > 18 else self.question
            self.short_title = truncated_question
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Chat by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"



class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)  # True = user's message, False = bot's reply
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = "User" if self.is_user else "Bot"
        return f"{who} at {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.content[:30]}"



from django.db import models
from django.contrib.auth.models import User

# (your existing models: CustomUser, Chat, Message)

# ➡️ NEW MODEL for extracted document content
class UploadedDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()  # ⬅️ store the extracted text, not the file
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document: {self.title} uploaded by {self.user.username}"

# ➡️ NEW MODEL for document-based Q&A
class DocumentQA(models.Model):
    document = models.ForeignKey(UploadedDocument, on_delete=models.CASCADE, related_name='qa_pairs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:30]}... (Document: {self.document.title})"

class OurModelChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    short_title = models.CharField(max_length=3000, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_title:
            truncated_question = (self.question[:18] + "...") if len(self.question) > 18 else self.question
            self.short_title = truncated_question
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OurModelChat by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    

class OurModelMessage(models.Model):
    chat = models.ForeignKey(OurModelChat, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)  # True = user's message, False = bot's reply
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = "User" if self.is_user else "Bot"
        return f"{who} at {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.content[:30]}"
