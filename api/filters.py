import django_filters
from django_filters import filters

from .models import Titles


class TitlesFilter(django_filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__slug',
        method='filter_category')
    genre = filters.CharFilter(
        field_name='genre__slug',
        method='filter_genre')
    name = filters.CharFilter(
        field_name='name',
        method='filter_name')

    class Meta:
        model = Titles
        fields = [
            'category',
            'genre',
            'name',
            'year',
        ]

    def filter_category(self, queryset, slug, category):
        return queryset.filter(category__slug=category)

    def filter_genre(self, queryset, slug, genre):
        return queryset.filter(genre__slug__in=genre.split(','))

    def filter_name(self, queryset, slug, name):
        return queryset.filter(name__contains=name)
