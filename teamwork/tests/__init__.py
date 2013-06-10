from django.test import TestCase
from django.contrib.auth.models import User, Permission, Group

from ..models import Team, Role, Membership, TeamOwnership

from teamwork_example.models import Document


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""

    def setUp(self):
        super(TestCaseBase, self).setUp()

        self.users = [User.objects.create_user(*d) for d in (
            ('tester0', 'tester0@example.com', 'trustno0'),
            ('tester1', 'tester1@example.com', 'trustno1'),
            ('tester2', 'tester2@example.com', 'trustno2'),
            ('tester3', 'tester3@example.com', 'trustno3'),
            ('tester4', 'tester4@example.com', 'trustno4'),
            ('tester5', 'tester5@example.com', 'trustno5'),
            ('tester6', 'tester6@example.com', 'trustno6'),
            ('tester7', 'tester7@example.com', 'trustno7'),
            ('tester8', 'tester8@example.com', 'trustno8'),
        )]

        teams_fields = ('founder', 'title', 'description')
        teams_data = (dict(zip(teams_fields, row)) for row in (
            (self.users[0], "Alpha Team", "A testing team of cool people"),
            (self.users[1], "Beta Team", "A team of testing folks"),
            (self.users[2], "Gamma Team", "Assemblage of users for testing"),
        ))
        self.teams = [Team.objects.create(**d) for d in teams_data]

        roles_fields = ('team', 'name')
        roles_data = (dict(zip(roles_fields, row)) for row in (
            (self.teams[0], 'Trainee'),
            (self.teams[0], 'Normal'),
            (self.teams[0], 'Advanced'),

            (self.teams[1], 'Foo'),
            (self.teams[1], 'Bar'),
            (self.teams[1], 'Baz'),

            (self.teams[2], '!@#$'),
            (self.teams[2], '%^&*'),
            (self.teams[2], '()_+'),
        ))
        self.roles = [Role.objects.create(**d) for d in roles_data]

        perms_data = (
            # 0 has no perms
            (1, 'teamwork_example', 'document', 'can_review'),

            (2, 'teamwork_example', 'document', 'can_review'),
            (2, 'teamwork_example', 'document', 'can_move'),

            (3, 'teamwork_example', 'document', 'can_review'),
            (3, 'teamwork_example', 'document', 'can_move'),

            (4, 'teamwork_example', 'document', 'can_review'),
            (4, 'teamwork_example', 'document', 'can_move'),
            (4, 'teamwork_example', 'document', 'can_frob'),

            (5, 'teamwork_example', 'document', 'can_frob'),

            (6, 'teamwork_example', 'document', 'can_xyzzy'),
            (6, 'teamwork_example', 'document', 'can_hello'),
        )
        for role_idx, app_label, model, perm_name in perms_data:
            role = self.roles[role_idx]
            perm = Permission.objects.get_by_natural_key(perm_name,
                                                         app_label,
                                                         model)
            role.add_permission(perm)
            # role.permissions.add(perm)

        self.members = [self.roles[r].assign(self.users[u]) for r, u in (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4), (3, 5),
            (4, 6), (4, 7),
            (6, 7), (6, 8),
        )]

        docs_fields = ('team', 'title')
        docs_data = (dict(zip(docs_fields, row)) for row in (
            (self.teams[0], 'Alpha doc 1'),
            (self.teams[1], 'Beta doc 1'),
            (self.teams[2], 'Gamma doc 1'),
        ))
        self.docs = [Document.objects.create(**d) for d in docs_data]

    def tearDown(self):
        super(TestCaseBase, self).tearDown()
