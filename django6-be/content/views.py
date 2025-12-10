"""
REST API Views for content management.
Includes Django 6 async features.
"""

from django.db.models import Q
from django.core.paginator import AsyncPaginator  # Django 6 new feature
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Platform, Tag, Collection, Content, MediaDescription, SearchHistory
from .serializers import (
    PlatformSerializer,
    TagSerializer,
    CollectionSerializer,
    ContentListSerializer,
    ContentDetailSerializer,
    ContentCreateSerializer,
    MediaDescriptionSerializer,
    SearchHistorySerializer,
    SearchQuerySerializer,
    BulkImportSerializer,
)
from .tasks import process_media_description, generate_embedding, auto_tag_content


class PlatformViewSet(viewsets.ModelViewSet):
    """ViewSet for managing platforms"""
    queryset = Platform.objects.filter(is_active=True)
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def stats(self, request, slug=None):
        """Get statistics for a specific platform"""
        platform = self.get_object()
        user_contents = platform.contents.filter(user=request.user)
        return Response({
            "total_contents": user_contents.count(),
            "by_type": {
                choice[0]: user_contents.filter(content_type=choice[0]).count()
                for choice in Content.ContentType.choices
            },
            "favorites": user_contents.filter(is_favorite=True).count(),
        })


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tags"""
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        # User tags + system tags (user=None)
        return Tag.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def popular(self, request):
        """Get most used tags"""
        tags = self.get_queryset().order_by("-contents__count")[:20]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)


class CollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing collections"""
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_content(self, request, pk=None):
        """Add content to collection"""
        collection = self.get_object()
        content_ids = request.data.get("content_ids", [])

        contents = Content.objects.filter(
            id__in=content_ids,
            user=request.user
        )
        collection.contents.add(*contents)

        return Response({"added": contents.count()})

    @action(detail=True, methods=["post"])
    def remove_content(self, request, pk=None):
        """Remove content from collection"""
        collection = self.get_object()
        content_ids = request.data.get("content_ids", [])

        contents = Content.objects.filter(
            id__in=content_ids,
            user=request.user
        )
        collection.contents.remove(*contents)

        return Response({"removed": contents.count()})


class ContentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content with Django 6 features"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at", "view_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Content.objects.filter(user=self.request.user)

        # Filter by content type
        content_type = self.request.query_params.get("type")
        if content_type:
            queryset = queryset.filter(content_type=content_type)

        # Filter by platform
        platform = self.request.query_params.get("platform")
        if platform:
            queryset = queryset.filter(platform__slug=platform)

        # Filter by tags
        tags = self.request.query_params.getlist("tags")
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        # Filter by collection
        collection = self.request.query_params.get("collection")
        if collection:
            queryset = queryset.filter(collections__id=collection)

        # Filter favorites
        favorites = self.request.query_params.get("favorites")
        if favorites == "true":
            queryset = queryset.filter(is_favorite=True)

        # Filter archived
        include_archived = self.request.query_params.get("include_archived")
        if include_archived != "true":
            queryset = queryset.filter(is_archived=False)

        return queryset.select_related("platform").prefetch_related("tags")

    def get_serializer_class(self):
        if self.action == "list":
            return ContentListSerializer
        elif self.action == "create":
            return ContentCreateSerializer
        return ContentDetailSerializer

    def perform_create(self, serializer):
        content = serializer.save(user=self.request.user)

        # Queue background tasks for media processing (Django 6 feature)
        if content.content_type in [Content.ContentType.IMAGE, Content.ContentType.VIDEO]:
            process_media_description.enqueue(content.id)

        # Generate embeddings and auto-tag
        generate_embedding.enqueue(content.id)
        auto_tag_content.enqueue(content.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        """Toggle favorite status"""
        content = self.get_object()
        content.is_favorite = not content.is_favorite
        content.save(update_fields=["is_favorite"])
        return Response({"is_favorite": content.is_favorite})

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Toggle archive status"""
        content = self.get_object()
        content.is_archived = not content.is_archived
        content.save(update_fields=["is_archived"])
        return Response({"is_archived": content.is_archived})

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        """Re-process media for AI descriptions"""
        content = self.get_object()

        if content.content_type not in [Content.ContentType.IMAGE, Content.ContentType.VIDEO]:
            return Response(
                {"error": "Only image and video content can be processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear existing descriptions
        content.media_descriptions.all().delete()
        content.processing_status = Content.ProcessingStatus.PENDING
        content.save(update_fields=["processing_status"])

        # Queue for reprocessing
        process_media_description.enqueue(content.id)
        generate_embedding.enqueue(content.id)

        return Response({"status": "queued"})

    @action(detail=False, methods=["post"])
    def bulk_import(self, request):
        """Bulk import content from a platform"""
        serializer = BulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        platform = serializer.validated_data["platform"]
        items = serializer.validated_data["items"]

        created_count = 0
        for item in items:
            content, created = Content.objects.get_or_create(
                user=request.user,
                platform=platform,
                source_id=item.get("source_id", ""),
                defaults={
                    "title": item.get("title", ""),
                    "original_text": item.get("text", ""),
                    "content_type": item.get("content_type", Content.ContentType.TEXT),
                    "source_url": item.get("url", ""),
                    "media_url": item.get("media_url", ""),
                    "author_name": item.get("author_name", ""),
                    "author_handle": item.get("author_handle", ""),
                }
            )
            if created:
                created_count += 1
                # Queue processing
                if content.content_type in [Content.ContentType.IMAGE, Content.ContentType.VIDEO]:
                    process_media_description.enqueue(content.id)
                generate_embedding.enqueue(content.id)

        return Response({
            "imported": created_count,
            "total": len(items),
            "skipped": len(items) - created_count,
        })

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get user content statistics"""
        queryset = Content.objects.filter(user=request.user)
        return Response({
            "total": queryset.count(),
            "by_type": {
                choice[0]: queryset.filter(content_type=choice[0]).count()
                for choice in Content.ContentType.choices
            },
            "by_platform": {
                p.name: queryset.filter(platform=p).count()
                for p in Platform.objects.filter(is_active=True)
            },
            "favorites": queryset.filter(is_favorite=True).count(),
            "archived": queryset.filter(is_archived=True).count(),
            "pending_processing": queryset.filter(
                processing_status=Content.ProcessingStatus.PENDING
            ).count(),
        })


class SearchViewSet(viewsets.ViewSet):
    """ViewSet for search functionality"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Search content with natural language.
        Supports both keyword and semantic search.
        """
        serializer = SearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["q"]
        content_type = serializer.validated_data.get("content_type")
        platform = serializer.validated_data.get("platform")
        tags = serializer.validated_data.get("tags", [])
        collection = serializer.validated_data.get("collection")
        favorites_only = serializer.validated_data.get("favorites_only", False)
        include_archived = serializer.validated_data.get("include_archived", False)
        use_semantic = serializer.validated_data.get("semantic", False)

        # Base queryset
        queryset = Content.objects.filter(user=request.user)

        # Apply filters
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if platform:
            queryset = queryset.filter(platform=platform)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if collection:
            queryset = queryset.filter(collections=collection)
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        if not include_archived:
            queryset = queryset.filter(is_archived=False)

        # Text search
        if use_semantic and query:
            # Semantic search using embeddings
            results = self._semantic_search(queryset, query)
        else:
            # Keyword search
            results = queryset.filter(
                Q(title__icontains=query) |
                Q(original_text__icontains=query) |
                Q(ai_description__icontains=query) |
                Q(ai_summary__icontains=query) |
                Q(search_text__icontains=query)
            )

        # Save search history
        SearchHistory.objects.create(
            user=request.user,
            query=query,
            results_count=results.count()
        )

        # Paginate results
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(results, request)

        serializer = ContentListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def _semantic_search(self, queryset, query):
        """Perform semantic search using vector embeddings"""
        from .tasks import _generate_text_embedding

        # Generate query embedding
        query_embedding = _generate_text_embedding(query)

        # Filter to only contents with embeddings
        contents_with_embeddings = queryset.exclude(embedding__isnull=True)

        # Calculate similarity scores
        results = []
        for content in contents_with_embeddings:
            if content.embedding:
                similarity = self._cosine_similarity(query_embedding, content.embedding)
                results.append((content, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top results as queryset
        content_ids = [r[0].id for r in results[:100]]
        return Content.objects.filter(id__in=content_ids)

    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 * magnitude2 == 0:
            return 0
        return dot_product / (magnitude1 * magnitude2)

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        """Get search suggestions based on history"""
        recent = SearchHistory.objects.filter(
            user=request.user
        ).values_list("query", flat=True).distinct()[:10]
        return Response({"suggestions": list(recent)})

    @action(detail=False, methods=["get"])
    def history(self, request):
        """Get search history"""
        history = SearchHistory.objects.filter(user=request.user)[:50]
        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear_history(self, request):
        """Clear search history"""
        deleted, _ = SearchHistory.objects.filter(user=request.user).delete()
        return Response({"deleted": deleted})
