from myApp.models import User
import json
from django.http import JsonResponse


class FakeUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Create a fake user and set it as the user attribute of the request

        try:
            kwargs: dict = json.loads(request.body)
            user_id = kwargs.get("userId", 1)
            request.user = User.objects.get(id=user_id)
        except Exception:
            request.user = User.objects.get(id=1)

        return self.get_response(request)