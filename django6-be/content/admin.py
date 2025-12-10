"""
Django Admin configuration for content models.
"""

from django.contrib import admin
from .models import Platform, Tag, Collection, Content, MediaDescription, SearchHistory


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color", "user", "is_auto_generated", "created_at"]
    list_filter = ["is_auto_generated", "user"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_default", "created_at", "updated_at"]
    list_filter = ["is_default", "user"]
    search_fields = ["name", "description"]


class MediaDescriptionInline(admin.TabularInline):
    model = MediaDescription
    extra = 0
    readonly_fields = ["description_type", "text", "confidence", "created_at"]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "title_short", "content_type", "platform", "user",
        "processing_status", "is_favorite", "created_at"
    ]
    list_filter = ["content_type", "platform", "processing_status", "is_favorite", "is_archived"]
    search_fields = ["title", "original_text", "ai_description", "search_text"]
    readonly_fields = ["ai_description", "ai_summary", "search_text", "embedding", "created_at", "updated_at"]
    filter_horizontal = ["tags", "collections"]
    inlines = [MediaDescriptionInline]

    def title_short(self, obj):
        return obj.title[:50] + "..." if obj.title and len(obj.title) > 50 else obj.title
    title_short.short_description = "Title"


@admin.register(MediaDescription)
class MediaDescriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "content", "description_type", "confidence", "language", "created_at"]
    list_filter = ["description_type", "language"]
    search_fields = ["text"]
    readonly_fields = ["created_at"]


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "query", "results_count", "created_at"]
    list_filter = ["user"]
    search_fields = ["query"]
    readonly_fields = ["created_at"]
