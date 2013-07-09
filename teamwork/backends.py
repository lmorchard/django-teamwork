import logging
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site, get_current_site

from . import DEFAULT_ANONYMOUS_USER_PK
from .models import Team, Role, Policy


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    perms_cache = dict()

    def authenticate(self, username, password):
        return None

    def get_all_permissions(self, user, obj=None):

        if not obj:
            # If there's no obj, then much can be shortcircuited
            perms = self._get_site_permissions(user)
            if perms is None:
                perms = self._get_settings_permissions(user)
            if perms is None:
                perms = set()
            return perms

        if user.is_anonymous():
            user_pk = DEFAULT_ANONYMOUS_USER_PK
        else:
            user_pk = user.pk

        # TODO: Stash this in the global django cache (ie. memcache)?
        if not hasattr(obj, '_teamwork_perms_cache'):
            obj._teamwork_perms_cache = dict()

        if not user_pk in obj._teamwork_perms_cache:

            # Try getting perms for the current object
            perms = self._get_obj_permissions(user, obj)

            # If the object yielded no perms, try traversing parents
            if perms is None and hasattr(obj, 'get_permission_parents'):
                parents = obj.get_permission_parents()
                for parent in parents:
                    perms = self._get_obj_permissions(user, parent)
                    if perms is not None:
                        break

            # Check for policies attached to the current Site object, if any.
            if perms is None:
                perms = self._get_site_permissions(user, obj)

            # Consult settings for a baseline policy.
            if perms is None:
                perms = self._get_settings_permissions(user, obj)

            # If none of the above came up with permissions (even an empty
            # set), then we have an empty set.
            if perms is None:
                perms = set()

            # Cache all this work...
            obj._teamwork_perms_cache[user_pk] = perms

        return obj._teamwork_perms_cache[user_pk]

    def has_perm(self, user, perm, obj=None):
        return perm in self.get_all_permissions(user, obj)

    def _perms_to_names(self, perms):
        return set([u"%s.%s" % (p.content_type.app_label, p.codename)
                    for p in perms])

    def _get_obj_permissions(self, user, obj):
        """Look up permissions for a single user / team / object"""
        ct = ContentType.objects.get_for_model(obj)

        # TODO: Consider multiple-team ownership of a content object
        team = getattr(obj, 'team', None)

        if user.is_superuser:
            # Superuser is super, gets all object permissions
            perms = Permission.objects.filter(content_type=ct).all()
        elif user.is_anonymous() or not team or not team.has_user(user):
            # Policies apply to anonymous users and non-team members
            perms = Policy.objects.get_all_permissions(user, obj)
        else:
            # Team permissions apply to team members
            perms = team.get_all_permissions(user)

        # Map the permissions down to a set of app.codename strings
        if perms is None:
            named_perms = None
        else:
            named_perms = self._perms_to_names(perms)

        if hasattr(obj, 'filter_permissions'):
            # Allow the object to filter the permissions
            named_perms = obj.filter_permissions(user, named_perms)

        return named_perms

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

    def _get_settings_permissions(self, user, obj=None):
        """
        Get permissions based on a baseline policy specified in settings.
        """
        policy = getattr(settings, 'TEAMWORK_BASE_POLICIES', None)
        if not policy:
            return None

        if user.is_anonymous():
            return policy.get('anonymous', set())

        perms = set()

        if user.is_authenticated():
            perms.update(policy.get('authenticated', set()))

        users_perms = policy.get('users', dict())
        if user.username in users_perms:
            perms.update(users_perms[user.username])

        group_perms = policy.get('groups', None)
        if group_perms:
            for group in user.groups.all():
                if group.name in group_perms:
                    perms.update(group_perms[group.name])

        if (obj and 'apply_to_owners' in policy and
                    hasattr(obj, 'get_owner_user') and
                    user == obj.get_owner_user()):
            perms.update(policy['apply_to_owners'])

        return perms
