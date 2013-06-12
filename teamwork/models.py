import logging

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db import models, transaction
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.utils.translation import ugettext_lazy as _


class TeamManager(models.Manager):
    """
    Manager and utilities for Teams
    """
    def get_teams_for_user(self, user):
        member_teams = (RoleUser.objects.filter(user=user)
                        .values('role__team').distinct())
        teams = self.filter(id__in=member_teams)
        return teams


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    name = models.CharField(_("name"),
                            max_length=128, editable=True, db_index=True)
    description = models.TextField(_("Description of intended use"),
                                   blank=False)
    founder = models.ForeignKey(User, editable=False, db_index=True,
                                blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    anonymous_permissions = models.ManyToManyField(
        Permission, blank=True,
        related_name='anonymous_permissions',
        verbose_name=_('anonymous permissions'),
        help_text='Permissions offered to anonymous users')

    authenticated_permissions = models.ManyToManyField(
        Permission, blank=True,
        related_name='authenticated_permissions',
        verbose_name=_('authenticated permissions'),
        help_text='Permissions offered to authenticated non-members')

    objects = TeamManager()

    class Meta:
        permissions = (
            ('view_team', 'Can view team'),
            ('can_add_role', 'Can add role'),
            ('can_change_role', 'Can change role'),
            ('can_delete_role', 'Can delete role'),
            ('can_add_member', 'Can add member'),
            ('can_change_member', 'Can change member'),
            ('can_delete_member', 'Can delete member'),
        )

    def __unicode__(self):
        return u'[Team %s]' % (self.name)

    def has_member(self, user, role):
        """Determine whether the given user is a member of this team"""
        # TODO: founder is not considered a member without an associated role
        hits = RoleUser.objects.filter(role__team=self, user=user).count()
        return hits > 0

    def get_members(self):
        """Convenience property with a QuerySet of user/role RoleUser"""
        return RoleUser.objects.filter(role__team=self)

    def has_user(self, user):
        """Determine whether the given user is a member of this team"""
        # TODO: founder is not considered a member without an associated role
        hits = RoleUser.objects.filter(role__team=self, user=user).count()
        return hits > 0

    def get_users(self):
        """Convenience property with a QuerySet of unique users"""
        members = (RoleUser.objects.filter(role__team=self)
                           .values('user').distinct())
        return User.objects.filter(id__in=members)

    def get_all_permissions(self, user):
        """Get all Permissions applied to this User based on assigned Roles"""
        # TODO: Keep thinking about how to simplify these queries
        if user.is_anonymous():
            return self.anonymous_permissions.all()

        role_ids = (RoleUser.objects.filter(user=user, role__team=self)
                            .values('role'))
        if 0 == len(role_ids):
            return self.authenticated_permissions.all()

        return (p.permission for p in
                RolePermission.objects.filter(role__in=role_ids)
                              .select_related())


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
        Permission, through='RolePermission', blank=True,
        verbose_name=_('role permissions'),
        help_text='Specific permissions for this role.')

    users = models.ManyToManyField(
        User, through='RoleUser', blank=True,
        verbose_name=_('role users'),
        help_text='Users granted this role')

    def __unicode__(self):
        return u'[Role %s for %s]' % (self.name, self.team)

    def assign_to(self, user):
        """Add user as a team member with the given role"""
        member, created = RoleUser.objects.get_or_create(user=user,
                                                         role=self)
        return member

    def add_permission(self, permission):
        rperm, created = RolePermission.objects.get_or_create(
            permission=permission, role=self)
        return rperm


class RolePermission(models.Model):
    """
    Permission associated with a role
    """
    role = models.ForeignKey(Role)
    permission = models.ForeignKey(Permission)
    created = models.DateTimeField(auto_now_add=True, db_index=True)


class RoleUser(models.Model):
    """
    Team RoleUser by role for a user
    """
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return u'[%s <- %s]' % (self.user, self.role)


class TeamOwnership(models.Model):
    """Claim of ownership by a team over a content object"""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
