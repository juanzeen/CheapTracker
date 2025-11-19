from ..models import Order, Box
from ..cruds.box_crud import BoxCrud


class OrderService:
    @staticmethod
    def add_box(
        order_id, box_size, length=None, width=None, height=None, payload_kg=None
    ):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

        if order.status != "Pend":
            raise ValueError("Order status must be Pending to add a box")

        box = BoxCrud.create(
            order_id=order_id,
            size=box_size,
            length=length,
            width=width,
            height=height,
            payload_kg=payload_kg,
        )

        order.total_weight_kg += box.payload_kg
        order.total_volume_m3 += box.volume_m3
        order.total_boxes += 1

        order.save()
        return order

    @staticmethod
    def remove_box(order_id, box_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

        try:
            box = Box.objects.get(id=box_id)
        except Box.DoesNotExist:
            raise ValueError("Box not found")

        if box.order.id != order_id:
            raise ValueError("This box does not belong to this order")

        if order.status != "Pend":
            raise ValueError("Order status must be Pending to add a box")

        order.total_weight_kg -= box.payload_kg
        order.total_volume_m3 -= box.volume_m3
        order.total_boxes -= 1

        order.save()
        BoxCrud.delete(box_id)
