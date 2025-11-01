import json
from django.http import JsonResponse
from django.views import View
from app.models import Usuario, Address
from app.cruds.user_crud import UserCrud
from app.cruds.address_crud import AddressCrud
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict


@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):
  #Personalizar o status number com base na operação 200 = OK, 201 = CREATED
  def SuccessJsonResponse(self, message='Success in operation!', data={}, status=200):
    return JsonResponse({'message': message, 'data': data}, status=status, safe=False)
  #Mesma coisa da success, 400 = Bad Request, 401 = Unauthorized, 404 = Not Found
  #Se ficar com duvidas só pesquisar HTTP status numbers (http cats também é maneiro)
  def ErrorJsonResponse(self, message='Fail in operation!', status=400):
    return JsonResponse({'error': message}, status=status, safe=False)

#Todas as classes que herdarem essa view, só funcionam com autenticação
class AuthBaseView(BaseView):
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
      return self.ErrorJsonResponse("User not authenticated!", 401)
    return super().dispatch(request, *args, **kwargs)

#Routes whithout auth
class LoginView(BaseView):
  def post(self, request, *args, **kwargs):
    data = json.loads(request.body)
    user = authenticate(email=data['email'], password=data['password'])
    if user is not None:
      login(request, user)
      return self.SuccessJsonResponse("User successfully logged in!", model_to_dict(user))
    return self.ErrorJsonResponse("Invalid credentials!")

class LogoutView(BaseView):
  def post(self, request, *args, **kwargs):
   try:
     logout(request)
     return self.SuccessJsonResponse("User successfully logged out!")
   except Exception as e:
     return self.ErrorJsonResponse("Error logging out!", e.args[0])

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
#Routes whith auth
class UserAPIView(AuthBaseView):
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

class ChangePasswordView(AuthBaseView):
  def put(self, request, *args, **kwargs):
    try:
      data = json.loads(request.body)
      user = UserCrud.read_by_email(kwargs['email'])
      UserCrud.change_password(user.id, data.get('old_password'), data.get('new_password'))
      return self.SuccessJsonResponse("Password successfully changed!", {"new_password": data.get('new_password')})
    except ValueError as e:
      return self.ErrorJsonResponse("Invalid old password!")

@method_decorator(csrf_exempt, name='dispatch')
class AddressesAPIView(AuthBaseView):
  def post(self, request, *args, **kwargs):
      try:
        data = json.loads(request.body)
        AddressCrud.create(data["street"], data["number"], data["complement"], data["neighborhood"], data["city"], data["state"], data["cep"], data["country"])
        return self.SuccessJsonResponse("Address successfully created", {"street": data.get('street'), "number": data.get('number'), "complement": data.get('complement'), "neighborhood": data.get('neighborhood'), "city": data.get('city'), "state": data.get('state'), "cep": data.get('cep'), "country": data.get('country')}, 201)
      except KeyError as e:
        return self.ErrorJsonResponse(e.args)
      
  def get(self, request, *args, **kwargs):
    addresses = AddressCrud.read().values()
    if not addresses:
      return self.ErrorJsonResponse("Addresses not founded!")

    return self.SuccessJsonResponse('Addresses successfully retrieved!',list(addresses))

@method_decorator(csrf_exempt, name='dispatch')
class AddressAPIView(AuthBaseView):
    def get(self, request, *args, **kwargs):
      try:
        address = Address.objects.get(id=kwargs['id'])
        return self.SuccessJsonResponse("Address successfully retrieved!",{"street": address.street, "number": address.number, "complement": address.complement, "neighborhood": address.neighborhood, "city": address.city, "state": address.state, "cep": address.cep, "country": address.country}, 200)
      except Address.DoesNotExist:
        return self.ErrorJsonResponse("Address not found", 404)

    def put(self, request, *args, **kwargs):
      try:
        data = json.loads(request.body)
        address = Address.objects.get(id=kwargs['id'])
        AddressCrud.update(address.id, **data)
        return self.SuccessJsonResponse({"message": "Address successfully updated!", "data": data })
      except KeyError as e:
        return self.ErrorJsonResponse(e.args)
      except Address.DoesNotExist:
        return self.ErrorJsonResponse("Address not found")
    
    def delete(self, request, *args, **kwargs):
      try:
        address = Address.objects.get(id=kwargs['id'])
        AddressCrud.delete(address.id)
        return self.SuccessJsonResponse("Address successfully deleted!")
      except Address.DoesNotExist:
        return self.ErrorJsonResponse("Address not found", 404)