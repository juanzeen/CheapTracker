import json
from .base_views import BaseView, AuthBaseView
from app.models import Usuario
from app.cruds.user_crud import UserCrud
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from django.db import IntegrityError


class LoginView(BaseView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = authenticate(email=data["email"], password=data["password"])
        if user is not None:
            login(request, user)
            return self.SuccessJsonResponse(
                "User successfully logged in!", model_to_dict(user)
            )
        return self.ErrorJsonResponse("Invalid credentials!")


class LogoutView(BaseView):
    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            return self.SuccessJsonResponse("User successfully logged out!")
        except Exception as e:
            return self.ErrorJsonResponse("Error logging out!", data=e.args[0])


class UsersAPIView(BaseView):
    def get(self, request, *args, **kwargs):
        users = UserCrud.read().values()
        if not users:
            return self.ErrorJsonResponse("Users not found!")

        return self.SuccessJsonResponse("Users successfully retrieved!", list(users))

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            UserCrud.create(
                data["role"], data["name"], data["age"], data["email"], data["password"]
            )
            return self.SuccessJsonResponse(
                "User successfully created!",
                {
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "role": data.get("role"),
                },
                201,
            )
        except KeyError as e:
            return self.ErrorJsonResponse(data=e.args)
        except IntegrityError as e:
            return self.ErrorJsonResponse(f"E-mail already used: {data["email"]}", 409)


class UserAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
        try:
            user = UserCrud.read_by_email(kwargs["email"])
            if request.user != user:
                return self.ErrorJsonResponse(
                    "User don't match with the requested user", 403
                )
            return self.SuccessJsonResponse(
                "User successfully retrieved!",
                {"name": user.name, "email": user.email, "role": user.role},
                200,
            )
        except Usuario.DoesNotExist:
            return self.ErrorJsonResponse("User not found!", 404)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = UserCrud.read_by_email(kwargs["email"])
            if request.user != user:
                return self.ErrorJsonResponse(
                    "User don't match with the requested user", 403
                )
            UserCrud.update(user.id, **data)
            return self.SuccessJsonResponse(
                {"message": "User successfully requested!", "data": data}
            )
        except KeyError as e:
            return self.ErrorJsonResponse(data=e.args)
        except ValueError as e:
            return self.ErrorJsonResponse("User not found")

    def delete(self, request, *args, **kwargs):
        try:
            user = UserCrud.read_by_email(kwargs["email"])
            if request.user != user:
                return self.ErrorJsonResponse(
                    "User don't match with the requested user", 403
                )
            UserCrud.delete(user.id)
            return self.SuccessJsonResponse("User successfully deleted!")
        except Usuario.DoesNotExist:
            return self.ErrorJsonResponse("User not found!", 404)


class ChangePasswordView(AuthBaseView):
    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = UserCrud.read_by_email(kwargs["email"])
            if request.user != user:
                return self.ErrorJsonResponse(
                    "User don't match with the requested user", 403
                )
            UserCrud.change_password(
                user.id, data.get("old_password"), data.get("new_password")
            )
            return self.SuccessJsonResponse(
                "Password successfully changed!",
                {"new_password": data.get("new_password")},
            )
        except ValueError as e:
            return self.ErrorJsonResponse("Invalid old password!")
