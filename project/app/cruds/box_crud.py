from ..models import Box
from .order_crud import OrderCrud
from ..exception_errors import StatusError


class BoxCrud:
    @staticmethod
    def create(order_id, size, length, width, height, payload_kg):
        order = OrderCrud.read_by_id(order_id)

        if size not in ["small", "medium", "big", "large", "custom"]:
            raise ValueError("Size must be: small, medium, big, large or custom")

        match size:
            case "small":
                return Box.objects.create(
                    order=order,
                    size="Sma",
                    length=0.4,
                    width=0.3,
                    height=0.2,
                    payload_kg=5.0,
                    was_delivered=False,
                )
            case "medium":
                return Box.objects.create(
                    order=order,
                    size="Med",
                    length=0.6,
                    width=0.4,
                    height=0.4,
                    payload_kg=15.0,
                    was_delivered=False,
                )
            case "big":
                return Box.objects.create(
                    order=order,
                    size="Big",
                    length=0.8,
                    width=0.6,
                    height=0.6,
                    payload_kg=25.0,
                    was_delivered=False,
                )
            case "large":
                return Box.objects.create(
                    order=order,
                    size="Lar",
                    length=1.2,
                    width=0.8,
                    height=0.8,
                    payload_kg=35.0,
                    was_delivered=False,
                )
            case "custom":
                if not all([length, width, height, payload_kg]):
                    raise ValueError(
                        "Custom boxes must have length, width, height and "
                        "payload_kg defined"
                    )

                if not all(
                    value > 0.01 for value in [length, width, height, payload_kg]
                ):
                    raise ValueError("Size values must be greater than 0.01")

                return Box.objects.create(
                    order=order,
                    size="Cus",
                    length=length,
                    width=width,
                    height=height,
                    payload_kg=payload_kg,
                    was_delivered=False,
                )

    @staticmethod
    def read():
        return Box.objects.all()

    @staticmethod
    def read_by_id(box_id):
        try:
            return Box.objects.get(id=box_id)
        except Box.DoesNotExist:
            raise ValueError("Box not found")

    @staticmethod
    def read_boxes_by_order(order_id):
        order = OrderCrud.read_by_id(order_id)

        return Box.objects.filter(order=order)

    @staticmethod
    def delete(box_id):
        box = BoxCrud.read_by_id(box_id)

        if box.order.status in ["Sche", "Ship", "Deli"]:
            raise StatusError(
                "Delete box denied. Order box has already been scheduled, shipped or delivered."
            )

        box.delete()
