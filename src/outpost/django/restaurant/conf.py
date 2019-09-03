from appconf import AppConf
from django.conf import settings


class RestaurantAppConf(AppConf):
    API_URL = "http://localhost/rest/menu/"

    class Meta:
        prefix = "restaurant"
