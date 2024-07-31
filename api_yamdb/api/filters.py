from django_filters import FilterSet, filters

from reviews.models import Title


class TitleFilter(FilterSet):
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'

    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
