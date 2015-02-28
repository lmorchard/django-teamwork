import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from nose.tools import (assert_equal, assert_items_equal, with_setup,
                        assert_false, eq_, ok_)
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy, Member

from . import TestCaseBase


class TeamTests(TestCaseBase):

    def test_unicode_repr(self):
        """Teamwork objects should have useful string representations"""
        team = Team.objects.create(name="foo")
        eq_("foo", unicode(team))

        role = Role.objects.create(name="bar")
        eq_("bar", unicode(role))

        doc = Document.objects.create(name="baz")
        policy = Policy.objects.create(content_object=doc)
        eq_("Policy(baz)", unicode(policy))

    def test_owner_is_owner(self):
        """Ensure that Teams claim owner as owner"""
        owner = self.users['randomguy1']
        team = Team.objects.create(name="ownerowned")
        team.add_member(owner, is_owner=True)
        ok_(team.has_owner(owner))

    def test_double_add_member(self):
        """Multiple calls to add_member should result in only one Member record"""
        owner = self.users['randomguy1']
        team = Team.objects.create(name="ownerowned")
        team.add_member(owner)
        team.add_member(owner, is_owner=True)
        eq_(1, team.members.through.objects.filter(user=owner).count())

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
            (True, u'Section 1 Team', u'randomguy8'),
            (True, u'Section 2 Team', u'randomguy8'),
            (True, u'Section 3 Team', u'randomguy8'),
        )
        for expected, team_name, user_name in cases:
            team = self.teams[team_name]
            user = self.users[user_name]
            eq_(expected, team.has_member(user))

    def test_teams_for_user(self):
        """List of teams for user should correspond to membership"""
        cases = (
            (u'section1_leader', (u'Section 1 Team',)),
            (u'section1_editor', (u'Section 1 Team',)),
            (u'section2_leader', (u'Section 2 Team',)),
            (u'section2_editor', (u'Section 2 Team',)),
            (u'section3_leader', (u'Section 3 Team',)),
            (u'section3_editor', (u'Section 3 Team',)),
            (u'randomguy1', []),
            (u'randomguy8', (u'Section 1 Team', u'Section 2 Team', u'Section 3 Team')),
        )
        for username, expected_team_names in cases:
            expected_teams = set(name for name in expected_team_names)
            user = User.objects.get(username=username)
            result_teams = set(team.name for team in Team.objects.get_teams_for_user(user))
            eq_(expected_teams, result_teams)
