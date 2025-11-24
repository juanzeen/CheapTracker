from ..models import Usuario
from ..models import Manager
from django.contrib.auth.hashers import check_password


class UserCrud:
    @staticmethod
    def create(role, name, age, email, password):
        if len(password) < 8:
            raise ValueError("The password must contain at least 8 characters")

        return Usuario.objects.create_user(
            email=email, role=role, name=name, age=age, password=password
        )

    @staticmethod
    def read():
        return Usuario.objects.all()

    @staticmethod
    def read_by_email(user_email):
        try:
            return Usuario.objects.get(email=user_email)
        except Usuario.DoesNotExist:
            raise ValueError("User not found")

    @staticmethod
    def read_by_id(user_id):
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise ValueError("User not found")

    @staticmethod
    def update(user_id, **kwargs):
        user = UserCrud.read_by_id(user_id)
        for key, value in kwargs.items():
            if key == "password_hash":
                raise KeyError("Change password denied")

            setattr(user, key, value)

        user.save()
        return user

    @staticmethod
    def delete(user_id):
        user = UserCrud.read_by_id(user_id)
        user.delete()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = UserCrud.read_by_id(user_id)

        if not check_password(old_password, user.password):
            raise ValueError("Incorrect password!")

        if len(new_password) < 8:
            raise ValueError("The new password must contain at least 8 characters")

        user.set_password(new_password)
        user.save()
        return user
