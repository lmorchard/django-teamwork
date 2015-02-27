import logging
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site, get_current_site

from . import DEFAULT_ANONYMOUS_USER_PK
from .models import Team, Role, Policy


def merge_perms(sets):
    out = set()
    for perms in sets:
        for perm in perms:
            if perm.startswith('-'):
                out.discard(perm[1:])
            else:
                out.add(perm)
    return out


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    perms_cache = dict()

    def authenticate(self, username, password):
        return None

    def get_all_permissions(self, user, obj=None):
        # TODO: Cache this on the object? or in memcache?
        return merge_perms([
            self._get_settings_permissions(user, obj),
            self._get_site_permissions(user, obj),
            self._get_obj_permissions(user, obj)
        ])

    def _get_settings_permissions(self, user, obj=None):
        """
        Get permissions based on a baseline policy specified in settings.
        """
        policy = getattr(settings, 'TEAMWORK_BASE_POLICIES', None)
        if not policy:
            return set()

        sets = [ policy.get('all', []) ]

        if user.is_authenticated():
            sets.append(policy.get('authenticated', []))

            if obj:

                if ('owners' in policy and hasattr(obj, 'has_owner') and
                        obj.has_owner(user)):
                    sets.append(policy.get('owners', []))

                if ('members' in policy and hasattr(obj, 'team') and
                        obj.team and obj.team.has_member(user)):
                    sets.append(policy.get('members', []))
        
        group_perms = policy.get('groups', None)
        if group_perms:
            for group in user.groups.all():
                if group.name in group_perms:
                    sets.append(group_perms[group.name])

        users_perms = policy.get('users', dict())
        if user.username in users_perms:
            sets.append(users_perms[user.username])

        return merge_perms(sets)

    def _get_obj_permissions(self, user, obj, recurse=True):
        """Look up permissions for a single user / team / object"""
        if not obj:
            return set()

        names = []

        if recurse and hasattr(obj, 'get_permission_parents'):
            for parent in obj.get_permission_parents():
                names.extend(self._get_obj_permissions(user, parent, False))

        # TODO: Consider multiple-team ownership of a content object
        team = getattr(obj, 'team', None)
        if team and user.is_authenticated():
            
            names.extend(self._perms_to_names(
                team.get_all_permissions(user)))

            names.extend(self._perms_to_names(
                team.get_all_permissions(user, denied=True),
                denied=True))

        names.extend(self._perms_to_names(
            Policy.objects.get_all_permissions(user, obj)))

        names.extend(self._perms_to_names(
            Policy.objects.get_all_permissions(user, obj, denied=True),
            denied=True))

        if user.is_superuser:
            # Superuser is super, gets all object permissions
            ct = ContentType.objects.get_for_model(obj)
            perms = Permission.objects.filter(content_type=ct).all()
            names.extend(self._perms_to_names(perms))

        if hasattr(obj, 'filter_permissions'):
            names = obj.filter_permissions(user, set(names))

        return names

    def _get_site_permissions(self, user, obj=None):
        """
        Get policy permissions attached to the current Site, or the Site
        specified by an object, if any.
        """
        perms = None
        # TODO: Abstract this hardcoded 'site' field name
        curr_site = getattr(obj, 'site', None)
        if not curr_site:
            curr_site = Site.objects.get_current()
        # HACK: Ensure we have a current site, and that it is in fact a Site
        # object. This turns out to be a problem with mozilla/kuma, which mocks
        # out Site.objects.get_current() for some tests and doesn't result in a
        # real Site object.
        if curr_site and isinstance(curr_site, Site):
            raw_perms = Policy.objects.get_all_permissions(
                user, curr_site)
            if raw_perms is not None:
                perms = self._perms_to_names(raw_perms)
        return perms

    def has_perm(self, user, perm, obj=None):
        return perm in self.get_all_permissions(user, obj)

    def _perms_to_names(self, perms, denied=False):
        return set([u"%s%s.%s" % (denied and '-' or '',
                                  p.content_type.app_label,
                                  p.codename)
                    for p in perms])
