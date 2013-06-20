import sys
import logging

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission, Group

from teamwork_example.wiki.models import Document

from ..models import Team, Role
from ..shortcuts import get_permission_by_name


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""
    fixtures = ['initial_data.json']

    def setUp(self):
        super(TestCaseBase, self).setUp()

        self.admin = User.objects.get(username='admin')
        self.users = dict((o.username, o) for o in User.objects.all())
        self.teams = dict((o.name, o) for o in Team.objects.all())
        self.roles = dict((o.name, o) for o in Role.objects.all())
        self.docs = dict((o.name, o) for o in Document.objects.all())
        self.doc_ct = ContentType.objects.get_by_natural_key(
            'wiki', 'document')

    def tearDown(self):
        super(TestCaseBase, self).tearDown()
