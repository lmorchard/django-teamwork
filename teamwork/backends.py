from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from .models import Team, Role, RolePermission, Membership, TeamOwnership


class TeamworkBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    def get_group_permissions(self, user, obj=None):
        pass

    def get_all_permissions(self, user, obj=None):
        
        if (user.is_anonymous() or obj is None or not hasattr(obj, 'team') or
                not obj.team):
            return set()

        if not hasattr(obj, '_teamwork_perms_cache'):
            obj._teamwork_perms_cache = dict()

        # FIXME: Primary key is not always .id
        user_pk = user.id
        if not user_pk in obj._teamwork_perms_cache:
            ct = ContentType.objects.get_for_model(obj)
            relevant_role_ids = Membership.objects.filter(role__team=obj.team, user=user).values('role')
            perm_ids = RolePermission.objects.filter(role__in=relevant_role_ids).values('permission')
            perms = Permission.objects.filter(id__in=perm_ids, content_type=ct).select_related()
            named_perms = set([
                u"%s.%s" % (p.content_type.app_label, p.codename)
                for p in perms
            ])
            obj._teamwork_perms_cache[user_pk] = named_perms

        return obj._teamwork_perms_cache[user_pk]

    def has_perm(self, user, perm, obj=None):
        if not user.is_active:
            return False
        return perm in self.get_all_permissions(user, obj)

    def has_module_perms(self, user, app_label):
        pass
