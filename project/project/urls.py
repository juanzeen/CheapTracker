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
    DefineTripAPIView
)

from app.views.api.truck_views import TrucksApiView, TruckApiView
from app.views.api.trip_view import (
    TripsAPIView,
    TripAPIView,
    TripsByStatusAPIView,
    TripsRemainingDeliveriesAPIView,
    StartTripsAPIView,
    EndTripAPIView,
    SimulateTripAPIView,
    CancelTripAPIView,
    ConfirmDeliveryInTripAPIView,
)

from app.views.api.order_views import (
    OrdersApiView,
    OrderApiView,
    PendentOrdersView,
    OrdersByStoreView,
    OrdersByTripView,
    AddBoxView,
    RemoveBoxView,
)
from app.views.templates_views import (
    HomeTemplateView,
    LoginTemplateView,
    RegisterTemplateView,
    DashboardTemplateView,
    CreatePlaceTemplateView,
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
    # auth routes
    path("api/auth/login", LoginView.as_view(), name="Login Route"),
    path("api/auth/logout", LogoutView.as_view(), name="Logout Route"),
    # addressess routes
    path("api/addresses", AddressesAPIView.as_view(), name="Address Create Route"),
    path("api/address/<int:id>", AddressAPIView.as_view(), name="Address Detail Route"),
    # stores routes
    path("api/stores", StoresApiView.as_view(), name="Stores Route"),
    path("api/store/<int:id>", StoreApiView.as_view(), name="Store Route"),
    path(
        "api/store/<int:id>/orders",
        OrdersByStoreView.as_view(),
        name="Orders By Store Route",
    ),
    # depots routes
    path("api/depots", DepotsApiView.as_view(), name="Depots Route"),
    path("api/depots/<int:id>", DepotApiView.as_view(), name="Depot Route"),
    path(
        "api/depots/<int:id>/define-trip",
        DefineTripAPIView.as_view(),
        name="Depot Define Trip Route",
    ),
    # carrier routes
    path("api/carriers", CarriersApiView.as_view(), name="Carriers Route"),
    path("api/carriers/<int:id>", CarrierApiView.as_view(), name="Carrier Route"),
    # truck routes
    path("api/trucks", TrucksApiView.as_view(), name="Trucks Route"),
    path("api/truck/<str:plate>", TruckApiView.as_view(), name="Truck Route"),
    # order routes
    path("api/orders", OrdersApiView.as_view(), name="Orders Route"),
    path(
        "api/pendent-orders", PendentOrdersView.as_view(), name="Pendent Orders Route"
    ),
    path("api/orders", OrdersApiView.as_view(), name="Orders Route"),
    path("api/order/<int:id>", OrderApiView.as_view(), name="Order Route"),
    path(
        "api/order/<int:id>/add-box", AddBoxView.as_view(), name="Order Add Box Route"
    ),
    path(
        "api/order/<int:id>/remove-box",
        RemoveBoxView.as_view(),
        name="Order Remove Box Route",
    ),
    # trip routes
    path("api/trips", TripsAPIView.as_view(), name="Trips Route"),
    path(
        "api/filtered-trips", TripsByStatusAPIView.as_view(), name="Filtered Trip Route"
    ),
    path("api/trip/<int:id>", TripAPIView.as_view(), name="Trip Route"),
    path(
        "api/trip/<int:id>/remaining-deliveries",
        TripsRemainingDeliveriesAPIView.as_view(),
        name="Remaining Deliveries Route",
    ),
    path(
        "api/trip/<int:id>/start", StartTripsAPIView.as_view(), name="Start Trip Route"
    ),
    path("api/trip/<int:id>/end", EndTripAPIView.as_view(), name="End Trip Route"),
    path(
        "api/trip/<int:id>/simulate",
        SimulateTripAPIView.as_view(),
        name="Simulate Trip Route",
    ),
    path(
        "api/trip/<int:id>/cancel-trip",
        CancelTripAPIView.as_view(),
        name="Simulate Trip Route",
    ),
    path(
        "api/trip/<int:trip_id>/confirm-delivery/<int:delivery_id>",
        ConfirmDeliveryInTripAPIView.as_view(),
        name="Simulate Trip Route",
    ),
    path(
        "api/trip/<int:id>/orders",
        OrdersByTripView.as_view(),
        name="Orders By Trip Route",
    ),
    # delivery routes
    # Front-end Views
    path("", HomeTemplateView.as_view(), name="View com template test"),
    path("login", LoginTemplateView.as_view(), name="Login View"),
    path("register", RegisterTemplateView.as_view(), name="Register View"),
    path("dashboard", DashboardTemplateView.as_view(), name="Dashboard View"),
    path("create-place", CreatePlaceTemplateView.as_view(), name="Create Place View"),
]
