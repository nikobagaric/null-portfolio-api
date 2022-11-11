"""
Serializers for the blog API.
"""
from rest_framework import serializers

from core.models import (
    Blog,
)


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for the blog model."""

    class Meta:
        model = Blog
        fields = [''] #TO DO
        read_only_fields = ['id']