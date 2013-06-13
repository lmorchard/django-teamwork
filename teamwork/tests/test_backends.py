import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from ..models import Team, Role, RoleUser, TeamOwnership
from ..backends import TeamworkBackend

from teamwork_example.wiki.models import Document

from . import TestCaseBase


class TeamBackendTests(TestCaseBase):

    def setUp(self):
        super(TeamBackendTests, self).setUp()

        self.backend = TeamworkBackend()

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
