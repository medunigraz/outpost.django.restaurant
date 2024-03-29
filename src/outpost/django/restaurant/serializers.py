import logging

from django.db.models.manager import BaseManager
from django.utils import timezone
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import (
    ListSerializer,
    ManyRelatedField,
    PrimaryKeyRelatedField,
)

from . import models

logger = logging.getLogger(__name__)


class DietSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = models.Diet
        exclude = ("foreign",)


class TodayMealsListSerializer(ListSerializer):
    def to_representation(self, data):
        today = timezone.localdate()
        if isinstance(data, BaseManager):
            return super().to_representation(data.filter(available=today))
        else:
            return super().to_representation([m for m in data if m.available == today])


class TodayMealsField(ManyRelatedField):
    def get_attribute(self, instance):
        today = timezone.localdate()
        queryset = super().get_attribute(instance)
        return queryset.filter(available=today)


class RestaurantSerializer(FlexFieldsModelSerializer):
    """
    ## Expansions

    To activate relation expansion add the desired fields as a comma separated
    list to the `expand` query parameter like this:

        ?expand=<field>,<field>,<field>,...

    The following relational fields can be expanded:

     * `meals`

    """

    meals = TodayMealsField(
        child_relation=PrimaryKeyRelatedField(read_only=True), read_only=True
    )
    expandable_fields = {
        "meals": (
            "outpost.django.restaurant.serializers.MealSerializer",
            {"source": "meals", "many": True},
        )
    }

    class Meta:
        model = models.Restaurant
        exclude = ("foreign", "enabled", "polymorphic_ctype")


class MealSerializer(FlexFieldsModelSerializer):
    """
    ## Expansions

    To activate relation expansion add the desired fields as a comma separated
    list to the `expand` query parameter like this:

        ?expand=<field>,<field>,<field>,...

    The following relational fields can be expanded:

     * `diet`

    """

    expandable_fields = {
        "diet": (DietSerializer, {"source": "diet"}),
        "restaurant": (RestaurantSerializer, {"source": "restaurant"}),
    }

    class Meta:
        model = models.Meal
        exclude = ("foreign",)
        list_serializer_class = TodayMealsListSerializer
