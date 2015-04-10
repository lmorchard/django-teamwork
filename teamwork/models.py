import logging
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Group, Permission
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
        return Team.objects.filter(members__pk=user.pk)


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    name = models.CharField(
        _("name"), max_length=128, editable=True, unique=True,
        db_index=True)

    description = models.TextField(_("Description"), null=True, blank=True)

    members = models.ManyToManyField(User, through='Member')

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

    @property
    def team(self):
        return self

    def add_member(self, user, is_owner=False, role=None):
        (member, created) = Member.objects.get_or_create(team=self, user=user)
        member.role = role
        member.is_owner = is_owner
        member.save()
        return member

    def remove_member(self, user):
        Member.objects.filter(team=self, user=user).delete()

    def has_member(self, user):
        """Determine whether the given user is a member of this team"""
        return (self.members.through.objects
                    .filter(team=self, user=user).count() > 0)

    def has_owner(self, user):
        """Determine whether the given user is an owner of this team"""
        if user.is_anonymous():
            return False
        return (self.members.through.objects
                    .filter(team=self, user=user, is_owner=True).count() > 0)

    def filter_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if self.has_owner(user):
            # owner is admin-equivalent for the team
            for perm, desc in self._meta.permissions:
                permissions.add('teamwork.%s' % perm)
        return permissions

    def get_all_permissions(self, user, denied=False):
        """Get all Permissions applied to this User based on assigned Roles"""
        out = []
        for member in self.members.through.objects.filter(team=self, user=user):
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

    description = models.TextField(_("Description of intended use"), blank=True)

    permissions = models.ManyToManyField(
        Permission, blank=True, related_name='roles_granted',
        help_text='Specific permissions for this role.')

    permissions_denied = models.ManyToManyField(
        Permission, blank=True, related_name='roles_denied',
        help_text='Specific permissions denied for this role.')

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

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
        if self.team.has_owner(user):
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

    def get_by_natural_key(self, team_name, username):
        return self.get(team__name=name, user__username=username)


class Member(models.Model):
    """
    Through model representing Team member Users, with annotations on granted
    role and Team ownership status.
    """
    team = models.ForeignKey(Team, db_index=True)
    user = models.ForeignKey(User, db_index=True)

    role = models.ForeignKey(Role, db_index=True, null=True)
    is_owner = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    class Meta:
        unique_together = (('team', 'user'),)

    objects = MemberManager()

    def natural_key(self):
        return [self.team.name, self.user.username]

    def get_permission_parents(self):
        return [ self.team, ]

    def has_owner(self, user):
        return user == self.user


class PolicyManager(models.Manager):
    """
    Manager and utilities for Policies
    """
    def get_all_permissions(self, user, obj, denied=False):
        
        user_filter = Q(all=True)

        if user.is_authenticated():
            
            groups = user.groups.all().values('id')
            
            user_filter |= (Q(authenticated=True) |
                            Q(users__pk=user.pk) |
                            Q(groups__in=groups))
        
            if hasattr(obj, 'has_owner') and obj.has_owner(user):
                user_filter |= Q(owners=True)
        
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

    creator = models.ForeignKey(User, null=True, blank=True, related_name='creator')
    team = models.ForeignKey(
        Team, db_index=True, blank=True, null=True,
        help_text='Team responsible for managing this policy')

    all = models.BooleanField(default=False, help_text=(
        'Apply this policy to all users?'))
    authenticated = models.BooleanField(default=False, help_text=(
        'Apply this policy to authenticated users?'))
    owners = models.BooleanField(default=False, help_text=(
        'Apply this policy to owners of content objects?'))
    users = models.ManyToManyField(
        User, blank=True,
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
        verbose_name=_('permissions denied'),
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
