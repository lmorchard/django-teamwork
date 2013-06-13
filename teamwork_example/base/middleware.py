from django.shortcuts import render
from django.contrib.auth.models import User


class UserListMiddleware(object):
    """
    Populates the login selector in the header
    """
    def process_request(self, request):
        request.user_list = User.objects.all()
        return None
