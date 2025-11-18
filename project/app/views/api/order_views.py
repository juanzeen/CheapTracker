import json
from .base_views import AuthBaseView
from app.cruds.order_crud import OrderCrud
from app.cruds.store_crud import StoreCrud
from django.forms.models import model_to_dict


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
        OrderCrud.create(store_id)
        return self.SuccessJsonResponse("Order successfully created!", 201)


class OrderApiView(AuthBaseView):
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
