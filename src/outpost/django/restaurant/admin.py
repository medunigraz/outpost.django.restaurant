from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from . import models


@admin.register(models.Diet)
class DietAdmin(admin.ModelAdmin):
    pass


class RestaurantChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.Restaurant


@admin.register(models.XMLRestaurant)
class XMLRestaurantAdmin(RestaurantChildAdmin):
    base_model = models.XMLRestaurant


@admin.register(models.Restaurant)
class RestaurantParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.Restaurant
    child_models = (models.Restaurant, models.XMLRestaurant)
    list_filter = (PolymorphicChildModelFilter,)


class BaseExtractorChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.BaseExtractor


@admin.register(models.XSLTExtractor)
class XSLTExtractorAdmin(BaseExtractorChildAdmin):
    base_model = models.XSLTExtractor


@admin.register(models.BaseExtractor)
class BaseExtractorParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.BaseExtractor
    child_models = (models.XSLTExtractor,)
    list_filter = (PolymorphicChildModelFilter,)
