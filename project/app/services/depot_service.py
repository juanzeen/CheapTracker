from ..models import Depot, Order
from ..cruds.order_crud import OrderCrud


class DepotService:
    @staticmethod
    def select_orders(depot_id, orders_id_list):
        try:
            depot = Depot.objects.get(id=depot_id)
        except Depot.DoesNotExist:
            raise ValueError("Depot not found")

        selected_orders = []

        for order_id in orders_id_list:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise ValueError("Order not found")

            if order.status == "Pend":
                selected_orders.append(order)
            else:
                raise ValueError("Order must be pending to be selected")

        if not selected_orders:
            raise ValueError("No valid pending orders selected")

        return depot, selected_orders
