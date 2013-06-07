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
        member_teams = (Membership.objects.filter(user=user)
                                          .values('role__team')
                                          .distinct())
        teams = self.filter(id__in=member_teams)
        return teams


class Team(models.Model):
    """
    Organizational unit for a set of users with assigned roles
    """
    objects = TeamManager()

    title = models.CharField(_("title"),
                             max_length=128, editable=True, db_index=True)
    description = models.TextField(_("Description of intended use"),
                                   blank=False)
    founder = models.ForeignKey(User, editable=False, db_index=True,
                                blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, null=True, db_index=True)

    def __unicode__(self):
        return u'[Team %s]' % (self.title)

    def has_member(self, user):
        """Determine whether the given user is a member of this team"""
        hits = Membership.objects.filter(role__team=self, user=user).count()
        return hits > 0

    @property
    def users(self):
        """Convenience property with a QuerySet of unique users"""
        members = (Membership.objects.filter(role__team=self)
                                     .values('user').distinct())
        return User.objects.filter(id__in=members)

    @property
    def members(self):
        """Convenience property with a QuerySet of Membership models"""
        return Membership.objects.filter(role__team=self)


class Role(models.Model):
    """
    Role within a Team for a user.
    """
    team = models.ForeignKey(Team, db_index=True, blank=False, null=False)
    name = models.CharField(_("name"), max_length=128, db_index=False)
    description = models.TextField(_("Description of intended use"),
                                   blank=False)

    permissions = models.ManyToManyField(
        Permission, verbose_name=_('role permissions'), blank=True,
        help_text='Specific permissions for this role.')

    users = models.ManyToManyField(
        User, through='Membership', blank=True,
        verbose_name=_('role users'),
        help_text='Users granted this role')

    def __unicode__(self):
        return u'[Role %s for %s]' % (self.name, self.team)


class Membership(models.Model):
    """
    Team membership by role for a user
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
