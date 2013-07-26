from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
import django.contrib.auth

from .models import Team, Role
from .shortcuts import get_object_or_404_or_403


def user_roles(request, username):
    user = get_object_or_404(User, username=username)

    if 'POST' == request.method:

        role = get_object_or_404_or_403(
            'teamwork.manage_role_users', request.user,
            Role, id=request.POST.get('role_id'))

        if role.is_granted_to(user):
            role.users.remove(user)
            messages.info(request, _('Revoked %s for %s from %s') %
                          (role, role.team, user))
        else:
            role.users.add(user)
            messages.info(request, _('Granted %s for %s to %s') %
                          (role, role.team, user))

        return redirect(reverse('teamwork.views.user_roles',
                                args=(user.username,)))

    roles_by_team = Team.objects.get_team_roles_managed_by(request.user, user)

    return render(request, 'teamwork/user_roles.html', dict(
        user=user,
        roles_by_team=roles_by_team,
    ))
