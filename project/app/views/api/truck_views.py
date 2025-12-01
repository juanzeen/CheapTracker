import json
from .base_views import CarrierBaseView
from app.cruds.carrier_crud import CarrierCrud
from app.cruds.truck_crud import TruckCrud
from app.models import Truck
from django.forms.models import model_to_dict


class TrucksApiView(CarrierBaseView):
    def get(self, request, *args, **kwargs):
        trucks = TruckCrud.read().values()
        if not trucks:
            return self.ErrorJsonResponse("Trucks not founded!", 404)

        return self.SuccessJsonResponse("Trucks successfully retrieved!", list(trucks))

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            carrier = CarrierCrud.read_by_id(data["carrier_id"])
            if carrier.user_email != request.user:
                return self.ErrorJsonResponse("Carrier don't match to user!", 401)
            if request.user.role != "Carr":
                return self.ErrorJsonResponse(
                    "User don't have permission to this action!", 401
                )
            if not carrier:
                return self.ErrorJsonResponse("Carrier not founded!", 404)
            truck = TruckCrud.create(
                data["carrier_id"],
                data["plate"],
                data["category"],
                data["release_year"],
            )
            return self.SuccessJsonResponse(
                "Truck successfully created!", model_to_dict(truck), 201
            )
        except ValueError:
            return self.ErrorJsonResponse("Carrier not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class TruckApiView(CarrierBaseView):
    def get(self, request, *args, **kwargs):
        try:
            truck = TruckCrud.read_by_plate(kwargs["plate"])
            return self.SuccessJsonResponse(
                "Truck successfully retrieved!",
                model_to_dict(truck),
                200,
            )
        except ValueError:
            return self.ErrorJsonResponse("Truck not founded!", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            truck = TruckCrud.read_by_plate(kwargs["plate"])
            if not truck:
                return self.ErrorJsonResponse("Truck not founded!", 404)
            updated_truck = TruckCrud.update(truck.plate, **data)
            return self.SuccessJsonResponse(
                "Address successfully updated!", model_to_dict(updated_truck), 200
            )

        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except Truck.DoesNotExist:
            return self.ErrorJsonResponse("Truck not founded", 404)

    def delete(self, request, *args, **kwargs):
        try:
            truck = TruckCrud.read_by_plate(kwargs["plate"])
            TruckCrud.delete(truck.plate)
            return self.SuccessJsonResponse(
                "Truck successfully deleted!",
                {
                    "plate": truck.plate,
                    "axles": truck.axles_count,
                    "release_year": truck.release_year,
                },
            )
        except Truck.DoesNotExist:
            return self.ErrorJsonResponse("Truck not found", 404)
