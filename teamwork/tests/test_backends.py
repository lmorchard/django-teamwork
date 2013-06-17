import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy
from ..backends import TeamworkBackend

from . import TestCaseBase


class TeamBackendTests(TestCaseBase):

    def setUp(self):
        super(TeamBackendTests, self).setUp()

        self.backend = TeamworkBackend()

    def test_general_permissions(self):
        """Appropriate permissions for anonymous, authenticated, and members"""
        anon_user = AnonymousUser()
        auth_user = self.users['tester0']
        role_user = self.users['tester1']
        users_users = (self.users[u] for u in
                       ('tester2', 'tester3'))
        group_users = (self.users[u] for u in
                       ('tester4', 'tester5', 'tester6'))

        expected_anon_perms = set((u'can_frob', u'can_xyzzy'))
        expected_auth_perms = set((u'can_xyzzy', u'can_hello'))
        expected_role_perms = set((u'can_frob', u'can_hello'))
        expected_users_perms = set((u'can_frob',))
        expected_group_perms = set((u'can_hello',))

        team = Team.objects.create(name='general_permissive_team',
                                   founder=self.users['founder0'])

        doc = Document.objects.create(name='general_doc_1',
                                      team=team)

        anon_policy = Policy.objects.create(content_object=doc,
                                            anonymous=True)
        perms = self.names_to_doc_permissions(expected_anon_perms)
        anon_policy.permissions.add(*perms)

        auth_policy = Policy.objects.create(content_object=doc,
                                            authenticated=True)
        perms = self.names_to_doc_permissions(expected_auth_perms)
        auth_policy.permissions.add(*perms)

        role1 = Role.objects.create(name='role1', team=team)
        role1.users.add(role_user)
        perms = self.names_to_doc_permissions(expected_role_perms)
        role1.permissions.add(*perms)

        users_policy = Policy.objects.create(content_object=doc)
        perms = self.names_to_doc_permissions(expected_users_perms)
        users_policy.users.add(*users_users)
        users_policy.permissions.add(*perms)

        group_policy = Policy.objects.create(content_object=doc)
        group = Group.objects.create(name='Honk honk')
        for user in group_users:
            user.groups.add(group)
        group_policy.groups.add(group)
        perms = self.names_to_doc_permissions(expected_group_perms)
        group_policy.permissions.add(*perms)

        def assert_perms(expected_perms, user):
            eq_(expected_perms, set(
                n.split('.')[1] for n in
                self.backend.get_all_permissions(user, doc)))

        assert_perms(expected_anon_perms, anon_user)
        assert_perms(expected_auth_perms, auth_user)
        assert_perms(expected_role_perms, role_user)
        for user in users_users:
            assert_perms(expected_users_perms, user)
        for user in group_users:
            assert_perms(expected_group_perms, user)

    def test_permissions(self):
        """Ensure users with roles get appropriate permissions for objects
        associated with teams"""
        cases = (
            ('tester0', 'doc1', []),
            ('tester0', 'doc2', []),
            ('tester0', 'doc3', []),
            ('tester1', 'doc1', []),
            ('tester1', 'doc2', []),
            ('tester1', 'doc3', []),
            ('tester2', 'doc1', ['can_frob']),
            ('tester2', 'doc2', []),
            ('tester2', 'doc3', []),
            ('tester3', 'doc1', []),
            ('tester3', 'doc2', ['can_hello', 'can_xyzzy']),
            ('tester3', 'doc3', []),
            ('tester4', 'doc1', []),
            ('tester4', 'doc2', ['can_hello']),
            ('tester4', 'doc3', ['can_frob', 'can_xyzzy']),
            ('tester5', 'doc1', []),
            ('tester5', 'doc2', []),
            ('tester5', 'doc3', ['can_hello', 'can_frob', 'can_xyzzy']),
            ('tester6', 'doc1', []),
            ('tester6', 'doc2', []),
            ('tester6', 'doc3', ['can_hello', 'can_frob', 'can_xyzzy']),
        )
        # TODO: Harvest this from Document's Meta class
        all_perms = ['wiki.%s' % p[0] for p in (
            'can_frob', 'can_xyzzy', 'can_hello'
        )]
        for user_name, doc_name, perm_names in cases:
            user = self.users[user_name]
            doc = self.docs[doc_name]

            expected = set('wiki.%s' % p for p in perm_names)

            # Try the backend directly, then try it through the user
            result = self.backend.get_all_permissions(user, doc)
            eq_(expected, result)
            result = user.get_all_permissions(doc)
            eq_(expected, result)

            for perm in all_perms:
                hp_expected = perm in expected
                # Try the backend directly, then try it through the user
                hp_result = self.backend.has_perm(user, perm, doc)
                eq_(hp_expected, hp_result)
                hp_result = user.has_perm(perm, doc)
                eq_(hp_expected, hp_result)
