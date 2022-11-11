"""
URL mappings for the blog app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from blog import views


router = DefaultRouter()
router.register('blog', views.BlogViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls))
]
