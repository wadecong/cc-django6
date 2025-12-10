"""
Initialize default data for the content aggregator.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import Platform, Tag


class Command(BaseCommand):
    help = "Initialize default platforms and tags"

    def handle(self, *args, **options):
        # Create default platforms
        platforms = [
            {"name": "X (Twitter)", "slug": "x", "icon": "x-twitter", "base_url": "https://x.com"},
            {"name": "TikTok", "slug": "tiktok", "icon": "tiktok", "base_url": "https://tiktok.com"},
            {"name": "Facebook", "slug": "facebook", "icon": "facebook", "base_url": "https://facebook.com"},
            {"name": "Instagram", "slug": "instagram", "icon": "instagram", "base_url": "https://instagram.com"},
            {"name": "YouTube", "slug": "youtube", "icon": "youtube", "base_url": "https://youtube.com"},
            {"name": "Reddit", "slug": "reddit", "icon": "reddit", "base_url": "https://reddit.com"},
            {"name": "Pinterest", "slug": "pinterest", "icon": "pinterest", "base_url": "https://pinterest.com"},
            {"name": "LinkedIn", "slug": "linkedin", "icon": "linkedin", "base_url": "https://linkedin.com"},
            {"name": "Weibo", "slug": "weibo", "icon": "weibo", "base_url": "https://weibo.com"},
            {"name": "Bilibili", "slug": "bilibili", "icon": "bilibili", "base_url": "https://bilibili.com"},
            {"name": "Other", "slug": "other", "icon": "globe", "base_url": ""},
        ]

        for p in platforms:
            platform, created = Platform.objects.get_or_create(
                slug=p["slug"],
                defaults=p
            )
            if created:
                self.stdout.write(f"Created platform: {platform.name}")
            else:
                self.stdout.write(f"Platform exists: {platform.name}")

        # Create default system tags
        tags = [
            {"name": "Meme", "slug": "meme", "color": "#f59e0b"},
            {"name": "News", "slug": "news", "color": "#3b82f6"},
            {"name": "Tutorial", "slug": "tutorial", "color": "#10b981"},
            {"name": "Entertainment", "slug": "entertainment", "color": "#ec4899"},
            {"name": "Tech", "slug": "tech", "color": "#8b5cf6"},
            {"name": "Sports", "slug": "sports", "color": "#ef4444"},
            {"name": "Music", "slug": "music", "color": "#14b8a6"},
            {"name": "Art", "slug": "art", "color": "#f97316"},
            {"name": "Food", "slug": "food", "color": "#84cc16"},
            {"name": "Travel", "slug": "travel", "color": "#06b6d4"},
        ]

        for t in tags:
            tag, created = Tag.objects.get_or_create(
                slug=t["slug"],
                user=None,  # System tag
                defaults=t
            )
            if created:
                self.stdout.write(f"Created tag: {tag.name}")
            else:
                self.stdout.write(f"Tag exists: {tag.name}")

        self.stdout.write(self.style.SUCCESS("Data initialization complete!"))
