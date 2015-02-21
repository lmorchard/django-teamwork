import logging
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class TeamManager(models.Manager):
    """
    Manager and utilities for Teams
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)

    def get_teams_for_user(self, user):
        return [member.team for member in
                Member.objects.select_related('team').filter(user=user)]


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    name = models.CharField(
        _("name"), max_length=128, editable=True, unique=True,
        db_index=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    owner = models.ForeignKey(
        User, related_name='owned_teams', db_index=True, blank=False, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    objects = TeamManager()

    class Meta:
        permissions = (
            ('view_team', 'Can view team'),
        )

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return self.name

    def get_owner_user(self):
        return self.owner

    @property
    def team(self):
        return self

    def add_member(self, user, role=None):
        member = Member(team=self, user=user, role=role)
        member.save()
        return member

    def has_user(self, user):
        """Determine whether the given user is a member of this team"""
        # TODO: owner is not considered a member without an associated role
        return Member.objects.filter(team=self, user=user).count() > 0

    def filter_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if user == self.owner:
            # owner is admin-equivalent for the team
            for perm, desc in self._meta.permissions:
                permissions.add('teamwork.%s' % perm)
        return permissions

    def get_all_permissions(self, user, denied=False):
        """Get all Permissions applied to this User based on assigned Roles"""
        out = []
        for member in Member.objects.filter(user=user, team=self):
            if member.role:
                permission_set = (denied and
                        member.role.permissions_denied or
                        member.role.permissions)
                out.extend(permission_set.all())
        return out


class RoleManager(models.Manager):
    """
    Manager and utilities for Roles
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Role(models.Model):
    """
    Role within a Team for a user.

    This works somewhat like a Group, but its Permissions only apply when a
    User acts upon an object belonging to the Role's parent Team.
    """
    name = models.CharField(_("name"), max_length=128, db_index=False, unique=True)
    team = models.ForeignKey(Team, db_index=True, blank=True, null=True)
    description = models.TextField(_("Description of intended use"),
                                   blank=True)
    permissions = models.ManyToManyField(
        Permission, blank=True, related_name='roles_granted',
        help_text='Specific permissions for this role.')
    permissions_denied = models.ManyToManyField(
        Permission, blank=True, related_name='roles_denied',
        help_text='Specific permissions denied for this role.')

    objects = RoleManager()

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return self.name

    class Meta:
        permissions = (
            ('view_role', 'Can view role'),
            ('manage_role_permissions', 'Can manage role permissions'),
        )

    def filter_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if user == self.team.owner:
            # owner is admin-equivalent for the team
            if permissions is None:
                permissions = set()
            for perm, desc in self._meta.permissions:
                permissions.add('teamwork.%s' % perm)
        return permissions

    def add_permissions_by_name(self, names, obj=None):
        from .shortcuts import get_permission_by_name
        self.permissions.add(
                *(get_permission_by_name(name, obj)
                for name in names if not name.startswith('-')))
        self.permissions_denied.add(
                *(get_permission_by_name(name[1:], obj)
                for name in names if name.startswith('-')))


class MemberManager(models.Manager):
    pass


class Member(models.Model):
    team = models.ForeignKey(Team, db_index=True, blank=False, null=False)
    user = models.ForeignKey(User, db_index=True, blank=False, null=False)
    role = models.ForeignKey(Role, db_index=True, blank=True, null=True)

    objects = MemberManager()


class PolicyManager(models.Manager):
    """
    Manager and utilities for Policies
    """
    def get_all_permissions(self, user, obj, denied=False):
        if user.is_anonymous():
            user_filter = Q(anonymous=True)
        else:
            groups = user.groups.all().values('id')
            user_filter = (Q(authenticated=True) |
                           Q(users__pk=user.pk) |
                           Q(groups__in=groups))
            if (hasattr(obj, 'get_owner_user') and
                    user == obj.get_owner_user()):
                user_filter |= Q(apply_to_owners=True)
        ct = ContentType.objects.get_for_model(obj)
        policies = self.filter(user_filter,
                               content_type__pk=ct.id,
                               object_id=obj.id).all()
        if 0 == len(policies):
            return set()

        return chain(*(
            (denied and policy.permissions_denied or policy.permissions).all()
            for policy in policies))


class Policy(models.Model):
    """
    Permissions granted by an object to users matching various criteria
    """
    description = models.TextField(_("Description of policy"),
                                   blank=False, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creator = models.ForeignKey(User, null=True, blank=True)
    team = models.ForeignKey(
        Team, db_index=True, blank=True, null=True,
        help_text='Team responsible for managing this policy')

    anonymous = models.BooleanField(default=False, help_text=(
        'Apply this policy to anonymous users?'))
    authenticated = models.BooleanField(default=False, help_text=(
        'Apply this policy to authenticated users?'))
    apply_to_owners = models.BooleanField(default=False, help_text=(
        'Apply this policy to owners of content objects?'))
    users = models.ManyToManyField(
        User, blank=True, related_name='users',
        help_text=('Apply this policy for these users.'))
    groups = models.ManyToManyField(Group, blank=True, help_text=(
        'Apply this policy for these user groups.'))

    permissions = models.ManyToManyField(
        Permission, blank=True,
        related_name='policies_granted',
        verbose_name=_('permissions'),
        help_text='Permissions granted by this policy')

    permissions_denied = models.ManyToManyField(
        Permission, blank=True,
        related_name='policies_denied',
        verbose_name=_('permissions'),
        help_text='Permissions denied by this policy')

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    objects = PolicyManager()

    class Meta:
        verbose_name_plural = _('Policies')
        permissions = (
            ('view_policy', 'Can view policy'),
        )

    def __unicode__(self):
        return u'Policy(%s)' % self.content_object

    def add_permissions_by_name(self, names, obj=None):
        
        from .shortcuts import get_permission_by_name
        if obj is None:
            obj = self.content_object

        self.permissions.add(
                *(get_permission_by_name(name, obj)
                for name in names if not name.startswith('-')))
        self.permissions_denied.add(
                *(get_permission_by_name(name[1:], obj)
                for name in names if name.startswith('-')))
