from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render

class BaseAuthTemplateView(TemplateView, LoginRequiredMixin):
  login_url = '/login/'
  pass

class HomeView(TemplateView):
  template_name = 'cheaptracker/home.html'
