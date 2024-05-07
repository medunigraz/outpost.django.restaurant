from io import BytesIO

import qrcode
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)
from qrcode.image.svg import SvgPathImage

from . import models


@admin.register(models.Diet)
class DietAdmin(admin.ModelAdmin):
    pass


class MealInline(admin.TabularInline):
    model = models.Meal
    exclude = ("foreign",)


class SpecialInline(admin.TabularInline):
    model = models.Special


class RestaurantChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.Restaurant
    inlines = (MealInline,)


@admin.register(models.XMLRestaurant)
class XMLRestaurantAdmin(RestaurantChildAdmin):
    base_model = models.XMLRestaurant


@admin.register(models.ManualRestaurant)
class ManualRestaurantAdmin(RestaurantChildAdmin):
    base_model = models.ManualRestaurant
    inlines = (MealInline, SpecialInline)
    readonly_fields = ("secret", "link", "qrcode")

    def change_view(self, request, *args, **kwargs):
        self.request = request
        return super().change_view(request, *args, **kwargs)

    def link(self, obj):
        url = self.request.build_absolute_uri(
            reverse("restaurant:restaurant", kwargs={"secret": obj.secret})
        )
        return format_html("""<a href="{url}" target="_blank">{url}</a>""", url=url)

    qrcode.short_description = _("Link")

    def qrcode(self, obj):
        b = BytesIO()
        url = self.request.build_absolute_uri(
            reverse("restaurant:restaurant", kwargs={"secret": obj.secret})
        )
        qr = qrcode.make(url, image_factory=SvgPathImage)
        qr.save(b)
        tag = b.getvalue().decode("utf-8")
        b.close()
        return mark_safe(tag)

    qrcode.short_description = _("QR code")


@admin.register(models.Restaurant)
class RestaurantParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.Restaurant
    child_models = (models.Restaurant, models.XMLRestaurant, models.ManualRestaurant)
    list_filter = (PolymorphicChildModelFilter, "enabled")
    list_display = ("name", "enabled")


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


@admin.register(models.Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    pass
