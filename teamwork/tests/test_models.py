import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy

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
        for role_user in Role.users.through.objects.all():
            role_user.role.team.has_user(role_user.user)
            user_teams = Team.objects.get_teams_for_user(role_user.user)
            ok_(role_user.role.team in user_teams)
