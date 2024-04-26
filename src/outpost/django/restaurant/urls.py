from django.urls import path

from . import views

app_name = "restaurant"

urlpatterns = [
    path(
        "<str:secret>/special/<int:pk>/delete/",
        views.SpecialDeleteView.as_view(),
        name="special-delete",
    ),
    path(
        "<str:secret>/special/<int:pk>/",
        views.SpecialUpdateView.as_view(),
        name="special-update",
    ),
    path(
        "<str:secret>/special/",
        views.SpecialCreateView.as_view(),
        name="special-create",
    ),
    path(
        "<str:secret>/meal/<int:pk>/delete/",
        views.MealDeleteView.as_view(),
        name="meal-delete",
    ),
    path(
        "<str:secret>/meal/<int:pk>/",
        views.MealUpdateView.as_view(),
        name="meal-update",
    ),
    path("<str:secret>/meal/", views.MealCreateView.as_view(), name="meal-create"),
    path("<str:secret>/", views.RestaurantView.as_view(), name="restaurant"),
]
