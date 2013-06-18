import logging
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.db import models, transaction
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.utils.translation import ugettext_lazy as _


class TeamManager(models.Manager):
    """
    Manager and utilities for Teams
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)

    def get_teams_for_user(self, user):
        member_teams = (Role.users.through.objects
                            .filter(user=user)
                            .values('role__team').distinct())
        teams = self.filter(id__in=member_teams)
        return teams


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    name = models.CharField(
        _("name"), max_length=128, editable=True, unique=True,
        db_index=True)
    description = models.TextField(
        _("Description of intended use"), blank=False)
    founder = models.ForeignKey(
        User, db_index=True, blank=False, null=False)

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
        return (self.name,)

    def has_member(self, user, role):
        """Determine whether the given user is a member of this team"""
        # TODO: founder is not considered a member without an associated role
        hits = (Role.users.through.objects
                    .filter(role__team=self, user=user).count())
        return hits > 0

    def get_members(self):
        """Convenience property with a QuerySet of user/role RoleUser"""
        return RoleUser.objects.filter(role__team=self)

    def has_user(self, user):
        """Determine whether the given user is a member of this team"""
        # TODO: founder is not considered a member without an associated role
        hits = (Role.users.through.objects
                    .filter(role__team=self, user=user)).count()
        return hits > 0

    def get_users(self):
        """Convenience property with a QuerySet of unique users"""
        members = (Role.user.through.objects
                       .filter(role__team=self)
                       .values('user').distinct())
        return User.objects.filter(id__in=members)

    def get_all_permissions(self, user):
        """Get all Permissions applied to this User based on assigned Roles"""
        # TODO: Keep thinking about how to simplify these queries
        if user.is_anonymous():
            return []

        role_ids = (Role.users.through.objects
                        .filter(user=user, role__team=self)
                        .values('role'))

        if 0 == len(role_ids):
            return []

        return (p.permission for p in
                Role.permissions.through.objects
                    .filter(role__in=role_ids)
                    .select_related())


class RoleManager(models.Manager):
    """
    Manager and utilities for Roles
    """
    def get_by_natural_key(self, name, team_name):
        return self.get(
            name=name,
            team=Team.objects.get_by_natural_key(team_name)
        )


class Role(models.Model):
    """
    Role within a Team for a user.

    This works somewhat like a Group, but its Permissions only apply when a
    User acts upon an object belonging to the Role's parent Team.
    """
    team = models.ForeignKey(Team, db_index=True, blank=False, null=False)
    name = models.CharField(_("name"), max_length=128, db_index=False)
    description = models.TextField(_("Description of intended use"),
                                   blank=False)

    permissions = models.ManyToManyField(
        Permission, blank=True,
        help_text='Specific permissions for this role.')

    users = models.ManyToManyField(
        User, blank=True,
        help_text='Users granted this role')

    objects = RoleManager()

    class Meta:
        unique_together = (('name', 'team'),)
        permissions = (
            ('view_role', 'Can view role'),
            ('manage_permissions', 'Can manage role permissions'),
            ('manage_users', 'Can manage role users'),
        )

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,) + self.team.natural_key()
    natural_key.dependencies = ['teamwork.team']


class PolicyManager(models.Manager):
    """
    Manager and utilities for Policies
    """
    def get_all_permissions(self, user, obj):
        if user.is_anonymous():
            user_filter = Q(anonymous=True)
        elif user.is_authenticated():
            groups = user.groups.all().values('id')
            user_filter = (Q(authenticated=True) |
                           Q(users__pk=user.pk) |
                           Q(groups__in=groups))
            if (hasattr(obj, 'get_owner_user') and
                    user == obj.get_owner_user()):
                user_filter |= Q(apply_to_owners=True)
        else:
            return []
        ct = ContentType.objects.get_for_model(obj)
        policies = self.filter(user_filter,
                               content_type__pk=ct.id,
                               object_id=obj.id).all()
        return chain(*(policy.permissions.all() for policy in policies))


class Policy(models.Model):
    """
    Permissions granted by an object to users matching various criteria
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creator = models.ForeignKey(User, null=True)
    team = models.ForeignKey(
        Team, db_index=True, blank=True, null=True,
        help_text='Team responsible for managing this policy')

    apply_to_owners = models.BooleanField(default=False, help_text=(
        'Apply this policy to owners of content objects?'))
    anonymous = models.BooleanField(default=False, help_text=(
        'Apply this policy to anonymous users?'))
    authenticated = models.BooleanField(default=False, help_text=(
        'Apply this policy to authenticated users?'))
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
            ('manage_permissions', 'Can manage role permissions'),
            ('manage_users', 'Can manage role users'),
            ('manage_groups', 'Can manage role groups'),
        )

    def __unicode__(self):
        return u'Policy(%s)' % self.content_object
