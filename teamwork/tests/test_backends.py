import logging
import time

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from ..models import Team, Role, Membership, TeamOwnership
from ..backends import TeamworkBackend

from teamwork_example.models import Document

from . import TestCaseBase


class TeamBackendTests(TestCaseBase):

    def setUp(self):
        super(TeamBackendTests, self).setUp()

        self.backend = TeamworkBackend()

    def test_play(self):

        perms = ('can_review', 'can_move', 'can_frob', 'can_xyzzy', 'can_hello')
        for user in self.users:
            for doc in self.docs:
                for p in perms:
                    print '%s,' % str((self.backend.has_perm(user, 'teamwork_example.%s' % p, doc),
                              user.username, doc.title, p))

                #for p in self.backend.get_all_permissions(user, doc):
                #    print str((user.username, doc.title, p))

        #ok_(False, "Still playing...")

    def test_has_perm(self):
        cases = (
            (False, 'tester0', 'Alpha doc 1', 'can_review'),
            (False, 'tester0', 'Alpha doc 1', 'can_move'),
            (False, 'tester0', 'Alpha doc 1', 'can_frob'),
            (False, 'tester0', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester0', 'Alpha doc 1', 'can_hello'),
            (False, 'tester0', 'Beta doc 1', 'can_review'),
            (False, 'tester0', 'Beta doc 1', 'can_move'),
            (False, 'tester0', 'Beta doc 1', 'can_frob'),
            (False, 'tester0', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester0', 'Beta doc 1', 'can_hello'),
            (False, 'tester0', 'Gamma doc 1', 'can_review'),
            (False, 'tester0', 'Gamma doc 1', 'can_move'),
            (False, 'tester0', 'Gamma doc 1', 'can_frob'),
            (False, 'tester0', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester0', 'Gamma doc 1', 'can_hello'),
            (False, 'tester1', 'Alpha doc 1', 'can_review'),
            (False, 'tester1', 'Alpha doc 1', 'can_move'),
            (False, 'tester1', 'Alpha doc 1', 'can_frob'),
            (False, 'tester1', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester1', 'Alpha doc 1', 'can_hello'),
            (False, 'tester1', 'Beta doc 1', 'can_review'),
            (False, 'tester1', 'Beta doc 1', 'can_move'),
            (False, 'tester1', 'Beta doc 1', 'can_frob'),
            (False, 'tester1', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester1', 'Beta doc 1', 'can_hello'),
            (False, 'tester1', 'Gamma doc 1', 'can_review'),
            (False, 'tester1', 'Gamma doc 1', 'can_move'),
            (False, 'tester1', 'Gamma doc 1', 'can_frob'),
            (False, 'tester1', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester1', 'Gamma doc 1', 'can_hello'),
            (True, 'tester2', 'Alpha doc 1', 'can_review'),
            (False, 'tester2', 'Alpha doc 1', 'can_move'),
            (False, 'tester2', 'Alpha doc 1', 'can_frob'),
            (False, 'tester2', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester2', 'Alpha doc 1', 'can_hello'),
            (False, 'tester2', 'Beta doc 1', 'can_review'),
            (False, 'tester2', 'Beta doc 1', 'can_move'),
            (False, 'tester2', 'Beta doc 1', 'can_frob'),
            (False, 'tester2', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester2', 'Beta doc 1', 'can_hello'),
            (False, 'tester2', 'Gamma doc 1', 'can_review'),
            (False, 'tester2', 'Gamma doc 1', 'can_move'),
            (False, 'tester2', 'Gamma doc 1', 'can_frob'),
            (False, 'tester2', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester2', 'Gamma doc 1', 'can_hello'),
            (True, 'tester3', 'Alpha doc 1', 'can_review'),
            (True, 'tester3', 'Alpha doc 1', 'can_move'),
            (False, 'tester3', 'Alpha doc 1', 'can_frob'),
            (False, 'tester3', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester3', 'Alpha doc 1', 'can_hello'),
            (False, 'tester3', 'Beta doc 1', 'can_review'),
            (False, 'tester3', 'Beta doc 1', 'can_move'),
            (False, 'tester3', 'Beta doc 1', 'can_frob'),
            (False, 'tester3', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester3', 'Beta doc 1', 'can_hello'),
            (False, 'tester3', 'Gamma doc 1', 'can_review'),
            (False, 'tester3', 'Gamma doc 1', 'can_move'),
            (False, 'tester3', 'Gamma doc 1', 'can_frob'),
            (False, 'tester3', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester3', 'Gamma doc 1', 'can_hello'),
            (False, 'tester4', 'Alpha doc 1', 'can_review'),
            (False, 'tester4', 'Alpha doc 1', 'can_move'),
            (False, 'tester4', 'Alpha doc 1', 'can_frob'),
            (False, 'tester4', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester4', 'Alpha doc 1', 'can_hello'),
            (True, 'tester4', 'Beta doc 1', 'can_review'),
            (True, 'tester4', 'Beta doc 1', 'can_move'),
            (False, 'tester4', 'Beta doc 1', 'can_frob'),
            (False, 'tester4', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester4', 'Beta doc 1', 'can_hello'),
            (False, 'tester4', 'Gamma doc 1', 'can_review'),
            (False, 'tester4', 'Gamma doc 1', 'can_move'),
            (False, 'tester4', 'Gamma doc 1', 'can_frob'),
            (False, 'tester4', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester4', 'Gamma doc 1', 'can_hello'),
            (False, 'tester5', 'Alpha doc 1', 'can_review'),
            (False, 'tester5', 'Alpha doc 1', 'can_move'),
            (False, 'tester5', 'Alpha doc 1', 'can_frob'),
            (False, 'tester5', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester5', 'Alpha doc 1', 'can_hello'),
            (True, 'tester5', 'Beta doc 1', 'can_review'),
            (True, 'tester5', 'Beta doc 1', 'can_move'),
            (False, 'tester5', 'Beta doc 1', 'can_frob'),
            (False, 'tester5', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester5', 'Beta doc 1', 'can_hello'),
            (False, 'tester5', 'Gamma doc 1', 'can_review'),
            (False, 'tester5', 'Gamma doc 1', 'can_move'),
            (False, 'tester5', 'Gamma doc 1', 'can_frob'),
            (False, 'tester5', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester5', 'Gamma doc 1', 'can_hello'),
            (False, 'tester6', 'Alpha doc 1', 'can_review'),
            (False, 'tester6', 'Alpha doc 1', 'can_move'),
            (False, 'tester6', 'Alpha doc 1', 'can_frob'),
            (False, 'tester6', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester6', 'Alpha doc 1', 'can_hello'),
            (True, 'tester6', 'Beta doc 1', 'can_review'),
            (True, 'tester6', 'Beta doc 1', 'can_move'),
            (True, 'tester6', 'Beta doc 1', 'can_frob'),
            (False, 'tester6', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester6', 'Beta doc 1', 'can_hello'),
            (False, 'tester6', 'Gamma doc 1', 'can_review'),
            (False, 'tester6', 'Gamma doc 1', 'can_move'),
            (False, 'tester6', 'Gamma doc 1', 'can_frob'),
            (False, 'tester6', 'Gamma doc 1', 'can_xyzzy'),
            (False, 'tester6', 'Gamma doc 1', 'can_hello'),
            (False, 'tester7', 'Alpha doc 1', 'can_review'),
            (False, 'tester7', 'Alpha doc 1', 'can_move'),
            (False, 'tester7', 'Alpha doc 1', 'can_frob'),
            (False, 'tester7', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester7', 'Alpha doc 1', 'can_hello'),
            (True, 'tester7', 'Beta doc 1', 'can_review'),
            (True, 'tester7', 'Beta doc 1', 'can_move'),
            (True, 'tester7', 'Beta doc 1', 'can_frob'),
            (False, 'tester7', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester7', 'Beta doc 1', 'can_hello'),
            (False, 'tester7', 'Gamma doc 1', 'can_review'),
            (False, 'tester7', 'Gamma doc 1', 'can_move'),
            (False, 'tester7', 'Gamma doc 1', 'can_frob'),
            (True, 'tester7', 'Gamma doc 1', 'can_xyzzy'),
            (True, 'tester7', 'Gamma doc 1', 'can_hello'),
            (False, 'tester8', 'Alpha doc 1', 'can_review'),
            (False, 'tester8', 'Alpha doc 1', 'can_move'),
            (False, 'tester8', 'Alpha doc 1', 'can_frob'),
            (False, 'tester8', 'Alpha doc 1', 'can_xyzzy'),
            (False, 'tester8', 'Alpha doc 1', 'can_hello'),
            (False, 'tester8', 'Beta doc 1', 'can_review'),
            (False, 'tester8', 'Beta doc 1', 'can_move'),
            (False, 'tester8', 'Beta doc 1', 'can_frob'),
            (False, 'tester8', 'Beta doc 1', 'can_xyzzy'),
            (False, 'tester8', 'Beta doc 1', 'can_hello'),
            (False, 'tester8', 'Gamma doc 1', 'can_review'),
            (False, 'tester8', 'Gamma doc 1', 'can_move'),
            (False, 'tester8', 'Gamma doc 1', 'can_frob'),
            (True, 'tester8', 'Gamma doc 1', 'can_xyzzy'),
            (True, 'tester8', 'Gamma doc 1', 'can_hello'),
        )
        for expected, username, doc_title, perm_name in cases:
            user = User.objects.get(username=username)
            doc = Document.objects.get(title=doc_title)
            eq_(expected, self.backend.has_perm(user, 'teamwork_example.%s' % perm_name, doc))
