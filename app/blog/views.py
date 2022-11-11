"""
Views for the blog APIs
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models import (
    Blog,
)
from blog import serializers

from rest_framework import (
    viewsets,
    # mixins,
    # status,
)

"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
"""
# from rest_framework.decorators import action
# from rest_framework.response import Response


class BlogViewSet(viewsets.ModelViewSet):
    """View for managing auth blog APIs"""
    serializer_class = serializers.BlogSerializer
    queryset = Blog.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _paramts_to_ints(self, qs):
        """Convert a list of strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve posts for users"""
        queryset = self.queryset

        return queryset.filter().order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for the request"""
        if self.action == 'list':
            return serializers.BlogSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
