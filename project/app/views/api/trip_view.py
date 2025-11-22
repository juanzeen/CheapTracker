import json
from .base_views import AuthBaseView
from app.cruds.trip_crud import TripCrud
from django.forms.models import model_to_dict
from app.exception_errors import StatusError


class TripsAPIView(AuthBaseView):
  def get(self, request, *args, **kwargs):
    try:
      trips = TripCrud.read().values()
      return self.SuccessJsonResponse("Trips successfully retrieved!", list(trips))
    except ValueError as e:
      return self.ErrorJsonResponse(e.args[0])
    except PermissionError as e:
      return self.ErrorJsonResponse(e.args[0])


  def post(self, request, *args, **kwargs):
    data = json.loads(request.body)
    user = request.user
    if user.role != "Man":
      return self.ErrorJsonResponse("To create a Trip, the user must be a Depot Manager", 401)

    try:
      trip = TripCrud.create(data["depot_id"], data["total_loaded_weight_kg"], data["total_loaded_volume_m3"], data["total_distance_km"])
      return self.SuccessJsonResponse("Trip successfully created", model_to_dict(trip), 201)
    except KeyError as e:
      return self.ErrorJsonResponse(e.args[0])
    except PermissionError as e:
      return self.ErrorJsonResponse(e.args[0])

class TripAPIView(AuthBaseView):
  def get(self, request, *args, **kwargs):
    try:
      trip = TripCrud.read_by_id(kwargs["id"])
      return self.SuccessJsonResponse("Trip successfully retrieved!", model_to_dict(trip))
    except ValueError as e:
      return self.ErrorJsonResponse(e.args[0])

  def delete(self, request, *args, **kwargs):
    try:
      trip = TripCrud.read_by_id(kwargs["id"])
      TripCrud.delete(trip.id)
      return self.SuccessJsonResponse("Trip successfully deleted!", model_to_dict(trip))
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

      return self.SuccessJsonResponse("Trips successfully retrieved!", list(trips))
    except ValueError as e:
      return self.ErrorJsonResponse(e.args[0])
    except KeyError as e:
      return self.ErrorJsonResponse(e.args[0])
