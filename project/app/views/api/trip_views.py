import json
from .base_views import AuthBaseView
from app.cruds.trip_crud import TripCrud
from django.forms.models import model_to_dict
from app.exception_errors import (
    StatusError,
    CapacityError,
    BelongError,
    RemainingDeliveriesError,
)
from app.cruds.delivery_crud import DeliveryCrud
from app.cruds.truck_crud import TruckCrud
from app.cruds.depot_crud import DepotCrud
from app.services.trip_service import TripService


class TripsAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            trips = TripCrud.read().values()
            return self.SuccessJsonResponse(
                "Trips successfully retrieved!", list(trips)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except PermissionError as e:
            return self.ErrorJsonResponse(e.args[0])

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = request.user
        if user.role != "Man":
            return self.ErrorJsonResponse(
                "To create a Trip, the user must be a Depot Manager", 401
            )

        try:
            trip = TripCrud.create(
                data["depot_id"],
                data["total_loaded_weight_kg"],
                data["total_loaded_volume_m3"],
                data["total_distance_km"],
            )
            return self.SuccessJsonResponse(
                "Trip successfully created", model_to_dict(trip), 201
            )
        except KeyError as e:
            return self.ErrorJsonResponse(e.args[0])
        except PermissionError as e:
            return self.ErrorJsonResponse(e.args[0])


class TripAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Trip successfully retrieved!", model_to_dict(trip)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])

    def delete(self, request, *args, **kwargs):
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            TripCrud.delete(trip.id)
            return self.SuccessJsonResponse(
                "Trip successfully deleted!", model_to_dict(trip)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])


class TripsByStatusAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        status = json.loads(request.body).get("status")
        try:
            trips = TripCrud.read_by_status(status).values()
            if not trips:
                return self.ErrorJsonResponse("Trips not founded!", 404)

            return self.SuccessJsonResponse(
                "Trips successfully retrieved!", list(trips)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except KeyError as e:
            return self.ErrorJsonResponse(e.args[0])


class TripsRemainingDeliveriesAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            deliveries = TripService.remaining_deliveries(trip.id)

            if len(deliveries) == 0:
                return self.ErrorJsonResponse("No remaining deliveries!", 404)

            return self.SuccessJsonResponse(
                "Remaining deliveries successfully retrieved!",
                deliveries
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])


class StartTripsAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            truck = TruckCrud.read_by_plate(data["truck_plate"])
            depot = DepotCrud.read_by_id(data["depot_id"])
            started_trip = TripService.start_trip(truck.plate, trip.id, depot.id)
            return self.SuccessJsonResponse(
                "Trip successfully started!", model_to_dict(started_trip)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])
        except CapacityError as e:
            return self.ErrorJsonResponse(e.args[0])
        except BelongError as e:
            return self.ErrorJsonResponse(e.args[0], 405)


class EndTripAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            depot = DepotCrud.read_by_id(data["depot_id"])
            ended_trip = TripService.end_trip(trip.id, depot.id)
            return self.SuccessJsonResponse(
                "Trip successfully ended!", model_to_dict(ended_trip)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])
        except RemainingDeliveriesError as e:
            return self.ErrorJsonResponse(e.args[0])
        except BelongError as e:
            return self.ErrorJsonResponse(e.args[0], 405)


class SimulateTripAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            trip = TripCrud.read_by_id(kwargs["id"])
            truck = TruckCrud.read_by_plate(data["truck_plate"])
            simulation = TripService.simulate_trip(
                trip.id, truck.plate, data["traffic_status"]
            )
            return self.SuccessJsonResponse("Simulation has been finished!", simulation)
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])


class CancelTripAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            depot = DepotCrud.read_by_id(data["depot_id"])
            TripService.cancel_trip(kwargs["id"], depot.id)
            trip = TripCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Trip successfully cancelled!", model_to_dict(trip)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])
        except BelongError as e:
            return self.ErrorJsonResponse(e.args[0], 405)


class ConfirmDeliveryInTripAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            trip = TripCrud.read_by_id(kwargs["trip_id"])
            truck = TruckCrud.read_by_plate(data["truck_plate"])
            delivery = DeliveryCrud.read_by_id(kwargs["delivery_id"])
            confirmed_delivery = TripService.confirm_delivery(
                trip.id, truck.plate, delivery.id
            )
            return self.SuccessJsonResponse(
                "Delivery successfully confirmed!", model_to_dict(confirmed_delivery)
            )
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])
        except BelongError as e:
            return self.ErrorJsonResponse(e.args[0])
