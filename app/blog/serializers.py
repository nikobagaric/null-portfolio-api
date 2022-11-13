"""
Serializers for the blog API.
"""
from rest_framework import serializers

from core.models import (
    Blog,
    Section,
    Tag,
    Comment,
    Reply,
)


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for sections."""

    class Meta:
        model = Section
        fields = ['id', 'header', 'description']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for the blog model."""
    tags = TagSerializer(many=True, required=False)
    sections = SectionSerializer(many=True, required=False)

    class Meta:
        model = Blog
        fields = [
                'id', 'title', 'detail',
                'featured', 'visit_count',
                'visible', 'created_at',
                'tags', 'sections'
                ]
        read_only_fields = ['id', 'created_at']

    def _get_or_create_tags(self, tags, post):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            post.tags.add(tag_obj)

    def _get_or_create_sections(self, sections, post):
        """Handle getting or creating sections as needed"""
        auth_user = self.context['request'].user
        for section in sections:
            section_obj, created = Section.objects.get_or_create(
                user=auth_user,
                **section,
            )
            post.sections.add(section_obj)

    def create(self, validated_data):
        """Create a blog post"""
        tags = validated_data.pop('tags', [])
        sections = validated_data.pop('sections', [])
        post = Blog.objects.create(**validated_data)
        self._get_or_create_tags(tags, post)
        self._get_or_create_sections(sections, post)

        return post

    def update(self, instance, validated_data):
        """Update a post"""
        tags = validated_data.pop('tags', None)
        sections = validated_data.pop('sections', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if sections is not None:
            instance.sections.clear()
            self._get_or_create_sections(sections, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BlogDetailSerializer(BlogSerializer):
    """Detailed blog (to-do)"""

    class Meta(BlogSerializer.Meta):
        fields = BlogSerializer.Meta.fields

class SectionImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to a section"""

    class Meta:
        model = Section
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'False'}}


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""

    class Meta:
        model = Comment
        fields = ['id', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReplySerializer(serializers.ModelSerializer):
    """Serializer for replies"""

    class Meta:
        model = Reply
        fields = ['id', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']
