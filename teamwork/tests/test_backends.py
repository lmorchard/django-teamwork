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
    eq_(expected_perms, result_perms,
        "Expected perms %s, result was %s" % (expected_perms, result_perms))
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

    def test_mixed_permissions(self):
        """Policies & teams grant permissions by object to users & groups"""
        anon_user = AnonymousUser()
        founder_user = User.objects.create_user(
            'founder0', 'founder0@example.com', 'founder0')
        auth_user = self.users['randomguy1']
        role_user = self.users['randomguy2']
        users_users = [self.users[u] for u in ('randomguy3', 'randomguy4')]
        group_users = [self.users[u] for u in ('randomguy5', 'randomguy6')]
        owner_user = self.users['randomguy7']

        expected_anon_perms = set((u'frob', u'xyzzy'))
        expected_auth_perms = set((u'xyzzy', u'hello'))
        expected_role_perms = set((u'frob', u'hello'))
        expected_users_perms = set((u'frob',))
        expected_group_perms = set((u'hello',))
        expected_owner_perms = set((u'add_document_child',))

        team = Team.objects.create(name='general_permissive_team',
                                   founder=founder_user)

        doc = Document.objects.create(name='general_doc_1',
                                      creator=owner_user,
                                      team=team)

        role1 = Role.objects.create(name='role1', team=team)
        role1.users.add(role_user)
        role1.add_permissions_by_name(expected_role_perms, doc)

        anon_policy = Policy.objects.create(content_object=doc,
                                            anonymous=True)
        anon_policy.add_permissions_by_name(expected_anon_perms, doc)

        auth_policy = Policy.objects.create(content_object=doc,
                                            authenticated=True)
        auth_policy.add_permissions_by_name(expected_auth_perms, doc)

        users_policy = Policy.objects.create(content_object=doc)
        users_policy.users.add(*users_users)
        users_policy.add_permissions_by_name(expected_users_perms, doc)

        group_policy = Policy.objects.create(content_object=doc)
        group = Group.objects.create(name='Honk honk')
        for user in group_users:
            user.groups.add(group)
        group_policy.groups.add(group)
        group_policy.add_permissions_by_name(expected_group_perms, doc)

        owner_policy = Policy.objects.create(content_object=doc,
                                             apply_to_owners=True)
        owner_policy.add_permissions_by_name(expected_owner_perms, doc)

        assert_perms(expected_anon_perms, anon_user, doc)
        assert_perms(expected_auth_perms, auth_user, doc)
        assert_perms(expected_role_perms, role_user, doc)
        assert_perms(expected_auth_perms.union(expected_owner_perms),
                     owner_user, doc)

        expected_perms = expected_users_perms.union(expected_auth_perms)
        for user in users_users:
            assert_perms(expected_perms, user, doc)

        expected_perms = expected_group_perms.union(expected_auth_perms)
        for user in group_users:
            assert_perms(expected_perms, user, doc)

    def test_object_logic_permissions(self):
        """Objects can apply custom logic to permissions"""
        u_quux1 = User.objects.create_user(
            'quux1', 'quux1@example.com', 'quux1')
        u_randomguy1 = User.objects.create_user(
            'randomguy23', 'randomguy23@example.com', 'randomguy23')
        doc = Document.objects.create(name='Quuxy')
        ok_(u_quux1.has_perm('wiki.quux', doc))
        ok_(not u_randomguy1.has_perm('wiki.quux', doc))

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

        policy_on_0 = Policy.objects.create(content_object=docs[0],
                                            authenticated=True)
        policy_on_0.add_permissions_by_name(('frob',))

        policy_on_1 = Policy.objects.create(content_object=docs[1],
                                            authenticated=True)
        policy_on_1.add_permissions_by_name(('xyzzy',))

        policy_on_2 = Policy.objects.create(content_object=docs[2],
                                            authenticated=True)
        policy_on_2.add_permissions_by_name(('hello',))

        policy_on_5 = Policy.objects.create(content_object=docs[5],
                                            authenticated=True)
        policy_on_5.add_permissions_by_name(('quux',))

        # Set up a team & role to exercise team inheritance
        team_for_7 = Team.objects.create(name="Team for 7")
        docs[7].team = team_for_7
        docs[7].save()

        role1 = Role.objects.create(name='role1_for_7', team=team_for_7)
        role1.users.add(user)
        role1.add_permissions_by_name(('add_document_child',), docs[7])

        # Check the team inheritance as a special case
        perms = user.get_all_permissions(docs[8])
        eq_(set(('wiki.add_document_child',)), perms)

        cases = (
            (u'wiki.frob',),   # 0 has own policy
            (u'wiki.xyzzy',),  # 1 has own policy
            (u'wiki.hello',),  # 2 has own policy
            (u'wiki.frob',),   # 3 inherits from 0
            (u'wiki.xyzzy',),  # 4 inherits from 1
            (u'wiki.quux',),   # 5 has own policy
            (u'wiki.frob',),   # 6 inherits from 0
        )
        for idx in range(0, len(cases)):
            doc = docs[idx]
            case = cases[idx]
            perms = user.get_all_permissions(doc)
            eq_(set(case), perms,
                'Permissions for doc #%s should be %s, were instead %s' %
                (idx, case, perms))

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

    def test_settings_base_policy(self):
        """Base policy for the site overall can be specified in settings"""
        # Crude, but ensure there are no policies to override settings
        Policy.objects.all().delete()

        anon_user = AnonymousUser()
        founder_user = User.objects.create_user(
            'founder0', 'founder0@example.com', 'founder0')
        auth_user = self.users['randomguy1']
        role_user = self.users['randomguy2']
        users_users = [self.users[u] for u in ('randomguy3', 'randomguy4')]
        owner_user = self.users['randomguy7']

        group_name = 'settings_policy_group'
        group_users = [self.users[u] for u in ('randomguy5', 'randomguy6')]
        group = Group.objects.create(name=group_name)
        for user in group_users:
            user.groups.add(group)

        doc = Document.objects.create(name='general_doc_2',
                                      creator=owner_user)

        expected_anon_perms = set((u'xyzzy', u'hello'))
        expected_auth_perms = set((u'frob', u'xyzzy'))
        expected_role_perms = set((u'frob',))
        expected_users_perms = set((u'frob', u'hello'))
        expected_group_perms = set((u'add_document_child',))
        expected_owner_perms = set((u'hello',))

        test_policies = dict(
            anonymous=full_perms('wiki', expected_anon_perms),
            authenticated=full_perms('wiki', expected_auth_perms),
            apply_to_owners=full_perms('wiki', expected_owner_perms),
            users=dict(
                (u.username, full_perms('wiki', expected_users_perms))
                for u in users_users),
            groups=dict())

        test_policies['groups'][group_name] = full_perms(
            'wiki', expected_group_perms)

        with override_settings(TEAMWORK_BASE_POLICIES=test_policies):

            assert_perms(expected_anon_perms, anon_user, doc)
            assert_perms(expected_anon_perms, anon_user)
            assert_perms(expected_auth_perms, auth_user, doc)
            assert_perms(expected_auth_perms, auth_user)
            assert_perms(expected_auth_perms.union(expected_owner_perms),
                         owner_user, doc)

            expected_perms = expected_users_perms.union(expected_auth_perms)
            for user in users_users:
                assert_perms(expected_perms, user, doc)
                assert_perms(expected_perms, user)

            expected_perms = expected_group_perms.union(expected_auth_perms)
            for user in group_users:
                assert_perms(expected_perms, user, doc)
                assert_perms(expected_perms, user)

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

    def test_founder_permissions(self):
        """Founder should get special permissions to manage the team"""
        founder_user = User.objects.create_user(
            'founder0', 'founder0@example.com', 'founder0')
        some_user = self.users['randomguy7']
        team1 = Team.objects.create(name='founder_permissive',
                                    founder=founder_user)
        team2 = Team.objects.create(name='some_other_team',
                                    founder=self.users['randomguy1'])
        cases = (
            # Founder of team1 has authority over team1
            (team1, ((founder_user, True), (some_user, False))),
            # Founder of team1 has NO authority over team2
            (team2, ((founder_user, False), (some_user, False))),
        )
        for team, case in cases:
            all_perms = team._meta.permissions
            for user, expected in case:
                for perm, desc in all_perms:
                    eq_(expected, user.has_perm('teamwork.%s' % perm, team))

    def test_team_permissions(self):
        """Role with manage_role_users applies only to its own team"""
        founder_user = User.objects.create_user(
            'founder0', 'founder0@example.com', 'founder0')
        user1 = self.users['randomguy1']
        user2 = self.users['randomguy2']

        team1 = Team.objects.create(name='role_delegation',
                                    founder=founder_user)
        team2 = Team.objects.create(name='disregard_this_team',
                                    founder=founder_user)

        role_granter = Role.objects.create(name='role_granter', team=team1)
        role_granter.add_permissions_by_name(('teamwork.manage_role_users',))
        role_granter.users.add(user1)

        role_disregard = Role.objects.create(name='role_disregard', team=team2)
        role_disregard.add_permissions_by_name(('teamwork.manage_role_users',))

        cases = (
            (founder_user, True, True),
            (user1, True, False),
            (user2, False, False),
        )

        for user, ex_granter, ex_disregard in cases:
            perm1 = user.has_perm('teamwork.manage_role_users', role_granter)
            eq_(ex_granter, perm1,
                "manage_role_users on %s for %s should be %s, but is %s" % (
                    role_granter, user, ex_granter, perm1))
            perm2 = user.has_perm('teamwork.manage_role_users', role_disregard)
            eq_(ex_disregard, perm2,
                "manage_role_users on %s for %s should be %s, but is %s" % (
                    role_disregard, user, ex_disregard, perm2))
