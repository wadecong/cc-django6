"""
Content models for the content aggregator.
Supports multi-platform content collection with AI-generated descriptions.
"""

from django.db import models
from django.contrib.auth.models import User


class Platform(models.Model):
    """Supported content platforms (X, TikTok, Facebook, etc.)"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class or emoji
    base_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for content categorization and search"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#6366f1")  # Hex color
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tags",
        null=True,
        blank=True  # null = system tag
    )
    is_auto_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["name", "user"]]

    def __str__(self):
        return self.name


class Collection(models.Model):
    """User-defined collections to organize content"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="collections"
    )
    is_default = models.BooleanField(default=False)
    cover_image = models.ImageField(
        upload_to="collections/covers/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [["name", "user"]]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Content(models.Model):
    """Main content model - stores saved content from various platforms"""

    class ContentType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        LINK = "link", "Link"
        MIXED = "mixed", "Mixed"

    class ProcessingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    # Core fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contents"
    )
    title = models.CharField(max_length=500, blank=True)
    original_text = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=10,
        choices=ContentType.choices,
        default=ContentType.TEXT
    )

    # Source information
    platform = models.ForeignKey(
        Platform,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contents"
    )
    source_url = models.URLField(max_length=2000, blank=True)
    source_id = models.CharField(max_length=200, blank=True)  # Platform-specific ID
    author_name = models.CharField(max_length=200, blank=True)
    author_handle = models.CharField(max_length=200, blank=True)

    # Media
    media_file = models.FileField(
        upload_to="contents/media/%Y/%m/",
        blank=True,
        null=True
    )
    thumbnail = models.ImageField(
        upload_to="contents/thumbnails/%Y/%m/",
        blank=True,
        null=True
    )
    media_url = models.URLField(max_length=2000, blank=True)  # Original media URL

    # AI-generated description
    ai_description = models.TextField(blank=True)
    ai_summary = models.CharField(max_length=500, blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING
    )

    # Organization
    tags = models.ManyToManyField(Tag, blank=True, related_name="contents")
    collections = models.ManyToManyField(
        Collection,
        blank=True,
        related_name="contents"
    )

    # Search optimization
    search_text = models.TextField(blank=True)  # Combined searchable text
    embedding = models.JSONField(null=True, blank=True)  # Vector embedding for semantic search

    # Metadata
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    original_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["platform", "-created_at"]),
            models.Index(fields=["content_type"]),
            models.Index(fields=["processing_status"]),
        ]

    def __str__(self):
        return self.title or f"Content #{self.pk}"

    def save(self, *args, **kwargs):
        # Build search text from all searchable fields
        self.search_text = " ".join(filter(None, [
            self.title,
            self.original_text,
            self.ai_description,
            self.ai_summary,
            self.author_name,
        ]))
        super().save(*args, **kwargs)


class MediaDescription(models.Model):
    """AI-generated descriptions for media content"""

    class DescriptionType(models.TextChoices):
        OCR = "ocr", "OCR Text"
        CAPTION = "caption", "Image Caption"
        TRANSCRIPT = "transcript", "Video Transcript"
        SCENE = "scene", "Scene Description"
        MEME = "meme", "Meme Analysis"

    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name="media_descriptions"
    )
    description_type = models.CharField(
        max_length=20,
        choices=DescriptionType.choices
    )
    text = models.TextField()
    confidence = models.FloatField(default=0.0)
    language = models.CharField(max_length=10, default="en")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_description_type_display()} for Content #{self.content_id}"


class SearchHistory(models.Model):
    """User search history for suggestions and analytics"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="search_history"
    )
    query = models.CharField(max_length=500)
    results_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Search histories"

    def __str__(self):
        return f"{self.user.username}: {self.query}"
