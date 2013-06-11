from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from .models import Team, Role, RolePermission, Membership, TeamOwnership


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    def get_all_permissions(self, user, obj=None):

        if (user.is_anonymous() or (obj is None) or
                (not hasattr(obj, 'team')) or (not obj.team)):
            return set()

        # TODO: Consider multiple-team ownership of a content object
        team = obj.team

        if not hasattr(obj, '_teamwork_perms_cache'):
            obj._teamwork_perms_cache = dict()

        # FIXME: Primary key is not always .id
        user_pk = user.id
        if not user_pk in obj._teamwork_perms_cache:
            # TODO: Keep thinking about how to simplify these queries
            role_ids = (Membership.objects
                                  .filter(user=user, role__team=team)
                                  .values('role'))
            if 0 == len(role_ids):
                perms = set()
            else:
                ct = ContentType.objects.get_for_model(obj)
                rps = (RolePermission.objects
                                     .filter(role__in=role_ids)
                                     .select_related())
                perms = set([u"%s.%s" % (ct.app_label,
                                         rp.permission.codename)
                            for rp in rps])

            obj._teamwork_perms_cache[user_pk] = perms

        return obj._teamwork_perms_cache[user_pk]

    def has_perm(self, user, perm, obj=None):
        if not user.is_active:
            return False
        return perm in self.get_all_permissions(user, obj)
