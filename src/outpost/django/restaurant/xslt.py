from datetime import (
    date,
    timedelta,
)

from lxml import etree


class RestaurantExtension:
    def weekday(self, _, arg):
        wd = int(arg) - 1
        td = timedelta(days=wd - date.today().weekday())
        return str(date.today() + td)


extensions = etree.Extension(RestaurantExtension(), ns="restaurant")
