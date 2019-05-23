from . import api

v1 = [
    (
        r'restaurant/diet',
        api.DietViewSet,
        'restaurant-diet'
    ),
    (
        r'restaurant/restaurant',
        api.RestaurantViewSet,
        'restaurant-restaurant'
    ),
    (
        r'restaurant/meal',
        api.MealViewSet,
        'restaurant-meal'
    ),
]
