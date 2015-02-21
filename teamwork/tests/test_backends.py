import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from django.contrib.sites.models import Site, get_current_site

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy
from ..backends import TeamworkBackend

from . import TestCaseBase, override_settings


def full_perms(pre, perms):
    return ['%s.%s' % (pre, p) for p in perms]


def assert_perms(expected_perms, user, doc=None):
    result_perms = set(
        n.split('.')[1] for n in
        user.get_all_permissions(doc))
    eq_(set(expected_perms), result_perms)
    for perm in expected_perms:
        user.has_perm(perm, doc)


class TeamBackendTests(TestCaseBase):

    def setUp(self):
        super(TeamBackendTests, self).setUp()

        self.backend = TeamworkBackend()

    def test_authenticate_none(self):
        """Backend should punt on authenticate handling"""
        ok_(True, hasattr(self.backend, 'authenticate'))
        eq_(None, self.backend.authenticate('foo', 'bar'))

    def test_blank_slate_permissions(self):
        """Permission set should be empty, given a blank slate"""
        assert_perms(set(), AnonymousUser())

    def test_superuser_is_super(self):
        """A superuser should be granted all object permissions"""
        doc = Document.objects.create(name='random_doc_1',
                                      creator=self.users['randomguy1'])
        obj_perms = Permission.objects.filter(content_type=self.doc_ct).all()
        expected_perms = set([u"%s.%s" % (self.doc_ct.app_label, p.codename)
                              for p in obj_perms])
        result_perms = self.users['admin'].get_all_permissions(doc)
        eq_(expected_perms, result_perms)
        for perm in expected_perms:
            self.users['admin'].has_perm(perm)

    def test_object_logic_permissions(self):
        """Objects can apply custom logic to permissions"""
        u_quux1 = User.objects.create_user(
            'quux1', 'quux1@example.com', 'quux1')
        u_randomguy1 = User.objects.create_user(
            'randomguy23', 'randomguy23@example.com', 'randomguy23')
        doc = Document.objects.create(name='Quuxy')
        ok_(u_quux1.has_perm('wiki.quux', doc))
        ok_(not u_randomguy1.has_perm('wiki.quux', doc))

    def test_settings_base_policy(self):
        """Base policy for the site overall can be specified in settings"""
        # Crude, but ensure there are no policies to override settings
        Policy.objects.all().delete()

        # Get a handle on some users to play with
        anon_user = AnonymousUser()
        owner_user = User.objects.create_user('owner0', 'owner0@example.com', 'owner0')

        # Get some groups to play with
        group_name = 'settings_policy_group'
        group_users = [self.users[u] for u in ('randomguy5', 'randomguy6')]
        group = Group.objects.create(name=group_name)
        for user in group_users:
            user.groups.add(group)

        team = Team.objects.create(name='settings_test_team', owner=owner_user)
        member = team.add_member(self.users['randomguy7'])
        
        # Create a document to play with the permissions
        doc = Document.objects.create(name='general_doc_2', team=team,
                                      creator=owner_user)

        test_policies = {
            'all': ('wiki.xyzzy', 'wiki.quux', 'wiki.frob',),
            'authenticated': ('-wiki.frob', 'wiki.hello',),
            'owners': ('-wiki.hello', 'wiki.change_document',),
            'members': ('wiki.add_document',),
            'groups': {
                'settings_policy_group': ('-wiki.hello', 'wiki.add_document_child',)
            },
            'users': {
                'randomguy3': ('-wiki.xyzzy', 'wiki.delete_document'),
                'randomguy4': ('-wiki.quux', 'wiki.add_document_child'),
            },
        }

        with override_settings(TEAMWORK_BASE_POLICIES=test_policies):
            
            assert_perms(('xyzzy', 'quux', 'frob'), anon_user, doc)
            assert_perms(('xyzzy', 'quux', 'frob'), anon_user)

            assert_perms(('xyzzy', 'quux', 'hello'), self.users['randomguy1'], doc)
            assert_perms(('xyzzy', 'quux', 'hello'), self.users['randomguy1'])

            assert_perms(('xyzzy', 'quux', 'change_document'), owner_user, doc)

            assert_perms(('xyzzy', 'quux', 'hello', 'add_document'), self.users['randomguy7'], doc)

            assert_perms(('quux', 'hello', 'delete_document'), self.users['randomguy3'], doc)
            assert_perms(('xyzzy', 'hello', 'add_document_child'), self.users['randomguy4'], doc)

            assert_perms(('xyzzy', 'quux', 'add_document_child'), self.users['randomguy5'], doc)
            assert_perms(('xyzzy', 'quux', 'add_document_child'), self.users['randomguy6'], doc)

    def test_team_role_permissions(self):
        """A role assigned to a team member should grant and deny permissions"""
        member1 = self.users['randomguy1']
        owner = self.users['randomguy2']
        founder = self.users['randomguy3']

        team = Team.objects.create(name='general_permissive_team',
                                   owner=founder)

        doc = Document.objects.create(name='general_doc_1',
                                      creator=owner, team=team)

        role = Role.objects.create(name='role1')
        role.add_permissions_by_name(('frob', 'hello', '-add_document'), doc)

        assert_perms((
            'add_document', # Note: Attached as a policy to current site in fixture data
        ), member1, doc)
        
        team.add_member(member1, role)

        assert_perms(('frob', 'hello',), member1, doc)

    def test_owner_permissions(self):
        """Team owner should get special permissions to manage the team"""
        owner_user = User.objects.create_user(
            'owner0', 'owner0@example.com', 'owner0')
        some_user = self.users['randomguy7']
        team1 = Team.objects.create(name='owner_permissive',
                                    owner=owner_user)
        team2 = Team.objects.create(name='some_other_team',
                                    owner=self.users['randomguy1'])
        cases = (
            # owner of team1 has authority over team1
            (team1, ((owner_user, True), (some_user, False))),
            # owner of team1 has NO authority over team2
            (team2, ((owner_user, False), (some_user, False))),
        )
        for team, case in cases:
            all_perms = team._meta.permissions
            for user, expected in case:
                for perm, desc in all_perms:
                    eq_(expected, user.has_perm('teamwork.%s' % perm, team))

    def test_site_policy(self):
        """Policies on Sites should grant base-level permissions"""
        curr_site = Site.objects.get_current()
        new_site = Site.objects.create(domain='site2', name='site2')

        doc = Document.objects.create(name="site_doc")
        doc2 = Document.objects.create(name="site_doc2", site=new_site)

        policy = Policy.objects.create(content_object=curr_site)
        policy2 = Policy.objects.create(content_object=new_site)

        user = User.objects.create_user(
            'sitemember0', 'sitemember0@example.com', 'sitemember0')
        policy.users.add(user)
        policy2.users.add(user)

        expected_perms = ('add_document', 'add_document_child')
        policy.add_permissions_by_name(expected_perms, obj=doc)

        expected_perms2 = ('hello', 'quux')
        policy2.add_permissions_by_name(expected_perms2, obj=doc2)

        result_perms = user.get_all_permissions(doc)
        eq_(set(('wiki.add_document', 'wiki.add_document_child')),
            result_perms)

        result_perms = user.get_all_permissions()
        eq_(set(('wiki.add_document', 'wiki.add_document_child')),
            result_perms)

        result_perms = user.get_all_permissions(doc2)
        eq_(set(('wiki.hello', 'wiki.quux')), result_perms)

    def test_empty_obj_policy_overrides_base(self):
        """Policy on an object with no permissions overrides base policy"""
        Policy.objects.all().delete()
        anon_user = AnonymousUser()
        owner_user = self.users['randomguy7']
        doc = Document.objects.create(name='general_doc_2',
                                      creator=owner_user)
        anon_perms = set((u'xyzzy', u'hello'))
        base_policies = dict(anonymous=full_perms('wiki', anon_perms),)
        doc_policy = Policy.objects.create(content_object=doc,
                                           anonymous=True)

        # Note: No permissions added to this doc_policy, which should *revoke*
        # the base policies.
        expected_perms = set()
        #doc_policy.add_permissions_by_name(expected_perms, obj=doc)

        with override_settings(TEAMWORK_BASE_POLICIES=base_policies):
            assert_perms(expected_perms, anon_user, doc)

    def test_mixed_permissions(self):
        """Policies & teams grant permissions by object to users & groups"""

        anon_user = AnonymousUser()
        owner_user = User.objects.create_user('owner0', 'owner0@example.com', 'owner0')
        auth_user = self.users['randomguy1']
        role_user = self.users['randomguy2']
        users_users = [self.users[u] for u in ('randomguy3', 'randomguy4')]
        group_users = [self.users[u] for u in ('randomguy5', 'randomguy6')]
        owner_user = self.users['randomguy7']

        team = Team.objects.create(name='general_permissive_team', owner=owner_user)

        doc = Document.objects.create(name='general_doc_1', creator=owner_user, team=team)

        role1 = Role.objects.create(name='role1')
        role1.add_permissions_by_name(('frob', 'hello'), doc)

        team.add_member(role_user, role1)

        anon_policy = Policy.objects.create(content_object=doc, anonymous=True)
        anon_policy.add_permissions_by_name(('frob', 'xyzzy'), doc)

        auth_policy = Policy.objects.create(content_object=doc, authenticated=True)
        auth_policy.add_permissions_by_name(('xyzzy', 'hello', '-add_document'), doc)

        users_policy = Policy.objects.create(content_object=doc)
        users_policy.users.add(*users_users)
        users_policy.add_permissions_by_name(('frob',), doc)

        group_policy = Policy.objects.create(content_object=doc)
        group = Group.objects.create(name='Honk honk')
        for user in group_users:
            user.groups.add(group)
        group_policy.groups.add(group)
        group_policy.add_permissions_by_name(('quux',), doc)

        owner_policy = Policy.objects.create(content_object=doc, apply_to_owners=True)
        owner_policy.add_permissions_by_name(('change_document',), doc)

        assert_perms(('frob', 'xyzzy'), anon_user, doc)
        assert_perms(('xyzzy', 'hello'), auth_user, doc)
        assert_perms(('frob', 'xyzzy', 'hello'), role_user, doc)
        assert_perms(('change_document', 'xyzzy', 'hello'), owner_user, doc)

        for user in users_users:
            assert_perms(('hello', 'frob', 'xyzzy'), user, doc)

        for user in group_users:
            assert_perms(('hello', 'quux', 'xyzzy'), user, doc)

    def test_parent_permissions(self):
        """Content objects can supply a list of parents for inheritance"""
        user = User.objects.create_user('noob1', 'noob1@example.com', 'noob1')

        # Set up document tree:
        #  /- 1 - 4
        # 0 - 2 - 5
        #  \- 3 - 6
        #  \- 7 - 8
        docs = []
        for idx in range(0, 9):
            docs.append(Document.objects.create(name=('tree%s' % idx)))
        links = ((0, 1), (1, 4),
                 (0, 2), (2, 5),
                 (0, 3), (3, 6),
                 (0, 7), (7, 8))
        for (parent_idx, child_idx) in links:
            child = docs[child_idx]
            child.parent = docs[parent_idx]
            child.save()

        policy_on_0 = Policy.objects.create(content_object=docs[0], authenticated=True)
        policy_on_0.add_permissions_by_name(('frob', '-add_document'))

        policy_on_1 = Policy.objects.create(content_object=docs[1], authenticated=True)
        policy_on_1.add_permissions_by_name(('xyzzy',))

        policy_on_2 = Policy.objects.create(content_object=docs[2], authenticated=True)
        policy_on_2.add_permissions_by_name(('hello',))

        policy_on_5 = Policy.objects.create(content_object=docs[5], authenticated=True)
        policy_on_5.add_permissions_by_name(('quux',))

        # Set up a team & role to exercise team inheritance
        team_for_7 = Team.objects.create(name="Team for 7")
        docs[7].team = team_for_7
        docs[7].save()

        role1 = Role.objects.create(name='role1_for_7', team=team_for_7)
        role1.add_permissions_by_name(('add_document_child',), docs[7])

        team_for_7.add_member(user, role1)

        # Check the team inheritance as a special case
        perms = user.get_all_permissions(docs[8])
        eq_(set([u'wiki.frob', u'wiki.add_document_child']), perms)

        cases = (
            # 0 has own policy
            [u'wiki.frob'],
            # 1 inherits from 0 and own policy
            [u'wiki.frob', u'wiki.xyzzy'],
            # 2 inherits from 0 and own policy
            [u'wiki.frob', u'wiki.hello'],
            # 3 inherits from 0
            [u'wiki.frob'],
            # 4 inherits from 1 and 0
            [u'wiki.frob', u'wiki.xyzzy'],
            # 5 inherits from 0, 2, and own policy
            [u'wiki.hello', u'wiki.frob', u'wiki.quux'],
            # 6 inherits from 3 (which inherits from 0)
            [u'wiki.frob'],
        )
        for idx in range(0, len(cases)):
            doc = docs[idx]
            case = cases[idx]
            perms = user.get_all_permissions(doc)
            logging.debug('%s: %s' % (doc, perms))
            eq_(set(case), perms)
