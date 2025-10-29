from ..models import Delivery, Trip, Store, Order

class DeliveryCrud:
    @staticmethod
    def create(trip_id, store_id, order_id, delivered_at=None):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise ValueError("Store not found")
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")
        
        return Delivery.objects.create(trip=trip, store=store, order=order, 
                                       delivered_at=delivered_at)
    
    @staticmethod
    def read():
        return Delivery.objects.all()
    
    @staticmethod
    def delivery_by_trip(trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")
        
        return Delivery.objects.filter(trip=trip)
    
    @staticmethod
    def delivery_by_store(store_id):
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise ValueError("Store not found")
        
        return Delivery.objects.filter(store=store)
    
    @staticmethod
    def delivery_by_order(order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")
        
        return Delivery.objects.filter(order=order)
    
    @staticmethod
    def is_delivered(delivery_id):
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            raise ValueError("Delivery not found")
        
        if delivery.delivered_at == None:
            return False
        else:
            return True