from ..models import Carrier
from .address_crud import AddressCrud
from .user_crud import UserCrud


class CarrierCrud:
    @staticmethod
    def create(
        user_email,
        name,
        contact,
        registration,
        street,
        number,
        complement,
        neighborhood,
        city,
        state,
        cep,
        country,
    ):
        user = UserCrud.read_by_email(user_email)
        if user.role != "Carr":
            raise ValueError("To create a Carrier, the user role must be: Carr")

        address = AddressCrud.create(
            street, number, complement, neighborhood, city, state, cep, country
        )

        return Carrier.objects.create(
            user=user,
            name=name,
            address=address,
            contact=contact,
            registration=registration,
        )

    @staticmethod
    def read():
        return Carrier.objects.all()

    @staticmethod
    def read_by_id(carrier_id):
        try:
            carrier = Carrier.objects.get(id=carrier_id)
            return carrier
        except Carrier.DoesNotExist:
            raise ValueError

    @staticmethod
    def read_carriers_by_email(user_email):
        user = UserCrud.read_by_email(user_email)
        return Carrier.objects.filter(user=user)

    @staticmethod
    def update(carrier_id, **kwargs):
        carrier = Carrier.objects.get(id=carrier_id)
        address = carrier.address
        for key, value in kwargs.items():
            if key in [
                "street",
                "number",
                "complement",
                "neighborhood",
                "city",
                "state",
                "cep",
                "country",
            ]:
                setattr(address, key, value)
            elif key == "user":
                raise KeyError("Update user denied")
            else:
                setattr(carrier, key, value)

        address.save()
        carrier.save()
        return carrier

    @staticmethod
    def delete(carrier_id):
        carrier = Carrier.objects.get(id=carrier_id)
        AddressCrud.delete(carrier.address.id)
