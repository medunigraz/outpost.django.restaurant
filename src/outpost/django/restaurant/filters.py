from django_filters.rest_framework import FilterSet

from .models import Restaurant


class RestaurantFilter(FilterSet):
    class Meta:
        model = Restaurant
        fields = ("consumers",)
