"""
Database models
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def section_image_file_path(instance, filename):
    """Generate file path for new section image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'blog', filename)


"""
GLOBAL MODELS
"""

class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_field):
        """Create save and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create save and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

"""
BLOG API MODELS
"""

class Tag(models.Model):
    """Tag model for blog filtering"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Section(models.Model):
    """Section model for blog, the actual content of the post"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    header = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True, upload_to=section_image_file_path, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)

    def __str__(self):
        return self.header


class Blog(models.Model):
    """Blog post model."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, null=True)
    detail = models.CharField(max_length=2000, null=True)
    featured = models.BooleanField(default=False)
    visit_count = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sections = models.ManyToManyField(Section, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model for blog"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    body = models.CharField(max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)


class Reply(models.Model):
    """Reply model for comment"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reply',
    )
    body = models.CharField(max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)
