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
    DefineTripAPIView,
    TripsByDepotAPIView,
)

from app.views.api.truck_views import TrucksApiView, TruckApiView, TruckByCarrierApiView

from app.views.api.trip_views import (
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
    BoxesFromOrderView,
    AddBoxView,
    RemoveBoxView,
)
from app.views.templates_views import (
    HomeTemplateView,
    LoginTemplateView,
    RegisterTemplateView,
    UserDashboardTemplateView,
    CreatePlaceTemplateView,
    PlaceDashboardTemplateView,
    CreateOrderTemplateView,
    OrderDetailsTemplateView,
    AddBoxTemplateView,
    RemoveBoxTemplateView,
    CreateTruckTemplateView,
    TruckDetailsTemplateView,
    TripDetailsTemplateView,
    CreateTripTemplateView,
    StartTripTemplateView,
    SimulateTripTemplateView,
    SwaggerUIView,
    openapi_yaml_view,
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
    path("api/depot/<int:id>", DepotApiView.as_view(), name="Depot Route"),
    path(
        "api/depot/<int:id>/define-trip",
        DefineTripAPIView.as_view(),
        name="Depot Define Trip Route",
    ),
    path(
        "api/depot/<int:id>/trips",
        TripsByDepotAPIView.as_view(),
        name="Trips by Depot Route",
    ),
    # carrier routes
    path("api/carriers", CarriersApiView.as_view(), name="Carriers Route"),
    path("api/carrier/<int:id>", CarrierApiView.as_view(), name="Carrier Route"),
    path(
        "api/carrier/<int:id>/trucks",
        TruckByCarrierApiView.as_view(),
        name="Carrier Trucks Route",
    ),
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
        "api/order/<int:id>/boxes",
        BoxesFromOrderView.as_view(),
        name="Get Order Boxes Route",
    ),
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
        name="Cancel Trip Route",
    ),
    path(
        "api/trip/<int:trip_id>/confirm-delivery/<int:delivery_id>",
        ConfirmDeliveryInTripAPIView.as_view(),
        name="Confirm Delivery Route",
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
    path("dashboard", UserDashboardTemplateView.as_view(), name="Dashboard View"),
    path("create-place", CreatePlaceTemplateView.as_view(), name="Create Place View"),
    path(
        "store/<int:place_id>",
        PlaceDashboardTemplateView.as_view(),
        name="Generic Store Dashboard",
    ),
    path(
        "store/<int:place_id>/create-order",
        CreateOrderTemplateView.as_view(),
        name="Create Order Form View",
    ),
    path(
        "store/<int:store_id>/order/<int:order_id>",
        OrderDetailsTemplateView.as_view(),
        name="Order Details View",
    ),
    path(
        "depot/<int:place_id>",
        PlaceDashboardTemplateView.as_view(),
        name="Generic Depot  Dashboard",
    ),
    path(
        "depot/<int:place_id>/create-trip",
        CreateTripTemplateView.as_view(),
        name="Create Trip View",
    ),
    path(
        "depot/<int:depot_id>/trip/<int:trip_id>",
        TripDetailsTemplateView.as_view(),
        name="Trip Details View",
    ),
    path(
        "depot/<int:depot_id>/trip/<int:trip_id>/start-trip",
        StartTripTemplateView.as_view(),
        name="Start Trip View",
    ),
    path(
        "depot/<int:depot_id>/trip/<int:trip_id>/simulate-trip",
        SimulateTripTemplateView.as_view(),
        name="Simulate Trip View",
    ),
    path(
        "carrier/<int:place_id>",
        PlaceDashboardTemplateView.as_view(),
        name="Generic Carrier Dashboard",
    ),
    path(
        "carrier/<int:carrier_id>/create-truck",
        CreateTruckTemplateView.as_view(),
        name="Generic Place Dashboard",
    ),
    path(
        "carrier/<int:carrier_id>/truck/<str:plate>",
        TruckDetailsTemplateView.as_view(),
        name="Truck Details View",
    ),
    path(
        "store/<int:store_id>/order/<int:order_id>/add-boxes",
        AddBoxTemplateView.as_view(),
        name="Add Box To The Order Template View",
    ),
    path(
        "store/<int:store_id>/order/<int:order_id>/remove-boxes",
        RemoveBoxTemplateView.as_view(),
        name="Remove Box To The Order Template View",
    ),
    # Swagger-UI routes
    path("api/docs", SwaggerUIView.as_view(), name="swagger-ui"),
    path("openapi.yaml", openapi_yaml_view, name="openapi-yaml"),
]
