from django.contrib import admin
from .models import Page, ChatMessage

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'scraped_at')
    search_fields = ('title', 'content')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    readonly_fields = ('created_at',)