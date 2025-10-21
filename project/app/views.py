import json
from django.http import JsonResponse
from django.views import View
from .models import User
from .cruds.user_crud import UserCrud
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):
  def SuccesJsonResponse(self, data, status=200):
    return JsonResponse(data, status=status, safe=False)

  def ErrorJsonResponse(self, message, status=400):
    return JsonResponse({'error': message}, status=status, safe=False)


class UserAPIView(BaseView):
  def get(self, request, *args, **kwargs):
    users = UserCrud.read().values('name', 'role', 'email')
    if not users:
      return self.ErrorJsonResponse("Nenhum usuário encontrado!")

    return self.SuccesJsonResponse(list(users))

  def post(self, request, *args, **kwargs):
    try:
      data = json.loads(request.body)
      new_user = UserCrud.create(data['role'], data['name'], data['age'], data['email'], data['password'])
      return self.SuccesJsonResponse({"name": data.get('name'), "email": data.get('email'), "role": data.get('role')}, 201)
    except KeyError as e:
      return self.ErrorJsonResponse(list(e.args))
