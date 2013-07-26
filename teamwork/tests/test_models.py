import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from nose.tools import (assert_equal, assert_items_equal, with_setup,
                        assert_false, eq_, ok_)
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy

from . import TestCaseBase


class TeamTests(TestCaseBase):

    def test_unicode_repr(self):
        """Teamwork objects should have useful string representations"""
        team = Team.objects.create(name="foo")
        eq_("foo", unicode(team))

        role = Role.objects.create(team=team, name="bar")
        eq_("bar", unicode(role))

        doc = Document.objects.create(name="baz")
        policy = Policy.objects.create(content_object=doc)
        eq_("Policy(baz)", unicode(policy))

    def test_has_member(self):
        """Users with roles on a team should be counted as members"""
        cases = (
            (True, u'Section 1 Team', u'section1_leader'),
            (True, u'Section 1 Team', u'section1_editor'),
            (True, u'Section 2 Team', u'section2_leader'),
            (True, u'Section 2 Team', u'section2_editor'),
            (True, u'Section 3 Team', u'section3_leader'),
            (True, u'Section 3 Team', u'section3_editor'),
            (False, u'Section 1 Team', u'randomguy1'),
            (False, u'Section 2 Team', u'randomguy1'),
            (False, u'Section 3 Team', u'randomguy1'),
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

    def test_get_team_roles_managed_by(self):
        """get_team_roles_managed_by should assemble list of roles by team"""
        cases = [
            ('section1_leader', [
                ('Section 1 Team', [
                    {'granted': False, 'role': 'leader'},
                    {'granted': True, 'role': 'editor'}
                ])
            ]),
            ('section2_leader', [
                ('Section 2 Team', [
                    {'granted': False, 'role': 'leader'},
                    {'granted': False, 'role': 'editor'}
                ])
            ]),
            ('randomguy1', []),
        ]

        managed_user = self.users['section1_editor']
        for manager_username, expected in cases:
            manager_user = self.users[manager_username]
            result = Team.objects.get_team_roles_managed_by(
                manager_user, managed_user)
            for idx in range(0, len(expected)):
                ex_team_name = expected[idx][0]
                eq_(ex_team_name, result[idx][0].name)
                ex_roles, r_roles = expected[idx][1], result[idx][1]
                for s_idx in range(0, len(ex_roles)):
                    ex_role = ex_roles[s_idx]
                    r_role = r_roles[s_idx]
                    eq_(ex_role['granted'], r_role['granted'])
                    eq_(ex_role['role'], r_role['role'].name)
                    eq_(ex_team_name, r_role['role'].team.name)


class RoleTests(TestCaseBase):

    def test_is_granted(self):
        """Role.is_granted_to should indicate whether user has the role"""
        team = Team.objects.create(name="foo")
        role = Role.objects.create(team=team, name="bar")
        user1 = self.users['randomguy1']
        user2 = self.users['randomguy2']
        role.users.add(user1)
        eq_(True, role.is_granted_to(user1))
        eq_(False, role.is_granted_to(user2))
