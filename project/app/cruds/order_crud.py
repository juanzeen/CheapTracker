from ..models import Order, Store


class OrderCrud:
    @staticmethod
    def create(store_id):
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise ValueError("Store not found")

        return Order.objects.create(
            store=store,
            status="Pend",
            total_weight_kg=0.0,
            total_volume_m3=0.0,
            total_boxes=0,
            scheduled=False,
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
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise ValueError("Store not found")

        return Order.objects.filter(store=store)

    @staticmethod
    def delete(order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

        if order.status != "Pend":
            raise ValueError("Order status must be Pending to delete")

        order.delete()
