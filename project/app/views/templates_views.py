from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render

class BaseAuthTemplateView(TemplateView, LoginRequiredMixin):
  login_url = '/login/'
  pass

class HomeTemplateView(TemplateView):
  template_name = 'cheaptracker/home.html'

class LoginTemplateView(TemplateView):
  template_name = 'cheaptracker/login.html'

class RegisterTemplateView(TemplateView):
  template_name = 'cheaptracker/register.html'

class DashboardTemplateView(TemplateView):
  template_name = 'cheaptracker/dashboard.html'
