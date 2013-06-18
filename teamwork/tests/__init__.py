import sys
import logging

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission, Group

from teamwork_example.wiki.models import Document

from ..models import Team, Role


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""

    def setUp(self):
        super(TestCaseBase, self).setUp()

        self.doc_ct = (ContentType.objects.get_by_natural_key('wiki',
                                                              'document'))

        self.admin = User.objects.create_superuser(
            'admin', 'admin@example.com', 'admin')

        self.users = dict(admin=self.admin)
        for pre, amt in (('tester', 10), ('founder', 3)):
            self.users.update(dict(
                ('%s%s' % (pre, idx),
                 User.objects.create_user('%s%s' % (pre, idx),
                                          '%s%s@example.com' % (pre, idx),
                                          '%s%s' % (pre, idx)))
                for idx in range(0, amt)))

        teams_fields = ('founder', 'name', 'description')
        teams_data = (dict(zip(teams_fields, row)) for row in (
            (self.users['founder0'], "alpha", "Cool people"),
            (self.users['founder1'], "beta", "A team of folks"),
            (self.users['founder2'], "gamma", "Assemblage of users"),
        ))
        self.teams = dict([(d['name'], Team.objects.create(**d))
                           for d in teams_data])

        roles_fields = ('team', 'name')
        roles_data = (dict(zip(roles_fields, row)) for row in (
            (self.teams['alpha'], 'trainee'),
            (self.teams['alpha'], 'normal'),

            (self.teams['beta'], 'foo'),
            (self.teams['beta'], 'bar'),

            (self.teams['gamma'], 'baz'),
            (self.teams['gamma'], 'quux'),
        ))
        self.roles = dict([(d['name'], Role.objects.create(**d))
                           for d in roles_data])

        app_label, model = 'wiki', 'document'
        perms_data = (
            # trainee has no perms

            ('normal', 'frob'),

            ('foo', 'xyzzy'),

            ('bar', 'hello'),

            ('baz', 'frob'),
            ('baz', 'xyzzy'),

            ('quux', 'frob'),
            ('quux', 'xyzzy'),
            ('quux', 'hello'),
        )
        for role_name, perm_name in perms_data:
            role = self.roles[role_name]
            perm = Permission.objects.get_by_natural_key(perm_name,
                                                         app_label,
                                                         model)
            role.permissions.add(perm)

        roles_data = (
            ('trainee', 'tester1'),
            ('normal', 'tester2'),
            ('foo', 'tester3'),
            ('bar', 'tester3'),
            ('bar', 'tester4'),
            ('baz', 'tester4'),
            ('baz', 'tester5'),
            ('quux', 'tester5'),
            ('quux', 'tester6'),
        )
        for role_name, user_name in roles_data:
            role = self.roles[role_name]
            user = self.users[user_name]
            role.users.add(user)

        docs_fields = ('team', 'name')
        docs_data = (dict(zip(docs_fields, row)) for row in (
            (self.teams['alpha'], 'doc1'),
            (self.teams['beta'],  'doc2'),
            (self.teams['gamma'], 'doc3'),
        ))
        self.docs = dict([(d['name'], Document.objects.create(**d))
                          for d in docs_data])

        if False:
            from django.core.management import call_command
            sysout = sys.stdout
            sys.stdout = open('test_data.json', 'w')
            call_command('dumpdata', indent=4)
            sys.stdout = sysout

    def tearDown(self):
        super(TestCaseBase, self).tearDown()

    def names_to_doc_permissions(self, names):
        return [Permission.objects.get_by_natural_key(name, 'wiki', 'document')
                for name in names]
