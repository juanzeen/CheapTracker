from ..models import Depot
from .address_crud import AddressCrud
from .user_crud import UserCrud


class DepotCrud:
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
        if user.role != "Man":
            raise ValueError("To create a Depot, the user role must be: Man")

        address = AddressCrud.create(
            street, number, complement, neighborhood, city, state, cep, country
        )

        return Depot.objects.create(
            user=user,
            name=name,
            address=address,
            contact=contact,
            registration=registration,
        )

    @staticmethod
    def read():
        return Depot.objects.all()

    @staticmethod
    def read_by_id(carrier_id):
        try:
            depot = Depot.objects.all(id=carrier_id)
            return depot
        except Depot.DoesNotExist:
            raise ValueError

    @staticmethod
    def read_depots_by_email(user_email):
        user = UserCrud.read_by_email(user_email)
        return Depot.objects.filter(user=user)

    @staticmethod
    def update(depot_id, **kwargs):
        depot = Depot.objects.get(id=depot_id)
        address = depot.address
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
                setattr(depot, key, value)

        address.save()
        depot.save()
        return depot

    @staticmethod
    def delete(depot_id):
        depot = Depot.objects.get(id=depot_id)
        AddressCrud.delete(depot.address.id)
