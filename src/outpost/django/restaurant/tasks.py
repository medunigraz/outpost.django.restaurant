import json
import logging
from collections import defaultdict
from datetime import (
    datetime,
    timedelta,
)
from decimal import (
    Decimal,
    InvalidOperation,
)
from email.utils import parsedate_to_datetime
from functools import reduce
from hashlib import sha256

import requests
from celery.task import PeriodicTask
from django.conf import settings
from django.contrib.gis.geos import Point
from django.template import (
    Context,
    Template,
)
from django.utils import timezone
from lxml import etree
from requests.exceptions import RequestException

from . import models

logger = logging.getLogger(__name__)


class RestaurantSyncTask(PeriodicTask):
    run_every = timedelta(hours=2)

    def run(self, **kwargs):
        today = timezone.localdate()
        self.json()
        self.xml()
        logger.debug(f'Removing meals not available today: {today}')
        models.Meal.objects.exclude(available=today).delete()

    def json(self):
        today = timezone.localdate()
        url = settings.OUTPOST.get('restaurants')
        if not url:
            logger.debug('No URL for restaurant sync defined, skipping.')
            return
        try:
            req = requests.get(
                url,
                headers={
                    'Accept': 'application/json',
                }
            )
            req.raise_for_status()
        except RequestException as e:
            logger.warn(f'Could not fetch restaurant data: {e}')
            return
        menu = req.json().get('menu')
        if not menu:
            logger.warn('No "menu" attribute found in restaurant data.')
            return
        date = parsedate_to_datetime(menu.get('date'))
        if date:
            logger.debug(f'Processing restaurant menu from {date}')
        diets = {}
        for foreign, name in menu.get('diet', {}).items():
            obj, created = models.Diet.objects.update_or_create(
                foreign=int(foreign),
                defaults={
                    'foreign': int(foreign),
                    'name': name,
                }
            )
            if created:
                logger.info(f'Created new diet: {obj}')
            diets[int(foreign)] = obj
        geo = settings.GEORESOLVERS
        for data in menu.get('restaurants', {}):
            query = {
                'street': data.get('address'),
                'city': data.get('city'),
                'country': 'Austria',  # TODO: No hardcoded country ... find a way to autolocate
                'postalcode': data.get('zip'),
            }
            locate = reduce(lambda a, r: a or r.geocode(query), geo, None)
            if locate:
                logger.debug(f'Gelocated at {locate}')
                position = Point(
                    locate.longitude,
                    locate.latitude,
                    srid=4326
                )
            else:
                logger.info(f'No geolocation for {query}')
                position = None
            rest, created = models.Restaurant.objects.update_or_create(
                foreign=int(data.get('uid')),
                defaults={
                    'foreign': int(data.get('uid')),
                    'name': data.get('company'),
                    'address': data.get('address'),
                    'zipcode': data.get('zip'),
                    'city': data.get('city'),
                    'phone': data.get('telephone'),
                    'email': data.get('email'),
                    'url': data.get('www') or None,
                    'position': position,
                }
            )
            if created:
                logger.info(f'Created new restaurant: {rest}')
            else:
                logger.debug(f'Updated restaurant: {rest}')
            for meal in data.get('meals', {}):
                available = parsedate_to_datetime(meal.get('date'))
                if today != available.date():
                    continue
                obj, created = models.Meal.objects.update_or_create(
                    foreign=meal.get('uid'),
                    defaults={
                        'foreign': meal.get('uid'),
                        'restaurant': rest,
                        'available': available,
                        'description': meal.get('description'),
                        'price': Decimal(meal.get('price')),
                        'diet': diets.get(meal.get('diet')),
                    }
                )
                if created:
                    logger.info(f'Created new meal: {obj}')
                else:
                    logger.debug(f'Updated meal: {obj}')

    def xml(self):
        today = timezone.localdate()
        for xrest in models.XMLRestaurant.objects.filter(enabled=True):
            logger.debug(f'Processing {xrest}')
            try:
                req = requests.get(
                    xrest.source,
                    headers={
                        'Accept': 'text/xml',
                    }
                )
                req.raise_for_status()
            except RequestException as e:
                logger.warn(f'Could not fetch restaurant data: {e}')
                return
            doc = etree.XML(req.text)
            context = Context({
                'restaurant': xrest,
            })
            xslt = Template(xrest.extractor.xslt).render(context)
            transformer = etree.XSLT(etree.XML(xslt))
            data = transformer(doc)
            for meal in json.loads(str(data)):
                values = defaultdict(lambda: None)
                values.update(meal)
                if 'available' in meal:
                    values['available'] = datetime.strptime(
                        meal.get('available'),
                        xrest.extractor.dateformat
                    ).date()
                    if values['available'] != today:
                        continue
                else:
                    values['available'] = today
                if 'foreign' not in meal:
                    logger.info(f'No foreign key data found: {meal}')
                    continue
                hashkey = meal.get('foreign').encode('utf-8')
                values['foreign'] = sha256(hashkey).hexdigest()
                if meal.get('price'):
                    try:
                        values['price'] = Decimal(meal.get('price'))
                    except InvalidOperation as e:
                        logger.info(f'Could not convert to Decimal: {e}')
                        values['price'] = None
                if meal.get('diet'):
                    try:
                        diet_pk = int(meal.get('diet'))
                    except ValueError as e:
                        logger.info(f'Could not convert diet primary key: {e}')
                    else:
                        try:
                            values['diet'] = models.Diet.objects.get(pk=diet_pk)
                        except models.Diet.DoesNotExist:
                            logger.info(f'Diet not found: {diet_pk}')
                            values['diet'] = None
                values['restaurant'] = xrest
                obj, created = models.Meal.objects.update_or_create(
                    foreign=values['foreign'],
                    defaults=values
                )
                if created:
                    logger.info(f'Created new meal: {obj}')
                else:
                    logger.debug(f'Updated meal: {obj}')
