import logging
import time

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from ..models import Team, Role, Membership, TeamOwnership

from teamwork_example.models import Document

from . import TestCaseBase


class TeamTests(TestCaseBase):

    def test_has_member(self):
        """Users with roles on a team should be counted as members"""
        team = self.teams[0]

        # TODO: The founder is not considered a member, lacking a Role
        # ok_(team.has_user(self.users[0]))
        ok_(team.has_user(self.users[1]))
        ok_(team.has_user(self.users[2]))
        ok_(team.has_user(self.users[3]))
        ok_(not team.has_user(self.users[4]))

    def test_teams_for_user(self):
        """User with roles should be considered member of associated teams"""
        for member in self.members:
            member.role.team.has_user(member.user)
            user_teams = Team.objects.get_teams_for_user(member.user)
            ok_(member.role.team in user_teams)

    """
    def test_play(self):

        for t in self.teams:
            logging.debug("TEAM %s" % t)
            for r in t.role_set.all():
                logging.debug("\tROLE %s" % r)
                for p in r.permissions.all():
                    logging.debug("\t\tPERM %s" % p)

        ok_(False, "Still playing...")
    """
