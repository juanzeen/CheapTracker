from ..cruds.box_crud import BoxCrud
from ..cruds.order_crud import OrderCrud
from ..exception_errors import StatusError, BelongError


class OrderService:
    @staticmethod
    def add_box(
        order_id,
        box_size,
        quantity,
        length=None,
        width=None,
        height=None,
        payload_kg=None,
    ):
        order = OrderCrud.read_by_id(order_id)

        if order.status != "Pend":
            raise StatusError("Order status must be Pending to add a box")

        if quantity < 1:
            raise ValueError("The boxes quantity must be greater than 0!")

        for _ in range(quantity):
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
        order = OrderCrud.read_by_id(order_id)
        box = BoxCrud.read_by_id(box_id)

        if box.order.id != order_id:
            raise BelongError("This box does not belong to this order")

        if order.status != "Pend":
            raise StatusError("Order status must be Pending to delete a box")

        order.total_weight_kg -= box.payload_kg
        order.total_volume_m3 -= box.volume_m3
        order.total_boxes -= 1

        order.save()
        BoxCrud.delete(box_id)
