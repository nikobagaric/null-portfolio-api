"""
Tests for the comments API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Comment,
    Blog,
)

from blog.serializers import (
    CommentSerializer,
)


COMMENT_URL = reverse('blog:comment-list')


def detail_url(comment_id):
    """Create and return a comment detail URL."""
    return reverse('blog:comment-detail', args=[comment_id])


def post_like_url(comment_id):
    """Create and return a comment like URL."""
    return reverse('blog:comment-like-post', args=[comment_id])


def create_post(user, **params):
    """Create and return a sample comment post"""
    defaults = {
        'title': 'Sample Text',
        'detail': 'Lorem ipsum dolor sit amet',
        'featured': True,
    }
    defaults.update(params)

    post = Comment.objects.create(user=user, **defaults)
    return post


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicCommentAPITests(TestCase):
    """Test unauthenticatged API requests for comment posts"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.post(COMMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentAPITests(TestCase):
    """Test authenticated API requests for comments"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='amogus@example.com',
            password='testpass123',
        )
        self.post = create_post(user=self.user)
        self.client.force_authenticate(self.user)

    def test_retrieve_comments(self):
        """Test retrieving a list of comments"""
        post = create_post()

        Comment.objects.create(user=self.user, post=self.post, body='body 1')
        Comment.objects.create(user=self.user, post=self.post, body='body 2')

        res = self.client.get(COMMENT_URL)

        comments = Comment.objects.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_comment(self):
        """Test updating a comment"""
        comment = Comment.objects.create(user=self.user, post=self.post, body='body 1')

        payload = {'body': 'body 2'}
        url = detail_url(comment.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.body, payload['body'])

    def test_delete_comment(self):
        """Test deleting a comment"""
        comment = Comment.objects.create(user=self.user, post=self.post, body='body 1')

        url = detail_url(comment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        comments = Comment.objects.filter(user=self.user)
        self.assertFalse(comments.exists())
