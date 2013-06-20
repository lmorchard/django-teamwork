import logging
from itertools import chain

from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.contrib.sites.models import Site, get_current_site

from . import DEFAULT_ANONYMOUS_USER_PK
from .models import Team, Role, Policy


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

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
        named_perms = self._perms_to_names(perms)

        if hasattr(obj, 'get_all_permissions'):
            # Allow the object to filter the permissions
            named_perms = obj.get_all_permissions(user, named_perms)

        return named_perms

    def _get_site_permissions(self, user, obj=None):
        """
        Get policy permissions attached to the current Site, or the Site
        specified by an object, if any.
        """
        # TODO: Abstract this hardcoded 'site' field name
        curr_site = getattr(obj, 'site', None)
        if not curr_site:
            curr_site = Site.objects.get_current()
        if curr_site:
            raw_perms = Policy.objects.get_all_permissions(
                user, curr_site)
            perms = self._perms_to_names(raw_perms)
        return perms

    def get_all_permissions(self, user, obj=None):

        if obj is None:
            return self._get_site_permissions(user)

        if user.is_anonymous():
            user_pk = DEFAULT_ANONYMOUS_USER_PK
        else:
            user_pk = user.pk

        if not hasattr(obj, '_teamwork_perms_cache'):
            obj._teamwork_perms_cache = dict()

        if not user_pk in obj._teamwork_perms_cache:

            # Try getting perms for the current object
            perms = self._get_obj_permissions(user, obj)

            # If the object yielded no perms, try traversing the parent chain
            if not perms and hasattr(obj, 'get_permission_parents'):
                parents = obj.get_permission_parents()
                for parent in parents:
                    perms = self._get_obj_permissions(user, parent)
                    if perms:
                        break

            # Last ditch for permissions is to look for policies attached to
            # the current Site object.
            if not perms:
                perms = self._get_site_permissions(user, obj)

            # Cache all this work...
            obj._teamwork_perms_cache[user_pk] = perms

        return obj._teamwork_perms_cache[user_pk]

    def has_perm(self, user, perm, obj=None):
        return perm in self.get_all_permissions(user, obj)
