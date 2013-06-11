from django.test import TestCase
from django.contrib.auth.models import User, Permission, Group

from ..models import Team, Role, Membership, TeamOwnership

from teamwork_example.models import Document


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""

    def setUp(self):
        super(TestCaseBase, self).setUp()

        self.users = dict([
            ('tester%s' % idx,
             User.objects.create_user(*('tester%s' % idx,
                                        'tester%s@example.com' % idx,
                                        'trustno%s' % idx)))
            for idx in range(0, 10)
        ])
        self.users.update(dict([
            ('founder%s' % idx,
             User.objects.create_user(*('founder%s' % idx,
                                        'founder%s@example.com' % idx,
                                        'trustno%s' % idx)))
            for idx in range(0, 3)
        ]))

        teams_fields = ('founder', 'title', 'description')
        teams_data = (dict(zip(teams_fields, row)) for row in (
            (self.users['founder0'], "alpha", "Cool people"),
            (self.users['founder1'], "beta", "A team of folks"),
            (self.users['founder2'], "gamma", "Assemblage of users"),
        ))
        self.teams = dict([(d['title'], Team.objects.create(**d))
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

        app_label, model = 'teamwork_example', 'document'
        perms_data = (
            # trainee has no perms

            ('normal', 'can_frob'),

            ('foo', 'can_xyzzy'),

            ('bar', 'can_hello'),

            ('baz', 'can_frob'),
            ('baz', 'can_xyzzy'),

            ('quux', 'can_frob'),
            ('quux', 'can_xyzzy'),
            ('quux', 'can_hello'),
        )
        for role_name, perm_name in perms_data:
            role = self.roles[role_name]
            perm = Permission.objects.get_by_natural_key(perm_name,
                                                         app_label,
                                                         model)
            role.add_permission(perm)

        self.members = [self.roles[r].assign(self.users[u]) for r, u in (
            ('trainee', 'tester1'),
            ('normal', 'tester2'),
            ('foo', 'tester3'),
            ('bar', 'tester3'),
            ('bar', 'tester4'),
            ('baz', 'tester4'),
            ('baz', 'tester5'),
            ('quux', 'tester5'),
            ('quux', 'tester6'),
        )]

        docs_fields = ('team', 'name')
        docs_data = (dict(zip(docs_fields, row)) for row in (
            (self.teams['alpha'], 'doc1'),
            (self.teams['beta'],  'doc2'),
            (self.teams['gamma'], 'doc3'),
        ))
        self.docs = dict([(d['name'], Document.objects.create(**d))
                          for d in docs_data])

    def tearDown(self):
        super(TestCaseBase, self).tearDown()
