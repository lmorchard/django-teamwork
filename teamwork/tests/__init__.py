import sys
import logging

from django.conf import settings, UserSettingsHolder
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.functional import wraps

from teamwork_example.wiki.models import Document

from ..models import Team, Role
from ..shortcuts import get_permission_by_name


class overrider(object):
    """
    See http://djangosnippets.org/snippets/2437/

    Acts as either a decorator, or a context manager.  If it's a decorator it
    takes a function and returns a wrapped function.  If it's a contextmanager
    it's used with the ``with`` statement.  In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def enable(self):
        pass

    def disable(self):
        pass


class override_settings(overrider):
    """Decorator / context manager to override Django settings"""

    def enable(self):
        self.old_settings = settings._wrapped
        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        settings._wrapped = override

    def disable(self):
        settings._wrapped = self.old_settings


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""
    fixtures = ['initial_data.json']

    def setUp(self):
        super(TestCaseBase, self).setUp()

        self.admin = User.objects.get(username='admin')
        self.admin_password = 'admin'

        self.users = dict((o.username, o) for o in User.objects.all())
        self.teams = dict((o.name, o) for o in Team.objects.all())
        self.roles = dict((o.name, o) for o in Role.objects.all())
        self.docs = dict((o.name, o) for o in Document.objects.all())
        self.doc_ct = ContentType.objects.get_by_natural_key(
            'wiki', 'document')

    def tearDown(self):
        super(TestCaseBase, self).tearDown()
