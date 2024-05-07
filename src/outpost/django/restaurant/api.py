from django_filters.rest_framework import DjangoFilterBackend
from outpost.django.base.decorators import docstring_format
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_gis.filters import DistanceToPointFilter

# from rest_framework_extensions.mixins import (
#     CacheResponseAndETAGMixin,
# )
# from rest_framework_extensions.cache.mixins import (
#     CacheResponseMixin,
# )
from . import (
    filters,
    models,
    serializers,
)


@docstring_format(
    model=models.Diet.__doc__, serializer=serializers.DietSerializer.__doc__
)
class DietViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    """
    List restaurants.

    {model}
    {serializer}
    """

    queryset = models.Diet.objects.all()
    serializer_class = serializers.DietSerializer
    permission_classes = (IsAuthenticated,)
    permit_list_expands = ("meals",)


@docstring_format(
    model=models.Restaurant.__doc__, serializer=serializers.RestaurantSerializer.__doc__
)
class RestaurantViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    """
    List restaurants.

    {model}
    {serializer}
    """

    queryset = models.Restaurant.objects.filter(enabled=True)
    serializer_class = serializers.RestaurantSerializer
    permission_classes = (IsAuthenticated,)
    distance_filter_field = "position"
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter)
    filterset_class = filters.RestaurantFilter
    bbox_filter_include_overlapping = True
    permit_list_expands = ("meals", "meals.diet")


@docstring_format(
    model=models.Meal.__doc__, serializer=serializers.MealSerializer.__doc__
)
class MealViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    """
    List restaurants.

    {model}
    {serializer}
    """

    queryset = models.Meal.active.all()
    serializer_class = serializers.MealSerializer
    permission_classes = (IsAuthenticated,)
    permit_list_expands = ("restaurant", "diet")


@docstring_format(
    model=models.Special.__doc__, serializer=serializers.SpecialSerializer.__doc__
)
class SpecialViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    """
    List specials.

    {model}
    {serializer}
    """

    queryset = models.Special.active.all()
    serializer_class = serializers.SpecialSerializer
    permission_classes = (IsAuthenticated,)
    permit_list_expands = ("restaurant",)
