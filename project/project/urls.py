from app.views.api_views import UsersAPIView, UserAPIView, ChangePasswordView, LoginView, LogoutView
from app.views.templates_views import HomeView


"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', UsersAPIView.as_view(), name = 'Users Routes'),
    path('api/users/<str:email>', UserAPIView.as_view(), name = 'User Route'),
    path('api/users/change-password/<str:email>', ChangePasswordView.as_view(), name = 'Change Password Route'),
    path('api/auth/login', LoginView.as_view(), name = 'Login Route'),
    path('api/auth/logout', LogoutView.as_view(), name = 'Logout Route'),
    path('', HomeView.as_view(), name = "View com template test")
    ]
