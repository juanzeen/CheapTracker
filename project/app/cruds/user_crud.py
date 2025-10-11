from ..models import User

class UserCrud:
    @staticmethod
    def create(role, name, age, email, password_hash):
        return User.objects.create(role=role, name=name, age=age, email=email,
                                   password_hash=password_hash)
    
    @staticmethod
    def read():
        return User.objects.all()
    
    @staticmethod
    def update(user_id, **kwargs):
        user = User.objects.get(id=user_id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user
    
    @staticmethod
    def delete(user_id):
        User.objects.get(id=user_id).delete()