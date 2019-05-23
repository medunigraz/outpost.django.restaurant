import logging

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField

from . import models

logger = logging.getLogger(__name__)


class DietSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = models.Diet
        exclude = (
            'foreign',
        )


class RestaurantSerializer(FlexFieldsModelSerializer):
    '''
    ## Expansions

    To activate relation expansion add the desired fields as a comma separated
    list to the `expand` query parameter like this:

        ?expand=<field>,<field>,<field>,...

    The following relational fields can be expanded:

     * `meals`

    '''
    meals = PrimaryKeyRelatedField(many=True, read_only=True)
    expandable_fields = {
        'meals': (
            'outpost.django.restaurant.serializers.MealSerializer',
            {
                'source': 'meals',
                'many': True,
            }
        ),
    }

    class Meta:
        model = models.Restaurant
        exclude = (
            'foreign',
            'enabled',
            'polymorphic_ctype',
        )


class MealSerializer(FlexFieldsModelSerializer):
    '''
    ## Expansions

    To activate relation expansion add the desired fields as a comma separated
    list to the `expand` query parameter like this:

        ?expand=<field>,<field>,<field>,...

    The following relational fields can be expanded:

     * `diet`

    '''
    expandable_fields = {
        'diet': (
            DietSerializer,
            {
                'source': 'diet',
            }
        ),
        'restaurant': (
            RestaurantSerializer,
            {
                'source': 'restaurant',
            }
        ),
    }

    class Meta:
        model = models.Meal
        exclude = (
            'foreign',
        )
