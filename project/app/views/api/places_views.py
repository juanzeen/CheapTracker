import json
from .base_views import AuthBaseView
from app.models import Usuario, Address
from app.cruds.address_crud import AddressCrud
from app.cruds.store_crud import StoreCrud
from app.cruds.depot_crud import DepotCrud
from app.cruds.carrier_crud import CarrierCrud
from app.services.trip_service import TripService
from django.forms.models import model_to_dict
from exception_errors import RangeError, StatusError




class AddressesAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            AddressCrud.create(
                data["street"],
                data["number"],
                data["complement"],
                data["neighborhood"],
                data["city"],
                data["state"],
                data["cep"],
                data["country"],
            )
            return self.SuccessJsonResponse(
                "Address successfully created",
                {
                    "street": data.get("street"),
                    "number": data.get("number"),
                    "complement": data.get("complement"),
                    "neighborhood": data.get("neighborhood"),
                    "city": data.get("city"),
                    "state": data.get("state"),
                    "cep": data.get("cep"),
                    "country": data.get("country"),
                },
                201,
            )
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")

    def get(self, request, *args, **kwargs):
        addresses = AddressCrud.read().values()
        if not addresses:
            return self.ErrorJsonResponse("Addresses not founded!")

        return self.SuccessJsonResponse(
            "Addresses successfully retrieved!", list(addresses)
        )


class AddressAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            address = Address.objects.get(id=kwargs["id"])
            return self.SuccessJsonResponse(
                "Address successfully retrieved!",
                {
                    "street": address.street,
                    "number": address.number,
                    "complement": address.complement,
                    "neighborhood": address.neighborhood,
                    "city": address.city,
                    "state": address.state,
                    "cep": address.cep,
                    "country": address.country,
                },
                200,
            )
        except Address.DoesNotExist:
            return self.ErrorJsonResponse("Address not found", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            address = Address.objects.get(id=kwargs["id"])
            AddressCrud.update(address.id, **data)
            return self.SuccessJsonResponse(
                {"message": "Address successfully updated!", "data": data}
            )
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except Address.DoesNotExist:
            return self.ErrorJsonResponse("Address not found")

    def delete(self, request, *args, **kwargs):
        try:
            address = Address.objects.get(id=kwargs["id"])
            AddressCrud.delete(address.id)
            return self.SuccessJsonResponse("Address successfully deleted!")
        except Address.DoesNotExist:
            return self.ErrorJsonResponse("Address not found", 404)


# Places views


class StoresApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        stores = StoreCrud.read().values()
        if not stores:
            return self.ErrorJsonResponse("Stores not founded!")

        return self.SuccessJsonResponse("Stores successfully retrieved!", list(stores))

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = request.user
            if not user.role == "Shop":
                return self.ErrorJsonResponse(
                    "To create a Store, the user role must be: Shop", 401
                )

            StoreCrud.create(
                request.user,
                data["name"],
                data["cep"],
                data["street"],
                data["number"],
                data["complement"],
                data["neighborhood"],
                data["city"],
                data["state"],
                data["country"],
                data["contact"],
                data["registration"],
            )
            return self.SuccessJsonResponse(
                "Store successfully created!",
                {
                    "name": data.get("name"),
                    "contact": data.get("contact"),
                    "registration": data.get("registration"),
                },
                201,
            )
        except Usuario.DoesNotExist:
            return self.ErrorJsonResponse("User not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class StoreApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            store = StoreCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Store successfully retrieved!", model_to_dict(store)
            )
        except ValueError:
            return self.ErrorJsonResponse("Store not founded!", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            store = StoreCrud.read_by_id(kwargs["id"])
            if not store:
                return self.ErrorJsonResponse("Store not founded!", 404)
            StoreCrud.update(store.id, **data)
            return self.SuccessJsonResponse("Store successfully updated!", data)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except ValueError:
            return self.ErrorJsonResponse("Store not founded!", 404)

    def delete(self, request, *args, **kwargs):
        try:
            store = StoreCrud.read_by_id(kwargs["id"])
            StoreCrud.delete(store.id)
            return self.SuccessJsonResponse("Store successfully deleted!")
        except ValueError:
            return self.ErrorJsonResponse("Store not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class DepotsApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        depots = DepotCrud.read().values()
        if not depots:
            return self.ErrorJsonResponse("Depots not founded!")

        return self.SuccessJsonResponse("Depots successfully retrieved!", list(depots))

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = request.user
            if user.role != "Man":
                return self.ErrorJsonResponse(
                    "To create a Depot, the user role must be: Man", 401
                )

            DepotCrud.create(
                request.user,
                data["name"],
                data["cep"],
                data["street"],
                data["number"],
                data["complement"],
                data["neighborhood"],
                data["city"],
                data["state"],
                data["country"],
                data["contact"],
                data["registration"],
            )
            return self.SuccessJsonResponse(
                "Depot successfully created!",
                {
                    "name": data.get("name"),
                    "contact": data.get("contact"),
                    "registration": data.get("registration"),
                },
                201,
            )
        except Usuario.DoesNotExist:
            return self.ErrorJsonResponse("User not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class DepotApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            depot = DepotCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Depot successfully retrieved!", model_to_dict(depot)
            )
        except ValueError:
            return self.ErrorJsonResponse("Depot not founded!", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            depot = DepotCrud.read_by_id(kwargs["id"])
            if not depot:
                return self.ErrorJsonResponse("Depot not founded!", 404)
            DepotCrud.update(depot.id, **data)
            return self.SuccessJsonResponse("Depot successfully updated!", data)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except ValueError:
            return self.ErrorJsonResponse("Depot not founded!", 404)

    def delete(self, request, *args, **kwargs):
        try:
            depot = DepotCrud.read_by_id(kwargs["id"])
            DepotCrud.delete(depot.id)
            return self.SuccessJsonResponse("Depot successfully deleted!")
        except ValueError:
            return self.ErrorJsonResponse("Depot not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")

class DefineTripAPIView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        try:
            depot = DepotCrud.read_by_id(kwargs["id"])
            orders = json.loads(request.body).get("orders")
            trip, route_order, fig = TripService.define_trip(depot, orders)
            return self.SuccessJsonResponse(f"Trip successfully defined!", {"trip": model_to_dict(trip), "route_order": route_order})
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except KeyError as e:
            return self.ErrorJsonResponse(e.args[0])
        except RangeError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])



class CarriersApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        carriers = CarrierCrud.read().values()
        if not carriers:
            return self.ErrorJsonResponse("Carriers not founded!")

        return self.SuccessJsonResponse(
            "Carriers successfully retrieved!", list(carriers)
        )

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = request.user
            if user.role != "Carr":
                return self.ErrorJsonResponse(
                    "To create a Carrier, the user role must be: Carr", 401
                )

            CarrierCrud.create(
                request.user,
                data["name"],
                data["cep"],
                data["street"],
                data["number"],
                data["complement"],
                data["neighborhood"],
                data["city"],
                data["state"],
                data["country"],
                data["contact"],
                data["registration"],
            )
            return self.SuccessJsonResponse(
                "Carrier successfully created!",
                {
                    "name": data.get("name"),
                    "contact": data.get("contact"),
                    "registration": data.get("registration"),
                },
                201,
            )
        except Usuario.DoesNotExist:
            return self.ErrorJsonResponse("User not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class CarrierApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            carrier = CarrierCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Carrier successfully retrieved!", model_to_dict(carrier)
            )
        except ValueError:
            return self.ErrorJsonResponse("Carrier not founded!", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            carrier = CarrierCrud.read_by_id(kwargs["id"])
            if not carrier:
                return self.ErrorJsonResponse("Carrier not founded!", 404)
            CarrierCrud.update(carrier.id, **data)
            return self.SuccessJsonResponse("Carrier successfully updated!", data)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except ValueError:
            return self.ErrorJsonResponse("Carrier not founded!", 404)

    def delete(self, request, *args, **kwargs):
        try:
            carrier = CarrierCrud.read_by_id(kwargs["id"])
            CarrierCrud.delete(carrier.id)
            return self.SuccessJsonResponse("Carrier successfully deleted!")
        except ValueError:
            return self.ErrorJsonResponse("Carrier not founded!", 404)
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
