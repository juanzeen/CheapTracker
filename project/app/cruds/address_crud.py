from ..models import Address


class AddressCrud:
    @staticmethod
    def create(street, number, complement, neighborhood, city, state, cep, country):
        return Address.objects.create(
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            cep=cep,
            country=country,
        )

    @staticmethod
    def read():
        return Address.objects.all()

    @staticmethod
    def read_by_id(address_id):
        try:
            return Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            raise ValueError

    @staticmethod
    def update(address_id, **kwargs):
        address = Address.objects.get(id=address_id)
        for key, value in kwargs.items():
            setattr(address, key, value)

        address.save()
        return address

    @staticmethod
    def delete(address_id):
        Address.objects.get(id=address_id).delete()

    @staticmethod
    def formatted_address(address_id):
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            raise ValueError("Address not found")

        return f"{address.street}, {address.number}, {address.neighborhood}, {address.city}, {address.state}, {address.cep}, {address.country}"
