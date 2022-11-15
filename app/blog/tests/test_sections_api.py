"""
Tests for the sections API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Blog,
    Section,
)

from serializers import (
    SectionImageSerializer,
    SectionSerializer
)


SECTION_URL = reverse('section:section-list')


def detail_url(section_id):
    """Create and return a section detail url"""
    return reverse('blog:section-detail', args=[section_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving sections."""
        res = self.client.get(SECTION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)