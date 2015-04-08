from django.shortcuts import render
from django.contrib.auth import get_user_model


class UserListMiddleware(object):
    """
    Populates the login selector in the header
    """
    def process_request(self, request):
        request.user_list = get_user_model().objects.all()
        request.base_perms = request.user.get_all_permissions()
        return None
