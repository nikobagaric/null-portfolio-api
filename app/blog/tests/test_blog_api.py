"""
Tests for the blog post api
"""

# my dumb dumb called user author and now it is too late

# import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Blog,
)

from blog.serializers import (
    BlogSerializer,
)

BLOG_URL = reverse('blog:blog-list')


def detail_url(blog_id):
    """Create and return a blog detail URL."""
    return reverse('blog:blog-detail', args=[blog_id])


def create_post(user, **params):
    """Create and return a sample blog post"""
    defaults = {
        'title': 'Sample Text',
        'detail': 'Lorem ipsum dolor sit amet',
        'featured': True,
    }
    defaults.update(params)

    post = Blog.objects.create(author=user, **defaults)
    return post


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicBlogAPITests(TestCase):
    """Test unauthenticatged API requests for blog posts"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res_a = self.client.get(BLOG_URL)
        res_b = self.client.post(BLOG_URL)

        self.assertEqual(res_a.status_code, status.HTTP_200_OK)
        self.assertEqual(res_b.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        """Set up user"""
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_posts(self):
        """Test retrieving a list of posts"""
        create_post(user=self.user)
        create_post(user=self.user)

        res = self.client.get(BLOG_URL)

        posts = Blog.objects.all().order_by('-id')
        serializer = BlogSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
