from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse


@method_decorator(csrf_exempt, name="dispatch")
class BaseView(View):
    def SuccessJsonResponse(self, message="Success in operation!", data={}, status=200):
        return JsonResponse(
            {"message": message, "data": data}, status=status, safe=False
        )

    def ErrorJsonResponse(self, message="Fail in operation!", status=400):
        return JsonResponse({"error": message}, status=status, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class AuthBaseView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.ErrorJsonResponse("User not authenticated!", 401)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class ShopkeeperBaseView(AuthBaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["Shop", "Adm"]:
            return self.ErrorJsonResponse(
                "User don't have permission to this action!", 401
            )
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class ManagerBaseView(AuthBaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["Man", "Adm"]:
            return self.ErrorJsonResponse(
                "User don't have permission to this action!", 401
            )
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class CarrierBaseView(AuthBaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["Carr", "Adm"]:
            return self.ErrorJsonResponse(
                "User don't have permission to this action!", 401
            )
        return super().dispatch(request, *args, **kwargs)
