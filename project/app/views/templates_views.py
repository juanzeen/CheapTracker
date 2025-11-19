from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class BaseAuthTemplateView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    pass


class HomeTemplateView(TemplateView):
    template_name = "cheaptracker/home.html"


class LoginTemplateView(TemplateView):
    template_name = "cheaptracker/login.html"


class RegisterTemplateView(TemplateView):
    template_name = "cheaptracker/register.html"


class DashboardTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/dashboard.html"


class CreatePlaceTemplateView(BaseAuthTemplateView):
    template_name = "cheaptracker/create_place.html"
