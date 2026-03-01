from django.contrib import admin

from app_chat.models import ChatMessage, ChatMedia, MessageReaction

admin.site.register([ChatMessage, ChatMedia, MessageReaction])
