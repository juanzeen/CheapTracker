from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse


class BaseAuthTemplateView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    pass


class HomeTemplateView(TemplateView):
    template_name = "cheaptracker/home.html"


class LoginTemplateView(TemplateView):
    template_name = "cheaptracker/login.html"


class RegisterTemplateView(TemplateView):
    template_name = "cheaptracker/register.html"


class UserDashboardTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/dashboard.html"


class CreatePlaceTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/create_place.html"


class PlaceDashboardTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/place_dashboard.html"

class CreateOrderTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/create_order.html"

class OrderDetailsTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/order_details.html"

class CreateTruckTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/create_truck.html"

class SwaggerUIView(TemplateView):
    template_name = "cheaptracker/swagger-ui.html"


def openapi_yaml_view(request):
    from django.conf import settings
    import os

    yaml_file_path = os.path.join(settings.BASE_DIR.parent, "openapi.yaml")
    with open(yaml_file_path, "r") as f:
        content = f.read()
    return HttpResponse(content, content_type="application/x-yaml")
