import logging
from itertools import chain

from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from . import DEFAULT_ANONYMOUS_USER_PK
from .models import Team, Role, Policy


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    def get_all_permissions(self, user, obj=None):

        if obj is None:
            return set()

        # TODO: Consider multiple-team ownership of a content object
        team = getattr(obj, 'team', None)

        if user.is_anonymous():
            user_pk = DEFAULT_ANONYMOUS_USER_PK
        else:
            user_pk = user.pk

        if not hasattr(obj, '_teamwork_perms_cache'):
            obj._teamwork_perms_cache = dict()

        if not user_pk in obj._teamwork_perms_cache:
            ct = ContentType.objects.get_for_model(obj)
            if user.is_anonymous() or not team or not team.has_user(user):
                # Policies apply to anonymous users and non-team members
                perms = Policy.objects.get_all_permissions(user, obj)
            else:
                # Team permissions apply to team members
                perms = team.get_all_permissions(user)

            # Map the permissions down to a set of app.codename strings
            named_perms = set([u"%s.%s" % (ct.app_label, p.codename)
                               for p in perms])

            if hasattr(obj, 'get_all_permissions'):
                # Allow the object to filter the permissions
                named_perms = obj.get_all_permissions(user, named_perms)

            obj._teamwork_perms_cache[user_pk] = named_perms

        return obj._teamwork_perms_cache[user_pk]

    def has_perm(self, user, perm, obj=None):
        if not user.is_active:
            return False
        return perm in self.get_all_permissions(user, obj)
