from ..models import User
from django.contrib.auth.hashers import check_password

class UserCrud:
    @staticmethod
    def create(role, name, age, email, password):
        if len(password) < 8:
            raise ValueError("The password must contain at least 8 characters")
        
        return User.objects.create(role=role, name=name, age=age, email=email,
                                   password_hash=password)
    
    @staticmethod
    def read():
        return User.objects.all()
    
    @staticmethod
    def read_by_email(user_email):
        return User.objects.get(email=user_email)
    
    @staticmethod
    def update(user_id, **kwargs):
        user = User.objects.get(id=user_id)
        for key, value in kwargs.items():
            if key == "password_hash":
                raise KeyError("Change password denied")

            setattr(user, key, value)

        user.save()
        return user
    
    @staticmethod
    def delete(user_id):
        User.objects.get(id=user_id).delete()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = User.objects.get(id=user_id)

        if not check_password(old_password, user.password_hash):
            raise ValueError("Incorrect password!")
        
        if len(new_password) < 8:
            raise ValueError("The new password must contain at least 8 characters")

        user.password_hash = new_password
        user.save()
        return user