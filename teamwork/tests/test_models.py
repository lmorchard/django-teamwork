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
        # Not an exhaustive list, but should be decent.
        cases = (
            (True, 'alpha', 'tester1'),
            (True, 'alpha', 'tester2'),
            (True, 'beta',  'tester3'),
            (True, 'beta',  'tester4'),
            (True, 'gamma', 'tester4'),
            (True, 'gamma', 'tester5'),
            (True, 'gamma', 'tester6'),

            (False, 'beta',  'tester0'),
            (False, 'gamma', 'tester0'),
            (False, 'beta',  'tester2'),
            (False, 'alpha', 'tester3'),
            (False, 'alpha', 'tester4'),

            # TODO: The founder is not considered a member, lacking a Role
            (False, 'alpha', 'founder0'),
            (False, 'beta',  'founder1'),
            (False, 'gamma', 'founder2'),
        )
        for expected, team_name, user_name in cases:
            team = self.teams[team_name]
            user = self.users[user_name]
            eq_(expected, team.has_user(user))

    def test_teams_for_user(self):
        """List of teams for user should correspond to roles"""
        for member in self.members:
            member.role.team.has_user(member.user)
            user_teams = Team.objects.get_teams_for_user(member.user)
            ok_(member.role.team in user_teams)
