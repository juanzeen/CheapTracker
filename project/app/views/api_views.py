import json
from django.http import JsonResponse
from django.views import View
from app.models import Usuario
from app.cruds.user_crud import UserCrud
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):
  def SuccessJsonResponse(self, message='Success in operation!', data={}, status=200):
    return JsonResponse({'message': message, 'data': data}, status=status, safe=False)

  def ErrorJsonResponse(self, message='Fail in operation!', status=400):
    return JsonResponse({'error': message}, status=status, safe=False)

# class AuthBaseView(BaseView):
#   def is_authenticated(self, request):
#     if request.user.is_authenticated:
#       return True
#     return False


class UsersAPIView(BaseView):
  def get(self, request, *args, **kwargs):
    users = UserCrud.read().values()
    if not users:
      return self.ErrorJsonResponse("Users not founded!")

    return self.SuccessJsonResponse('Users successfully retrieved!',list(users))

  def post(self, request, *args, **kwargs):
    try:
      data = json.loads(request.body)
      UserCrud.create(data['role'], data['name'], data['age'], data['email'], data['password'])
      return self.SuccessJsonResponse("User successfully created!",{"name": data.get('name'), "email": data.get('email'), "role": data.get('role')}, 201)
    except KeyError as e:
      return self.ErrorJsonResponse(e.args)

class UserAPIView(BaseView):
  def get(self, request, *args, **kwargs):
    try:
      user = UserCrud.read_by_email(kwargs['email'])
      return self.SuccessJsonResponse("User successfully retrieved!",{"name": user.name, "email": user.email, "role": user.role}, 200)
    except Usuario.DoesNotExist:
      return self.ErrorJsonResponse("User not founded!", 404)

  def put(self, request, *args, **kwargs):
    try:
      data = json.loads(request.body)
      user = UserCrud.read_by_email(kwargs['email'])
      UserCrud.update(user.id, **data)
      return self.SuccessJsonResponse({"message": "User successfully updated!", "data": data })
    except KeyError as e:
      return self.ErrorJsonResponse(e.args)
    except Usuario.DoesNotExist:
      return self.ErrorJsonResponse("User not founded!")

  def delete(self, request, *args, **kwargs):
    try:
      user = UserCrud.read_by_email(kwargs['email'])
      UserCrud.delete(user.id)
      return self.SuccessJsonResponse("User successfully deleted!")
    except Usuario.DoesNotExist:
      return self.ErrorJsonResponse("User not founded!", 404)

class ChangePasswordView(BaseView):
  def put(self, request, *args, **kwargs):
    try:
      data = json.loads(request.body)
      user = UserCrud.read_by_email(kwargs['email'])
      UserCrud.change_password(user.id, data.get('old_password'), data.get('new_password'))
      return self.SuccessJsonResponse("Password successfully changed!", {"new_password": data.get('new_password')})
    except ValueError as e:
      return self.ErrorJsonResponse("Invalid old password!")
