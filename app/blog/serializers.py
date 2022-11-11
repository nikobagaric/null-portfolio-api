"""
Serializers for the blog API.
"""
from rest_framework import serializers

from core.models import (
    Blog,
    Section,
    Tag,
)


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for the blog model."""

    class Meta:
        model = Blog
        fields = [
                'id', 'title', 'detail',
                'featured', 'visit_count',
                'visible', 'created_at',
                ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a blog post"""
        post = Blog.objects.create(**validated_data)

        # todo: add tags and secs

        return post

    def update(self, instance, validated_data):
        """Update a post"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
