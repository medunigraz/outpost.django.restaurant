from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_gis.filters import DistanceToPointFilter

from outpost.django.base.decorators import docstring_format

# from rest_framework_extensions.mixins import (
#     CacheResponseAndETAGMixin,
# )
# from rest_framework_extensions.cache.mixins import (
#     CacheResponseMixin,
# )
from . import (
    models,
    serializers,
)


@docstring_format(
    model=models.Diet.__doc__,
    serializer=serializers.DietSerializer.__doc__
)
class DietViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    '''
    List restaurants.

    {model}
    {serializer}
    '''
    queryset = models.Diet.objects.all()
    serializer_class = serializers.DietSerializer
    permission_classes = (
        IsAuthenticated,
    )
    permit_list_expands = (
        'meals',
    )


@docstring_format(
    model=models.Restaurant.__doc__,
    serializer=serializers.RestaurantSerializer.__doc__
)
class RestaurantViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    '''
    List restaurants.

    {model}
    {serializer}
    '''
    queryset = models.Restaurant.objects.filter(enabled=True)
    serializer_class = serializers.RestaurantSerializer
    permission_classes = (
        IsAuthenticated,
    )
    distance_filter_field = 'position'
    filter_backends = (
        DistanceToPointFilter,
    )
    bbox_filter_include_overlapping = True
    permit_list_expands = (
        'meals',
        'meals.diet',
    )


@docstring_format(
    model=models.Meal.__doc__,
    serializer=serializers.MealSerializer.__doc__
)
class MealViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    '''
    List restaurants.

    {model}
    {serializer}
    '''
    queryset = models.Meal.objects.all()
    serializer_class = serializers.MealSerializer
    permission_classes = (
        IsAuthenticated,
    )
    permit_list_expands = (
        'restaurant',
        'diet',
    )
