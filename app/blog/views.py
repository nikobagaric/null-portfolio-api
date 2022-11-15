"""
Views for the blog APIs
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from core.models import (
    Blog,
    Tag,
    Section,
    Comment,
    Reply,
)
from blog import serializers

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seperated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'sections',
                OpenApiTypes.STR,
                description='Comma seperated list of section IDs to filter',
            )
        ]
    )
)
class BlogViewSet(viewsets.ModelViewSet):
    """View for managing auth blog APIs"""
    serializer_class = serializers.BlogDetailSerializer
    queryset = Blog.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _paramts_to_ints(self, qs):
        """Convert a list of strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve posts for users"""
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tags_ids = self._paramts_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for the request, obsolete function"""
        if self.action == 'list':
            return serializers.BlogSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to posts.',
            )
        ]
    )
)
class BaseAttrViewSet(mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(blog__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseAttrViewSet):
    """View for managing tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class SectionViewSet(BaseAttrViewSet):
    """View for managing sections in the database"""
    serializer_class = serializers.SectionSerializer
    queryset = Section.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for the section request"""
        if self.action == 'list':
            return serializers.SectionSerializer
        elif self.action == 'upload_image':
            return serializers.SectionImageSerializer

        return self.serializer_class


class CommentViewSet(BaseAttrViewSet):
    """View for managing comments in the database."""
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()


class ReplyViewSet(BaseAttrViewSet):
    """View for managing replies in the database."""
    serializer_class = serializers.ReplySerializer
    queryset = Reply.objects.all()
