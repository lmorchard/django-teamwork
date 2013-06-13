import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role

from . import TestCaseBase


class TeamTests(TestCaseBase):

    def test_general_permissions(self):
        """Appropriate permissions for anonymous, authenticated, and members"""
        team = Team.objects.create(name='general_permissive_team',
                                   founder=self.users['founder0'])

        anon_user = AnonymousUser()
        auth_user = self.users['tester0']
        role_user = self.users['tester1']

        expected_anon_perms = set((u'can_frob', u'can_xyzzy'))
        expected_auth_perms = set((u'can_xyzzy', u'can_hello'))
        expected_role_perms = set((u'can_frob', u'can_hello'))

        perms = self.names_to_doc_permissions(expected_anon_perms)
        team.anonymous_permissions.add(*perms)

        perms = self.names_to_doc_permissions(expected_auth_perms)
        team.authenticated_permissions.add(*perms)

        role1 = Role.objects.create(name='role1', team=team)
        role1.users.add(role_user)

        perms = self.names_to_doc_permissions(expected_role_perms)
        role1.permissions.add(*perms)

        result_anon_perms = set(p.codename for p in
                                team.get_all_permissions(anon_user))
        eq_(expected_anon_perms, result_anon_perms)

        result_auth_perms = set(p.codename for p in
                                team.get_all_permissions(auth_user))
        eq_(expected_auth_perms, result_auth_perms)

        result_role_perms = set(p.codename for p in
                                team.get_all_permissions(role_user))
        eq_(expected_role_perms, result_role_perms)

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
