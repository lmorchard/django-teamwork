from django.contrib.auth.models import User, Permission
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect)
import django.contrib.auth

from teamwork.models import Team, Role
from teamwork.shortcuts import get_object_or_404_or_403


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


def user_detail(request, username):
    """View a user profile"""
    # user = get_object_or_404_or_403('view_user', request.user,
    #                                 User, username=username)
    user = get_object_or_404(User, username=username)
    base_perms = user.get_all_permissions()
    roles = Role.objects.filter(users=user)

    return render(request, 'profiles/user_detail.html', dict(
        user=user, base_perms=base_perms, roles=roles
    ))


def team_detail(request, name):
    team = get_object_or_404_or_403('view_team', request.user,        
                                    Team, name=name)

    # TODO: Should this be a team model method?
    members = dict()
    for role in team.role_set.all():
        for user in role.users.all():
            username = user.username
            if username not in members:
                members[username] = dict(user=user, roles=[role])
            else:
                members[username]['roles'].append(role)

    return render(request, 'profiles/team_detail.html', dict(
        team=team,
        members=members.values(),
        roles=team.role_set.all(),
    ))
