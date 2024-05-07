import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import (
    ArrayField,
    HStoreField,
)
from django.template import (
    Context,
    Template,
)
from django.utils import timezone
from outpost.django.api.models import Consumer
from outpost.django.base.utils import Uuid4Upload
from polymorphic.models import PolymorphicModel
from shortuuid.django_fields import ShortUUIDField

logger = logging.getLogger(__name__)


class Diet(models.Model):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key.

    ### `name` (`string`)
    Name of diet.
    """

    name = models.CharField(max_length=128)
    foreign = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Restaurant(PolymorphicModel):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key.

    ### `name` (`string`)
    Name of doctoral school.

    ### `address` (`string`)
    Street address.

    ### `zipcode` (`string`)
    Zip code.

    ### `city` (`string`)
    City.

    ### `phone` (`string`)
    Phone.

    ### `email` (`string`)
    Email address.

    ### `url` (`string`)
    Homepage URL.

    ### `position` (`Object`)
    Location of restaurant on map as [GeoJSON](http://geojson.org/).
    """

    name = models.CharField(max_length=128)
    foreign = models.CharField(
        max_length=256, blank=True, null=True, unique=True, db_index=True
    )
    address = models.CharField(max_length=128)
    zipcode = models.CharField(max_length=16)
    city = models.CharField(max_length=128)
    phone = models.CharField(max_length=64)
    email = models.EmailField()
    url = models.URLField(blank=True, null=True)
    position = models.PointField(
        blank=True, null=True, db_index=True, srid=settings.DEFAULT_SRID
    )
    enabled = models.BooleanField(default=False)
    consumers = models.ManyToManyField(Consumer, related_name="+")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class BaseExtractor(PolymorphicModel):
    name = models.CharField(max_length=128)
    dateformat = models.CharField(max_length=64)

    def extract(self, rest):
        pass

    def __str__(self):
        return self.name


class XSLTExtractor(BaseExtractor):
    xslt = models.TextField()

    def extract(self, rest):
        pass


class XMLRestaurant(Restaurant):
    source_template = models.TextField()
    extractor = models.ForeignKey("BaseExtractor", on_delete=models.CASCADE)
    normalize = models.BooleanField(default=False)
    decompose = ArrayField(models.CharField(max_length=256), blank=True)
    headers = HStoreField(blank=True)

    @property
    def source(self):
        context = Context({"restaurant": self})
        return Template(self.source_template).render(context)


class ManualRestaurant(Restaurant):
    secret = ShortUUIDField(length=16, max_length=16)


class MealManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(available__gte=timezone.now())


class Meal(models.Model):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key.

    ### `description` (`string`)
    Description of meal.

    ### `restaurant` (`integer` or `Object`)
    Foreign key to [Restaurant](../restaurant) this meal is served at.

    ### `price` (`number`)
    Price of meal.

    ### `diet` (`integer` or `Object`)
    Foreign key to [Diet](../diet) this meal is conformant with.
    """

    foreign = models.CharField(max_length=256, blank=True, null=True)
    restaurant = models.ForeignKey(
        "Restaurant", related_name="meals", on_delete=models.CASCADE
    )
    available = models.DateField()
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    diet = models.ForeignKey("Diet", blank=True, null=True, on_delete=models.SET_NULL)

    active = MealManager()
    objects = models.Manager()

    def __str__(self):
        return self.description


class SpecialManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(end__gte=timezone.now())


class Special(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="specials"
    )
    start = models.DateField()
    end = models.DateField()
    document = models.FileField(upload_to=Uuid4Upload, null=True, blank=True)
    description = models.TextField()

    active = SpecialManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.restaurant}: {self.start} - {self.end}"
