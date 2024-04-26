import logging

from django.db.models.manager import BaseManager
from django.utils import timezone
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import (
    ListSerializer,
    ManyRelatedField,
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
            return super().to_representation(data.filter(available__gte=today))
        else:
            return super().to_representation([m for m in data if m.available >= today])


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

    @property
    def expandable_fields(self):
        return {
            "meals": (
                f"{self.__class__.__module__}.MealSerializer",
                {"source": "meals", "many": True},
            ),
            "specials": (
                f"{self.__class__.__module__}.SpecialSerializer",
                {"source": "specials", "many": True},
            ),
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


class SpecialSerializer(FlexFieldsModelSerializer):
    """
    ## Expansions

    To activate relation expansion add the desired fields as a comma separated
    list to the `expand` query parameter like this:

        ?expand=<field>,<field>,<field>,...

    The following relational fields can be expanded:

     * `diet`

    """

    class Meta:
        model = models.Special
        fields = "__all__"
