import json
from .base_views import AuthBaseView, ShopkeeperBaseView
from app.cruds.order_crud import OrderCrud
from app.cruds.store_crud import StoreCrud
from app.cruds.trip_crud import TripCrud
from app.services.order_service import OrderService
from django.forms.models import model_to_dict
from app.exception_errors import BelongError


class OrdersApiView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        orders = OrderCrud.read().values()
        if not orders:
            return self.ErrorJsonResponse("Orders not founded!")

        return self.SuccessJsonResponse("Orders successfully retrieved!", list(orders))

    def post(self, request, *args, **kwargs):
        store_id = json.loads(request.body).get("store_id")
        current_store = StoreCrud.read_by_id(store_id)
        if not current_store:
            return self.ErrorJsonResponse("Store not founded!", 404)
        if current_store.user != request.user:
            return self.ErrorJsonResponse("Store don't match to user!", 401)
        if request.user.role not in ["Shop", "Adm"]:
            return self.ErrorJsonResponse(
                "User don't have permission to this action!", 401
            )
        OrderCrud.create(store_id)
        return self.SuccessJsonResponse("Order successfully created!", 201)


class OrderApiView(ShopkeeperBaseView):
    def get(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            return self.SuccessJsonResponse(
                "Order successfully retrieved!", model_to_dict(order)
            )
        except ValueError:
            return self.ErrorJsonResponse("Order not founded!", 404)

    def delete(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            OrderCrud.delete(order.id)
            return self.SuccessJsonResponse(
                "Order successfully deleted!", model_to_dict(order)
            )
        except ValueError:
            return self.ErrorJsonResponse("Order not founded!", 404)


class OrdersByTripView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            orders = OrderCrud.read_orders_by_trip(kwargs["id"]).values()
            trip = TripCrud.read_by_id(kwargs["id"])
            if not orders:
                return self.ErrorJsonResponse("Orders not founded!")
            if request.user.role not in ["Shop", "Man", "Adm"]:
                return self.ErrorJsonResponse(
                    "User don't have permission to this action!", 401
                )
            return self.SuccessJsonResponse(
                f"Orders for the trip with the truck {trip.truck.plate} successfully retrieved!",
                list(orders),
            )
        except ValueError:
            return self.ErrorJsonResponse("Trip not founded!", 404)


class OrdersByStoreView(ShopkeeperBaseView):
    def get(self, request, *args, **kwargs):
        try:
            store = StoreCrud.read_by_id(kwargs["id"])
            orders = OrderCrud.read_orders_by_store(store.id).values()
            if not orders:
                return self.ErrorJsonResponse("Orders not founded!", 404)

            return self.SuccessJsonResponse(
                f"Orders associated to {store.name} successfully retrieved!",
                list(orders),
            )
        except ValueError:
            return self.ErrorJsonResponse("Store not founded!", 404)


class PendentOrdersView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        orders = OrderCrud.read_pend_orders().values()
        if not orders:
            return self.ErrorJsonResponse("Orders not founded!")

        return self.SuccessJsonResponse(
            "Pendent orders successfully retrieved!", list(orders)
        )


class AddBoxView(ShopkeeperBaseView):
    def post(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            data = json.loads(request.body)
            if order.store.user != request.user:
                return self.ErrorJsonResponse("Order's Store don't match to user!", 401)
            if data["box_size"] == "Cus":
                box = OrderService.add_box(
                    kwargs["id"],
                    data["box_size"],
                    data["length"],
                    data["width"],
                    data["height"],
                    data["payload_kg"],
                )
                return self.SuccessJsonResponse(
                    "Custom box successfully added!", model_to_dict(box), 201
                )
            if data["box_size"] != "Cus":
                box = OrderService.add_box(kwargs["id"], data["box_size"])
                return self.SuccessJsonResponse(
                    f"{data["box_size"]} box successfully added!",
                    model_to_dict(box),
                    201,
                )
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")


class RemoveBoxView(ShopkeeperBaseView):
    def post(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            data = json.loads(request.body)
            if order.store.user != request.user:
                return self.ErrorJsonResponse("Order's Store don't match to user!", 401)
            OrderService.remove_box(kwargs["id"], data["box_id"])
            return self.SuccessJsonResponse(
                "Box successfully removed!", model_to_dict(order)
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except BelongError as e:
            return self.ErrorJsonResponse(e.args[0])
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
