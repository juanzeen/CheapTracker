from ..cruds.trip_crud import TripCrud
from ..cruds.delivery_crud import DeliveryCrud
from ..models import Trip

class TripService:
    @staticmethod
    def remaining_deliveries(trip_id):
        try: 
            Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")
        
        deliveries_list = DeliveryCrud.delivery_by_trip(trip_id)
        remaining_deliveries_list = []
        for delivery in deliveries_list:
            if delivery.delivered_at == None:
                remaining_deliveries_list.append(delivery)
        
        return remaining_deliveries_list
    
    @staticmethod
    def add_delivery(trip_id, store_id, order_id):
        return DeliveryCrud.create(trip_id=trip_id, store_id=store_id,
                                   order_id=order_id)