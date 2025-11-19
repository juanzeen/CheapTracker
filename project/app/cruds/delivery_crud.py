from ..models import Delivery
from .trip_crud import TripCrud
from .store_crud import StoreCrud
from .order_crud import OrderCrud
from ..exception_errors import DeleteError


class DeliveryCrud:
    @staticmethod
    def create(trip_id, store_id, order_id, delivered_at=None):
        trip = TripCrud.read_by_id(trip_id)
        store = StoreCrud.read_by_id(store_id)
        order = OrderCrud.read_by_id(order_id)

        return Delivery.objects.create(
            trip=trip, store=store, order=order, delivered_at=delivered_at
        )

    @staticmethod
    def read():
        return Delivery.objects.all()
    
    @staticmethod
    def read_by_id(delivery_id):
        try:
            return Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            raise ValueError("Delivery not found")

    @staticmethod
    def delivery_by_trip(trip_id):
        trip = TripCrud.read_by_id(trip_id)

        return Delivery.objects.filter(trip=trip)

    @staticmethod
    def delivery_by_store(store_id):
        store = StoreCrud.read_by_id(store_id)

        return Delivery.objects.filter(store=store)

    @staticmethod
    def delivery_by_order(order_id):
        order = OrderCrud.read_by_id(order_id)

        return Delivery.objects.filter(order=order)

    @staticmethod
    def is_delivered(delivery_id):
        delivery = DeliveryCrud.read_by_id(delivery_id)

        if delivery.delivered_at == None:
            return False
        else:
            return True

    @staticmethod
    def delete(delivery_id):
        delivery = DeliveryCrud.read_by_id(delivery_id)

        if delivery.delivered_at:
            raise DeleteError("Delete delivery denied. This delivery has already been delivered")

        delivery.delete()
