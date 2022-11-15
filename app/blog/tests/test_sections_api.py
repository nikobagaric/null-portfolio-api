"""
Tests for the sections API
"""
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Blog,
    Section,
)

from blog.serializers import (
    SectionSerializer
)


SECTIONS_URL = reverse('blog:section-list')


def detail_url(section_id):
    """Create and return a section detail url"""
    return reverse('blog:section-detail', args=[section_id])


def image_upload_url(section_id):
    """Create and return an image upload URL"""
    return reverse('blog:section-upload-image', args=[section_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_section(user, **params):
    """Sample section"""
    default = {
        'header': 'Sample Header',
        'description': 'Lorem ipsum dolor sit amet consectur it',
    }
    default.update(params)

    section = Section.objects.create(user=user, **default)
    return section


class PublicSectionApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving sections."""
        res = self.client.post(SECTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSectionAPITests(TestCase):
    """Test authenticated section API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_sections(self):
        """Test retrieving a list of sections"""
        Section.objects.create(user=self.user, header='Header 1')
        Section.objects.create(user=self.user, header='Header 2')

        res = self.client.get(SECTIONS_URL)

        sections = Section.objects.all().order_by('-header')
        serializer = SectionSerializer(sections, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_section(self):
        """Test updating a section"""
        section = Section.objects.create(user=self.user, header='Header 1')

        payload = {'header': 'Header 2'}
        url = detail_url(section.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        section.refresh_from_db()
        self.assertEqual(section.header, payload['header'])

    def test_delete_section(self):
        """Test deleting a section"""
        section = Section.objects.create(user=self.user, header='Header 1')

        url = detail_url(section.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        sections = Section.objects.filter(user=self.user)
        self.assertFalse(sections.exists())

    def test_filter_sections_assigned_to_post(self):
        """Test listing sections by those assigned to a specific blog post"""
        sec1 = Section.objects.create(user=self.user, header='Header 1')
        sec2 = Section.objects.create(user=self.user, header='Header 2')
        post = Blog.objects.create(
            user=self.user,
            title='Post',
            detail='Post about sections',
        )
        post.sections.add(sec1)

        res = self.client.get(SECTIONS_URL, {'assigned_only': 1})

        s1 = SectionSerializer(sec1)
        s2 = SectionSerializer(sec2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtering_sections_returns_unique_list(self):
        """Test filtering a post's sections returns a unique list to the blog post"""
        sec1 = Section.objects.create(user=self.user, header='Header 1')
        Section.objects.create(user=self.user, header='Header 2')
        post1 = Blog.objects.create(
            user=self.user,
            title='Post 1',
            detail='Post 1 about sections',
        )
        post2 = Blog.objects.create(
            user=self.user,
            title='Post 2',
            detail='Post 2 about sections',
        )
        post1.sections.add(sec1)
        post2.sections.add(sec1)

        res = self.client.get(SECTIONS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)


class ImageUploadTests(TestCase):
    """Test uploading an image to the API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)
        self.section = create_section(user=self.user)

    def tearDown(self):
        self.section.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.section.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.section.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.section.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid file"""
        url = image_upload_url(self.section.id)
        payload = {'image': 'defo not an img'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
