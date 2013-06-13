from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Permission
import django.contrib.auth

def login(request):
    """A horrible, terrible way to log in"""
    username = request.REQUEST.get('username', None)
    user = get_object_or_404(User, username=username)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    django.contrib.auth.login(request, user)
    return redirect('/')

def logout(request):
    """Not a great way to log out, either."""
    django.contrib.auth.logout(request)
    return redirect('/')
