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
    def get_teams_for_user(self, user):
        member_teams = (Role.users.through.objects
                            .filter(user=user)
                            .values('role__team').distinct())
        teams = self.filter(id__in=member_teams)
        return teams

    def get_team_roles_managed_by(self, manager_user, managed_user):
        """
        Assemble a list of roles collated by team, for which the manager_user
        has permission to manage users, annotated with which roles have been
        granted to the managed_user.
        """
        # Get a set of IDs for all the roles granted to the user in question.
        user_role_ids = set(
            r['role'] for r in
            Role.users.through.objects.filter(user=managed_user)
                                      .values('role'))

        # Join up roles managed by the auth'd user with roles granted to the
        # user in question.
        avail_roles = [
            dict(role=role, granted=(role.id in user_role_ids))
            for role in Role.objects.select_related('team').all()
            if manager_user.has_perm('teamwork.manage_role_users', role)
        ]

        # Extract the unique teams, indexed by ID
        teams = dict((r['role'].team.id, r['role'].team) for r in avail_roles)

        # Collate available roles by team
        return [
            (t[1], [r for r in avail_roles if r['role'].team.id == t[0]])
            for t in teams.items()
        ]


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    name = models.CharField(
        _("name"), max_length=128, editable=True, unique=True,
        db_index=True)
    description = models.TextField(
        _("Description of intended use"), null=True, blank=True)
    founder = models.ForeignKey(
        User, db_index=True, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    objects = TeamManager()

    class Meta:
        permissions = (
            ('view_team', 'Can view team'),
        )

    def __unicode__(self):
        return self.name

    @property
    def team(self):
        return self

    def has_user(self, user):
        """Determine whether the given user is a member of this team"""
        # TODO: founder is not considered a member without an associated role
        hits = (Role.users.through.objects
                    .filter(role__team=self, user=user)).count()
        return hits > 0

    def filter_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if user == self.founder:
            # Founder is admin-equivalent for the team
            if permissions is None:
                permissions = set()
            for perm, desc in self._meta.permissions:
                permissions.add('teamwork.%s' % perm)
        return permissions

    def get_all_permissions(self, user):
        """Get all Permissions applied to this User based on assigned Roles"""
        role_ids = (Role.users.through.objects
                        .filter(user=user, role__team=self)
                        .values('role'))
        return (p.permission for p in
                Role.permissions.through.objects
                    .filter(role__in=role_ids)
                    .select_related())


class RoleManager(models.Manager):
    """
    Manager and utilities for Roles
    """
    pass


class Role(models.Model):
    """
    Role within a Team for a user.

    This works somewhat like a Group, but its Permissions only apply when a
    User acts upon an object belonging to the Role's parent Team.
    """
    team = models.ForeignKey(Team, db_index=True, blank=False, null=False)
    name = models.CharField(_("name"), max_length=128, db_index=False)
    description = models.TextField(_("Description of intended use"),
                                   blank=True)

    permissions = models.ManyToManyField(
        Permission, blank=True,
        help_text='Specific permissions for this role.')

    users = models.ManyToManyField(
        User, blank=True,
        help_text='Users granted this role')

    objects = RoleManager()

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'team'),)
        permissions = (
            ('view_role', 'Can view role'),
            ('manage_role_permissions', 'Can manage role permissions'),
            ('manage_role_users', 'Can manage role users'),
        )

    def is_granted_to(self, user):
        """Return whether this role is granted to the given user"""
        return (self.users.filter(id=user.id).count() > 0)

    def filter_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if user == self.team.founder:
            # Founder is admin-equivalent for the team
            if permissions is None:
                permissions = set()
            for perm, desc in self._meta.permissions:
                permissions.add('teamwork.%s' % perm)
        return permissions

    def add_permissions_by_name(self, names, obj=None):
        from .shortcuts import get_permission_by_name
        self.permissions.add(*(get_permission_by_name(name, obj)
                             for name in names))


class PolicyManager(models.Manager):
    """
    Manager and utilities for Policies
    """
    def get_all_permissions(self, user, obj):
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
            return None
        return chain(*(policy.permissions.all() for policy in policies))


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
        related_name='permissions',
        verbose_name=_('permissions'),
        help_text='Permissions granted by this policy')

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
        self.permissions.add(*(get_permission_by_name(name, obj)
                             for name in names))
