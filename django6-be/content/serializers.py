"""
REST API Serializers for content models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Platform, Tag, Collection, Content, MediaDescription, SearchHistory


class PlatformSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()

    class Meta:
        model = Platform
        fields = ["id", "name", "slug", "icon", "base_url", "is_active", "content_count"]
        read_only_fields = ["id"]

    def get_content_count(self, obj):
        user = self.context.get("request")
        if user and user.user.is_authenticated:
            return obj.contents.filter(user=user.user).count()
        return 0


class TagSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "color", "is_auto_generated", "content_count", "created_at"]
        read_only_fields = ["id", "is_auto_generated", "created_at"]

    def get_content_count(self, obj):
        return obj.contents.count()


class CollectionSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()
    preview_items = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id", "name", "description", "is_default", "cover_image",
            "content_count", "preview_items", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_content_count(self, obj):
        return obj.contents.count()

    def get_preview_items(self, obj):
        items = obj.contents.all()[:4]
        return [
            {
                "id": item.id,
                "thumbnail": item.thumbnail.url if item.thumbnail else None,
                "title": item.title[:50] if item.title else None,
            }
            for item in items
        ]


class MediaDescriptionSerializer(serializers.ModelSerializer):
    description_type_display = serializers.CharField(
        source="get_description_type_display", read_only=True
    )

    class Meta:
        model = MediaDescription
        fields = [
            "id", "description_type", "description_type_display",
            "text", "confidence", "language", "metadata", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class ContentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    platform_name = serializers.CharField(source="platform.name", read_only=True)
    tag_names = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            "id", "title", "content_type", "platform_name",
            "thumbnail", "ai_summary", "is_favorite", "is_archived",
            "tag_names", "processing_status", "created_at"
        ]

    def get_tag_names(self, obj):
        return list(obj.tags.values_list("name", flat=True)[:5])


class ContentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views"""
    platform = PlatformSerializer(read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        source="platform",
        write_only=True,
        required=False,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        write_only=True,
        many=True,
        required=False
    )
    collections = CollectionSerializer(many=True, read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source="collections",
        write_only=True,
        many=True,
        required=False
    )
    media_descriptions = MediaDescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            "id", "title", "original_text", "content_type",
            "platform", "platform_id", "source_url", "source_id",
            "author_name", "author_handle",
            "media_file", "thumbnail", "media_url",
            "ai_description", "ai_summary", "processing_status",
            "tags", "tag_ids", "collections", "collection_ids",
            "media_descriptions",
            "is_favorite", "is_archived", "view_count",
            "original_created_at", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "ai_description", "ai_summary", "processing_status",
            "view_count", "created_at", "updated_at"
        ]


class ContentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new content"""
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        write_only=True,
        many=True,
        required=False
    )
    collection_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source="collections",
        write_only=True,
        many=True,
        required=False
    )

    class Meta:
        model = Content
        fields = [
            "title", "original_text", "content_type",
            "platform", "source_url", "source_id",
            "author_name", "author_handle",
            "media_file", "thumbnail", "media_url",
            "tag_ids", "collection_ids",
            "original_created_at"
        ]

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        collections = validated_data.pop("collections", [])
        content = Content.objects.create(**validated_data)
        content.tags.set(tags)
        content.collections.set(collections)
        return content


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ["id", "query", "results_count", "created_at"]
        read_only_fields = ["id", "results_count", "created_at"]


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search requests"""
    q = serializers.CharField(max_length=500, required=True)
    content_type = serializers.ChoiceField(
        choices=Content.ContentType.choices,
        required=False
    )
    platform = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Platform.objects.all(),
        required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        required=False
    )
    favorites_only = serializers.BooleanField(default=False)
    include_archived = serializers.BooleanField(default=False)
    semantic = serializers.BooleanField(default=False)  # Use vector search


class BulkImportSerializer(serializers.Serializer):
    """Serializer for bulk content import"""
    platform = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Platform.objects.all()
    )
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100
    )
