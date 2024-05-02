from crispy_forms.bootstrap import (
    AppendedText,
    FormActions,
    PrependedText,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy as reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from outpost.django.base.layout import (
    IconButton,
    LinkIconButton,
)

from .models import (
    ManualRestaurant,
    Meal,
    Special,
)


class RestaurantView(DetailView):
    model = ManualRestaurant
    slug_field = "secret"
    slug_url_kwarg = "secret"


class RestaurantMixin:
    def dispatch(self, request, *args, **kwargs):
        self.restaurant = get_object_or_404(
            ManualRestaurant, secret=self.kwargs.get("secret")
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "restaurant:restaurant", kwargs={"secret": self.restaurant.secret}
        )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(restaurant=self.restaurant)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{"restaurant": self.restaurant})

    def form_valid(self, form):
        form.instance.restaurant = self.restaurant
        return super().form_valid(form)


class FormHelperMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_action = "."
        form.helper.form_class = "form-horizontal"
        form.helper.use_custom_control = True
        form.helper.layout = self.get_layout()
        return form


class MealMixin:
    model = Meal
    fields = (
        "available",
        "description",
        "price",
        "diet",
    )

    def get_layout(self):
        return Layout(
            PrependedText(
                "available",
                mark_safe("""<i class="fa fa-calendar" aria-hidden="true"></i>"""),
            ),
            Field("description"),
            AppendedText("price", "€"),
            Field("diet"),
            FormActions(
                IconButton(
                    "fa fa-paper-plane-o",
                    _("Save changes"),
                    type="submit",
                    css_class="btn-block btn-success",
                ),
                LinkIconButton(
                    reverse(
                        "restaurant:restaurant",
                        kwargs={"secret": self.restaurant.secret},
                    ),
                    "fa fa-arrow-circle-o-left",
                    _("Cancel"),
                    css_class="btn btn-block btn-secondary",
                ),
            ),
        )


class MealCreateView(MealMixin, FormHelperMixin, RestaurantMixin, CreateView):
    def get_initial(self):
        return {"available": timezone.localdate() + timezone.timedelta(days=1)}


class MealUpdateView(MealMixin, FormHelperMixin, RestaurantMixin, UpdateView):
    pass


class MealDeleteView(MealMixin, FormHelperMixin, RestaurantMixin, DeleteView):
    template_name = "restaurant/confirm_delete.html"


class SpecialMixin:
    model = Special
    fields = (
        "start",
        "end",
        "document",
        "description",
    )

    def get_layout(self):
        return Layout(
            PrependedText(
                "start",
                mark_safe("""<i class="fa fa-calendar" aria-hidden="true"></i>"""),
            ),
            PrependedText(
                "end",
                mark_safe("""<i class="fa fa-calendar" aria-hidden="true"></i>"""),
            ),
            Field("document"),
            Field("description"),
            FormActions(
                IconButton(
                    "fa fa-paper-plane-o",
                    _("Save changes"),
                    type="submit",
                    css_class="btn-block btn-success",
                ),
                LinkIconButton(
                    reverse(
                        "restaurant:restaurant",
                        kwargs={"secret": self.restaurant.secret},
                    ),
                    "fa fa-arrow-circle-o-left",
                    _("Cancel"),
                    css_class="btn btn-block btn-secondary",
                ),
            ),
        )


class SpecialCreateView(SpecialMixin, FormHelperMixin, RestaurantMixin, CreateView):
    def get_initial(self):
        return {"start": timezone.localdate() + timezone.timedelta(days=1)}


class SpecialUpdateView(SpecialMixin, FormHelperMixin, RestaurantMixin, UpdateView):
    pass


class SpecialDeleteView(SpecialMixin, FormHelperMixin, RestaurantMixin, DeleteView):
    template_name = "restaurant/confirm_delete.html"
