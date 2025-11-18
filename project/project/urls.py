from app.views.api.user_views import (
    UsersAPIView,
    UserAPIView,
    ChangePasswordView,
    LoginView,
    LogoutView,
)
from app.views.api.places_views import (
    AddressesAPIView,
    AddressAPIView,
    StoresApiView,
    StoreApiView,
    DepotsApiView,
    DepotApiView,
    CarrierApiView,
    CarriersApiView,
)
from app.views.templates_views import (
    HomeTemplateView,
    LoginTemplateView,
    RegisterTemplateView,
    DashboardTemplateView,
)
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # API routes
    path("admin/", admin.site.urls),
    path("api/users", UsersAPIView.as_view(), name="Users Routes"),
    path("api/users/<str:email>", UserAPIView.as_view(), name="User Route"),
    path(
        "api/users/change-password/<str:email>",
        ChangePasswordView.as_view(),
        name="Change Password Route",
    ),
    path("api/auth/login", LoginView.as_view(), name="Login Route"),
    path("api/auth/logout", LogoutView.as_view(), name="Logout Route"),
    path("api/addresses", AddressesAPIView.as_view(), name="Address Create Route"),
    path("api/address/<int:id>", AddressAPIView.as_view(), name="Address Detail Route"),
    path("api/stores", StoresApiView.as_view(), name="Stores Route"),
    path("api/stores/<int:id>", StoreApiView.as_view(), name="Store Route"),
    path("api/depots", DepotsApiView.as_view(), name="Depots Route"),
    path("api/depots/<int:id>", DepotApiView.as_view(), name="Depot Route"),
    path("api/carriers", CarriersApiView.as_view(), name="Carriers Route"),
    path("api/carriers/<int:id>", CarrierApiView.as_view(), name="Carrier Route"),
    path("api/orders", CarrierApiView.as_view(), name="Orders Route"),
    path("api/order/<int:id>", CarrierApiView.as_view(), name="Order Route"),
    # Front-end Views
    path("", HomeTemplateView.as_view(), name="View com template test"),
    path("login", LoginTemplateView.as_view(), name="Login View"),
    path("register", RegisterTemplateView.as_view(), name="Register View"),
    path("dashboard", DashboardTemplateView.as_view(), name="Dashboard View"),
]
