from django.views import View
from django.http import HttpResponse
from django.shortcuts import render

def Test(request):
  return HttpResponse("<p>Testando resposta de template!</p>")
