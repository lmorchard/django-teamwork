import logging
from itertools import chain

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
            ('can_add_role', 'Can add role'),
            ('can_change_role', 'Can change role'),
            ('can_delete_role', 'Can delete role'),
            ('can_add_member', 'Can add member'),
            ('can_change_member', 'Can change member'),
            ('can_delete_member', 'Can delete member'),
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

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,) + self.team.natural_key()
    natural_key.dependencies = ['teamwork.team']


class PolicyManager(models.Manager):

    def get_all_permissions(self, user, obj):
        ct = ContentType.objects.get_for_model(obj)
        policies = self.filter(content_type__pk=ct.id, object_id=obj.id)
        if 0 == policies.count():
            return []
        if user.is_anonymous():
            fld = 'anonymous_permissions'
        else:
            fld = 'authenticated_permissions'
        return chain(*(getattr(policy, fld).all()
                       for policy in policies))


class Policy(models.Model):
    """
    Per-object assembly of permissions granted by a content object to anonymous
    and authenticated users.
    """
    team = models.ForeignKey(
        Team, db_index=True, blank=True, null=True,
        help_text='Team responsible for managing this policy')
    creator = models.ForeignKey(User, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    content_object = generic.GenericForeignKey('content_type', 'object_id')

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

    objects = PolicyManager()

    class Meta:
        verbose_name_plural = _('Policies')

    def __unicode__(self):
        return u'Policy(%s)' % self.content_object
