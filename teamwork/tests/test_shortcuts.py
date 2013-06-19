import logging
import time

from nose.tools import (assert_equal, with_setup, assert_false,
                        eq_, ok_, raises)
from nose.plugins.attrib import attr

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.test import TestCase

from django.core.exceptions import PermissionDenied

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy
from ..backends import TeamworkBackend
from ..shortcuts import get_object_or_404_or_403

from . import TestCaseBase


class ShortcutTests(TestCaseBase):

    def setUp(self):
        self.obj = Document.objects.create(name='shortcut_test')
        self.user = User.objects.create_user('noob2', 'noob2@example.com',
                                             'noob2')
        self.policy = Policy.objects.create(content_object=self.obj)
        self.policy.users.add(self.user)
        perms = self.names_to_doc_permissions(('hello',))
        self.policy.permissions.add(*perms)

    def test_simple_get(self):
        """get_object_or_404_or_403 shortcut should return an object"""
        obj = get_object_or_404_or_403('wiki.hello', self.user,
                                       Document, name='shortcut_test')
        eq_(self.obj.pk, obj.pk)

    def test_short_codename_get(self):
        """get_object_or_404_or_403 shortcut should accept a short codename"""
        obj = get_object_or_404_or_403('hello', self.user,
                                       Document, name='shortcut_test')
        eq_(self.obj.pk, obj.pk)

    @raises(PermissionDenied)
    def test_403(self):
        """get_object_or_404_or_403 should throw PermissionDenied"""
        obj = get_object_or_404_or_403('wiki.quux', self.user,
                                       Document, name='shortcut_test')

    @raises(Http404)
    def test_404(self):
        """get_object_or_404_or_403 should throw Http404"""
        obj = get_object_or_404_or_403('wiki.hello', self.user,
                                       Document, name='does_not_exist')
