from ..models import Store
from .address_crud import AddressCrud
from .user_crud import UserCrud

class StoreCrud:
    @staticmethod
    def create(user_email, name, contact, registration, 
               street, number, complement, neighborhood, city, state, cep, country):
        user = UserCrud.read_by_email(user_email)
        if user.role != "Shop":
            raise ValueError("To create a Store, the user role must be: Shop")

        address = AddressCrud.create(street, number, complement, 
                                        neighborhood, city, state, cep, country)

        return Store.objects.create(user=user, name=name, address=address,
                                    contact=contact, registration=registration)

    @staticmethod
    def read():
        return Store.objects.all()
    
    @staticmethod
    def read_stores_by_email(user_email):
        user = UserCrud.read_by_email(user_email)
        return Store.objects.filter(user=user)
    
    @staticmethod
    def update(store_id, **kwargs):
        store = Store.objects.get(id=store_id)
        address = store.address
        for key, value in kwargs.items():
            if key in ["street", "number", "complement", "neighborhood", "city", 
                       "state", "cep", "country"]:
                setattr(address, key, value)
            elif key == "user":
                raise KeyError("Update user denied")
            else:
                setattr(store, key, value)
        
        address.save()
        store.save()
        return store
    
    @staticmethod
    def delete(store_id):
        store = Store.objects.get(id=store_id)
        AddressCrud.delete(store.address.id)