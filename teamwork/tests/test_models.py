import logging
import time

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase
from django.test.client import Client

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from ..models import Team, Role, Membership, TeamOwnership

from teamwork_example.models import ContentPage


class TeamTests(TestCase):

    def setUp(self):

        self.users = [User.objects.create_user(*d) for d in (
            ('tester0', 'tester0@example.com', 'trustno0'),
            ('tester1', 'tester1@example.com', 'trustno1'),
            ('tester2', 'tester2@example.com', 'trustno2'),
            ('tester3', 'tester3@example.com', 'trustno3'),
            ('tester4', 'tester4@example.com', 'trustno4')
        )]

        self.teams = [Team.objects.create(**d) for d in (
            dict(title="Alpha Team",
                 description="A testing team of cool people",
                 founder=self.users[0]),
            dict(title="Beta Team",
                 description="A team of testing folks",
                 founder=self.users[1]),
            dict(title="Gamma Team",
                 description="Assemblage of users for testing",
                 founder=self.users[2]),
        )]

        self.roles = [Role.objects.create(**d) for d in (
            dict(team=self.teams[0], name='Trainee'),
            dict(team=self.teams[0], name='Normal'),
            dict(team=self.teams[0], name='Advanced'),
            dict(team=self.teams[0], name='L10N'),

            dict(team=self.teams[1], name='Foo'),
            dict(team=self.teams[1], name='Bar'),
            dict(team=self.teams[1], name='Baz'),

            dict(team=self.teams[2], name='!@#$'),
            dict(team=self.teams[2], name='%^&*'),
            dict(team=self.teams[2], name='()_+'),
        )]

    def tearDown(self):
        pass

    def test_has_member(self):
        """Users with roles on a team should be counted as members"""
        team = self.teams[0]
        members = [Membership.objects.create(role=role, user=user)
                   for role, user in (
                       (self.roles[0], self.users[1]),
                       (self.roles[1], self.users[2]),
                       (self.roles[2], self.users[3]),
                   )]

        # TODO: The founder is not considered a member, lacking a Role
        # ok_(team.has_member(self.users[0]))
        ok_(team.has_member(self.users[1]))
        ok_(team.has_member(self.users[2]))
        ok_(team.has_member(self.users[3]))
        ok_(not team.has_member(self.users[4]))

    def test_teams_for_user(self):
        user = self.users[3]
        expected_teams = [self.teams[idx] for idx in (0, 2)]
        for team in expected_teams:
            Membership.objects.create(role=team.role_set.all()[0],
                                      user=user)
        teams = Team.objects.get_teams_for_user(user)
        eq_(len(expected_teams), teams.count())
        for t in expected_teams:
            ok_(t in teams)

    def test_play(self):

        for r in self.teams[0].role_set.all():
            logging.debug("ROLE %s" % r)

        for m in self.teams[0].members:
            logging.debug("MEMBER %s" % m)

        for u in self.teams[0].users:
            logging.debug("USER %s" % u)

        page_ct = ContentType.objects.get(app_label="teamwork_example",
                                          model="contentpage")
        perms = Permission.objects.filter(content_type=page_ct)
        for p in perms:
            logging.debug("PERMISSION %s" % p)

        ok_(False, "Still playing...")
