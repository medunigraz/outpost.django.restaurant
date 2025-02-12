import json
import logging
from datetime import timedelta
from decimal import Decimal
from typing import List

import bleach
import fastjsonschema
import jmespath
import pluggy
from dateutil.parser import parse
from django.utils.translation import gettext as _
from gql import (
    Client,
    gql,
)
from gql.transport.requests import RequestsHTTPTransport
from outpost.django.base.plugins import Plugin

from . import models

logger = logging.getLogger(__name__)


class RestaurantBehaviourPlugin(Plugin):
    pass


class RestaurantBehaviour(object):

    name = f"{__name__}.RestaurantBehaviour"
    base = RestaurantBehaviourPlugin
    hookspec = pluggy.HookspecMarker(name)
    hookimpl = pluggy.HookimplMarker(name)

    @classmethod
    def manager(cls, condition=lambda _: True):
        pm = pluggy.PluginManager(cls.name)
        pm.add_hookspecs(cls)
        for plugin in cls.base.all():
            if condition(plugin):
                logger.info(f"Registering plugin: {plugin}")
                pm.register(plugin())
        return pm

    @hookspec
    def update(self, restaurant) -> List[dict]:
        """"""

    @hookspec
    def validate(self, restaurant) -> bool:
        """"""


class DebugRestaurantBehaviour(RestaurantBehaviourPlugin):

    name = _("Debugger")

    @RestaurantBehaviour.hookimpl
    def update(self, restaurant):
        logger.debug(f"{self.__class__.__name__}: update({restaurant})")
        return {"id": f"{self.__class__.__name__}:update"}

    @RestaurantBehaviour.hookimpl
    def validate(self, restaurant):
        return True


class MensenRestaurantBehaviour(RestaurantBehaviourPlugin):

    name = _("Mensen")

    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "endpoint": {"type": "string", "minLength": 1},
            "variables": {"type": "object", "additionalProperties": {"type": "string"}},
            "query": {"type": "string", "minLength": 1},
        },
        "required": [
            "endpoint",
            "variables",
            "query",
        ],
    }

    @RestaurantBehaviour.hookimpl
    def update(self, restaurant):
        transport = RequestsHTTPTransport(
            url=restaurant.configuration.get("endpoint"), verify=True
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql(restaurant.configuration.get("query"))
        result = client.execute(
            query, variable_values=restaurant.configuration.get("variables", {})
        )
        for nested in restaurant.configuration.get("nested"):
            data = json.loads(jmespath.search(nested, result))
            first_day = parse(data.get("first_day"))
            for menus in data.get("menus"):
                for offset, values in menus.get("menus").items():
                    day = first_day + timedelta(days=int(offset) - 1)
                    for pos, entry in enumerate(values):
                        foreign = "{day}-{pos}".format(
                            day=day.strftime("%Y-%m-%d"), pos=pos
                        )
                        informations = entry.get("informations")
                        if informations:
                            names = entry.get("informations").keys()
                        else:
                            names = []
                        diet_map = models.DietMap.objects.filter(
                            value__in=names
                        ).first()
                        if diet_map:
                            logger.debug(
                                f"Mapped diet {diet_map} for {restaurant} to values {names}."
                            )
                            diet = diet_map.diet
                        else:
                            logger.debug(
                                f"Could not map diet for {restaurant} to values {names}."
                            )
                            diet = restaurant.default_diet
                        meal, created = restaurant.meals.get_or_create(
                            foreign=foreign,
                            defaults={
                                "available": day,
                                "description": bleach.clean(
                                    " ".join(
                                        entry.get("title_de").replace("\n", " ").split()
                                    ),
                                    strip=True,
                                ),
                                "price": Decimal(entry.get("price")),
                                "diet": diet,
                            },
                        )
                        if created:
                            logger.debug(f"Created new meal {meal} for {restaurant}")
                        else:
                            logger.debug(f"Updated meal {meal} for {restaurant}")

    @RestaurantBehaviour.hookimpl
    def validate(self, restaurant):
        """
        Validate the value of the configuration field against the JSON schema
        of this behaviour.
        """
        try:
            fastjsonschema.validate(self.schema, restaurant.configuration)
        except fastjsonschema.JsonSchemaException:
            logger.warn(f"Incompatible configuration for restaurant {restaurant}")
            return False
        return True
