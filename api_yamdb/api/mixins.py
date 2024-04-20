from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from api.permissions import IsAdminOrReadOnly


class GetListCreateDeleteViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet,
):
    """ViewSet для методов Get, List, Create, Delete."""

    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)
