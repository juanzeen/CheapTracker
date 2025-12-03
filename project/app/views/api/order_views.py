import json
from .base_views import AuthBaseView, ShopkeeperBaseView
from app.cruds.order_crud import OrderCrud
from app.cruds.box_crud import BoxCrud
from app.cruds.store_crud import StoreCrud
from app.cruds.trip_crud import TripCrud
from app.services.order_service import OrderService
from django.forms.models import model_to_dict
from app.exception_errors import BelongError, StatusError


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
            order_dict = model_to_dict(order)
            order_dict["created_at"] = order.created_at
            if request.user != order.store.user:
                return self.ErrorJsonResponse(
                    "User store don't match to the order!", 401
                )
            return self.SuccessJsonResponse(
                "Order successfully retrieved!", order_dict
            )
        except ValueError:
            return self.ErrorJsonResponse("Order not founded!", 404)

    def delete(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            if request.user != order.store.user:
                return self.ErrorJsonResponse(
                    "User store don't match to the order!", 401
                )
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
                f"Orders for the trip with the truck {trip.truck} successfully retrieved!",
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
            if data["box_size"] == "custom":
                box = OrderService.add_box(
                   order_id=kwargs["id"],
                    box_size=data["box_size"],
                    quantity=data["quantity"],
                    length=data["length"],
                    width=data["width"],
                    height=data["height"],
                    payload_kg=data["payload_kg"],
                )
                return self.SuccessJsonResponse(
                    "Custom box successfully added!", model_to_dict(box), 201
                )
            if data["box_size"] != "custom":
                box = OrderService.add_box(kwargs["id"], data["box_size"], data["quantity"])
                return self.SuccessJsonResponse(
                    f"{data["box_size"]} box successfully added!",
                    model_to_dict(box),
                    201,
                )
        except KeyError as e:
            return self.ErrorJsonResponse(f"The {e.args} field was not received!")
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0])
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])


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
        except StatusError as e:
            return self.ErrorJsonResponse(e.args[0])

class BoxesFromOrderView(ShopkeeperBaseView):
    def get(self, request, *args, **kwargs):
        try:
            order = OrderCrud.read_by_id(kwargs["id"])
            boxes = BoxCrud.read_boxes_by_order(order.id).values()
            if not order:
                return self.ErrorJsonResponse("Order not found!", 404)
            if not boxes:
                return self.ErrorJsonResponse("Boxes not found!", 404)

            return self.SuccessJsonResponse(
                f"Boxes associated to order {order.id} successfully retrieved!",
                list(boxes),
            )
        except ValueError as e:
            return self.ErrorJsonResponse(e.args[0], 404)
