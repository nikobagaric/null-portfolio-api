"""
Tests for the blog post api
"""

# my dumb dumb called user user and now it is too late

# import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Blog,
    Tag,
)

from blog.serializers import (
    BlogSerializer,
    BlogDetailSerializer,
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

    post = Blog.objects.create(user=user, **defaults)
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
        res = self.client.get(BLOG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
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

    def test_get_post_detail(self):
        """Test get post details"""
        post = create_post(self.user)

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = BlogDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_post(self):
        """Test POSTing a post"""
        payload = {
            'title': 'Sample Text',
            'detail': 'Sample Text',
            'featured': True,
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Blog.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_partial_update(self):
        """Test patch on recipe"""
        orgdetail = 'Sample text'
        post = create_post(
            user=self.user,
            title='Sample',
            detail=orgdetail,
        )

        print(post)

        payload = {'title': 'New title'}
        url = detail_url(post.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        print(post)
        self.assertEqual(post.detail, orgdetail)
        self.assertEqual(post.user, self.user)

    def test_full_update(self):
        """Test full update of a post"""
        post = create_post(
            user=self.user,
            title='Sample',
            detail='orgdetail',
            featured=True,
        )
        payload = {
            'title': 'New title',
            'detail': 'New detail',
            'featured': False,
        }

        url = detail_url(post.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the post user results in an error."""
        new_user = create_user(
            email='user2@example.com',
            password='testpass123'
        )
        post = create_post(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(post.id)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.user, self.user)

    def test_delete_post(self):
        """Test deleting a post is succesful."""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(id=post.id).exists())

    def test_delete_other_users_post_error(self):
        """Test trying to delete another user's test gives an error"""
        new_user = create_user(email='user2@example.com', password='test123')
        post = create_post(user=new_user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Blog.objects.filter(id=post.id).exists())
