"""
Tests for the replys API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Comment,
    Reply,
    Blog,
)

from blog.serializers import (
    ReplySerializer,
)


REPLIES_URL = reverse('blog:reply-list')


def detail_url(reply_id):
    """Create and return a reply detail URL."""
    return reverse('blog:reply-detail', args=[reply_id])


def reply_like_url(reply_id):
    """Create and return a reply like URL."""
    return reverse('blog:reply-like-reply', args=[reply_id])


def create_post(user, **params):
    """Create and return a sample post"""
    defaults = {
        'title': 'Sample Text',
        'detail': 'Lorem ipsum dolor sit amet',
        'featured': True,
    }
    defaults.update(params)

    post = Blog.objects.create(user=user, **defaults)
    return post


def create_comment(user, post, **params):
    """Create and return a sample comment"""
    defaults = {
        'body': 'lorem ipsum',
    }
    defaults.update(params)

    comment = Comment.objects.create(user=user, post=post)
    comment.body = defaults['body']
    return comment


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicreplyAPITests(TestCase):
    """Test unauthenticatged API requests for reply replys"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.post(REPLIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatereplyAPITests(TestCase):
    """Test authenticated API requests for replys"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='amogus@example.com',
            password='testpass123',
        )
        self.post = create_post(user=self.user)
        self.comment = create_comment(user=self.user, post=self.post)
        self.client.force_authenticate(self.user)

    def test_retrieve_replies(self):
        """Test retrieving a list of replies"""
        Reply.objects.create(user=self.user, comment=self.comment, body='body 1')
        Reply.objects.create(user=self.user, comment=self.comment, body='body 2')

        res = self.client.get(REPLIES_URL)

        replies = Reply.objects.all().order_by('-created_at')
        serializer = ReplySerializer(replies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_reply(self):
        """Test updating a reply"""
        reply = Reply.objects.create(user=self.user, comment=self.comment, body='body 1')

        payload = {'body': 'body 2'}
        url = detail_url(reply.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reply.refresh_from_db()
        self.assertEqual(reply.body, payload['body'])

    def test_delete_reply(self):
        """Test deleting a reply"""
        reply = Reply.objects.create(user=self.user, comment=self.comment, body='body 1')

        url = detail_url(reply.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        replies = Reply.objects.filter(user=self.user)
        self.assertFalse(replies.exists())
