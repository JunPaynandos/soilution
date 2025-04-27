# middleware.py
from django.shortcuts import redirect
from django.contrib.auth import logout

class InactiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            return redirect('pending_approval')  # Define this URL/view
        return self.get_response(request)
