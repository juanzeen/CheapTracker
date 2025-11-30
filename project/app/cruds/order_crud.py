from ..models import Order
from .store_crud import StoreCrud
from .trip_crud import TripCrud
from ..exception_errors import StatusError


class OrderCrud:
    @staticmethod
    def create(store_id):
        store = StoreCrud.read_by_id(store_id)

        return Order.objects.create(
            store=store,
            status="Pend",
            total_weight_kg=0.0,
            total_volume_m3=0.0,
            total_boxes=0,
        )

    @staticmethod
    def read():
        return Order.objects.all()

    @staticmethod
    def read_by_id(order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

    @staticmethod
    def read_orders_by_store(store_id):
        store = StoreCrud.read_by_id(store_id)

        return Order.objects.filter(store=store)

    @staticmethod
    def read_orders_by_trip(trip_id):
        trip = TripCrud.read_by_id(trip_id)

        return Order.objects.filter(trip=trip)

    @staticmethod
    def read_pend_orders():
        return Order.objects.filter(status="Pend")

    @staticmethod
    def delete(order_id):
        order = OrderCrud.read_by_id(order_id)

        if order.status != "Pend":
            raise StatusError("Order status must be Pending to delete")

        order.delete()
