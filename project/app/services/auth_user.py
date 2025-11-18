from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from ..models import User


class AuthUser:
    @staticmethod
    def login_user(request, email, password):
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password_hash):
                login(request, user)
                return {"success": True, "user": user}
            else:
                return {"success": False, "error": "Incorrect password"}
        except User.DoesNotExist:
            return {"sucess": False, "error": "User not found"}

    @staticmethod
    def logout_user(request):
        logout(request)
        return {"sucess": True, "message": "Logout successful"}
