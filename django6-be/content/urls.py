"""
URL configuration for content API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"platforms", views.PlatformViewSet, basename="platform")
router.register(r"tags", views.TagViewSet, basename="tag")
router.register(r"collections", views.CollectionViewSet, basename="collection")
router.register(r"contents", views.ContentViewSet, basename="content")
router.register(r"search", views.SearchViewSet, basename="search")

urlpatterns = [
    path("", include(router.urls)),
]
