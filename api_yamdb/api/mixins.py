from rest_framework import filters
from rest_framework import mixins, viewsets

from api.paginators import StandardResultsSetPagination
from api.permissions import IsAdminOrReadOnly


class ListCreateDestroyMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = StandardResultsSetPagination
