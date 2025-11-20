from ..models import Depot, Order
from ..cruds.order_crud import OrderCrud
from ..cruds.depot_crud import DepotCrud
from ..exception_errors import StatusError


class DepotService:
    @staticmethod
    def select_orders(depot_id, orders_id_list):
        depot = DepotCrud.read_by_id(depot_id)

        selected_orders = []

        for order_id in orders_id_list:
            order = OrderCrud.read_by_id(order_id)

            if order.status == "Pend":
                selected_orders.append(order)
            else:
                raise StatusError("Order status must be pending to be selected")

        if not selected_orders:
            raise ValueError("No valid pending orders selected")

        return depot, selected_orders
