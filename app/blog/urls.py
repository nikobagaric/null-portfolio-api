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
router.register('post', views.BlogViewSet)
router.register('tag', views.TagViewSet)
router.register('section', views.SectionViewSet)
router.register('comment', views.CommentViewSet)
router.register('reply', views.ReplyViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls))
]
