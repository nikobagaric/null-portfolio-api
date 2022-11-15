"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)

def create_post(user, **params):
    """Create and return a sample blog post"""
    defaults = {
        'title': 'Sample Text',
        'detail': 'Lorem ipsum dolor sit amet',
        'featured': True,
    }
    defaults.update(params)

    post = models.Blog.objects.create(user=user, **defaults)
    return post


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a new user without email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_post(self):
        """Test creating a new post is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        post = models.Blog.objects.create(
            user=user,
            title='Sample post name',
            detail='Sample post description',
        )

        self.assertEqual(str(post), post.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_section(self):
        """Test creating a section is succesful"""
        user = create_user()
        section = models.Section.objects.create(
            user=user,
            header='Header',
            description='desc',
        )

        self.assertEqual(str(section), section.header)

    def test_create_comment(self):
        """Test creating a comment is succesful"""
        user = create_user()
        post = create_post(user=user)
        models.Comment.objects.create(
            user=user,
            post=post,
            body='sample text',
        )

        self.assertTrue(models.Comment.objects.filter(user=user).exists())

    def test_create_reply(self):
        """Test creating a comment reply is succesful"""
        user = create_user()
        post = create_post(user=user)
        comment = models.Comment.objects.create(
            user=user,
            post=post,
            body='sample text',
        )
        reply = models.Reply.objects.create(
            user=user,
            comment=comment,
            body='sample reply',
        )

        self.assertTrue(models.Reply.objects.filter(user=user).exists())
