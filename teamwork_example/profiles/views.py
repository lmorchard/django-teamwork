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


def user_roles(request, username):
    if not request.user.is_authenticated():
        raise PermissionDenied

    # Get the user in question
    user = get_object_or_404(User, username=username)
    
    if 'POST' == request.method:
        role_id = request.POST.get('role_id')
        role = Role.objects.get(id=role_id)
        
        if not request.user.has_perm('teamwork.grant_roles', role.team):
            raise PermissionDenied
        
        if not request.user.has_perm('teamwork.manage_role_users', role):
            raise PermissionDenied

        is_granted = (role.users.filter(id=user.id).count() > 0)
        if is_granted:
            role.users.remove(user)
            messages.info(request, 'Revoked %s for %s from %s' %
                          (role, role.team, user))
        else:
            role.users.add(user)
            messages.info(request, 'Granted %s for %s to %s' %
                          (role, role.team, user))

        return redirect(reverse('profiles.views.user_roles',
                                args=(user.username,)))
    
    # Get a set of IDs for all the roles granted to the user in question.
    user_role_ids = set(r['role'] for r in
        Role.users.through.objects.filter(user=user).values('role'))

    # Build a set of all teams for which the auth'd user can grant roles
    teams = (team for team in Team.objects.all()
        if request.user.has_perm('teamwork.grant_roles', team))

    # Join up the roles by team for which the auth'd user can grant roles,
    # along with whether the user in question has been granted the role.
    roles_by_team = [
        (team, [
            dict(
                role=role,
                granted=(role.id in user_role_ids)
            ) 
            for role in team.role_set.all()
            if request.user.has_perm('teamwork.manage_role_users', role)
        ])
        for team in teams
    ]

    return render(request, 'profiles/user_roles.html', dict(
        user=user,
        roles_by_team=roles_by_team,
    ))

    #return HttpResponse('%s' % [[user_role_ids, roles_by_team]])


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
