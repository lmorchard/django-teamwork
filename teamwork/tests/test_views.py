import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase
from django.test.client import Client

from pyquery import PyQuery as pq

from nose.tools import (assert_equal, with_setup, assert_false,
                        eq_, ok_, raises)
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy
from ..backends import TeamworkBackend

from . import TestCaseBase


class UserRolesViewTests(TestCaseBase):

    def setUp(self):
        super(UserRolesViewTests, self).setUp()

        self.client = Client()
        self.managed_user = self.users['section1_editor']
        self.url = reverse('teamwork.views.user_roles',
                           args=(self.managed_user.username,))

    def test_view(self):
        self.client.login(username=self.admin,
                          password=self.admin_password)

        resp = self.client.get(self.url)
        eq_(200, resp.status_code)
        page = pq(resp.content)

        expected = Team.objects.get_team_roles_managed_by(
            self.admin, self.managed_user)

        for team, roles in expected:
            eq_(1, page.find('#team-%s' % team.id).length)
            for r in roles:
                e_role = page.find('#role-%s' % r['role'].id)
                eq_(1, e_role.length)
                e_submit = e_role.find('input[type=submit]')
                eq_(1, e_submit.length)
                eq_(r['granted'] and 'revoke' or 'grant',
                    e_submit.attr('value'))

    def test_grant_revoke(self):
        self.client.login(username=self.admin,
                          password=self.admin_password)

        cases = (
            ('Section 2 Team', 'editor', 'grant', 'revoke'),
            ('Section 1 Team', 'editor', 'revoke', 'grant'),
        )
        for team_name, role_name, state_initial, state_after in cases:
            role = Role.objects.get(team__name=team_name,
                                    name=role_name)

            resp = self.client.get(self.url)
            page = pq(resp.content)
            e_submit = page.find('#role-%s input[type=submit]' % role.id)
            eq_(state_initial, e_submit.attr('value'))

            resp = self.client.post(self.url, data={'role_id': role.id},
                                    follow=True)
            page = pq(resp.content)
            e_submit = page.find('#role-%s input[type=submit]' % role.id)
            eq_(state_after, e_submit.attr('value'))

    def test_grant_403(self):
        self.client.logout()
        role = Role.objects.get(team__name='Section 2 Team',
                                name='editor')
        resp = self.client.post(self.url, data={'role_id': role.id},
                                follow=True)
        eq_(403, resp.status_code)
