import logging
import time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context, TemplateSyntaxError

from django.test import TestCase

from nose.tools import (assert_equal, with_setup, assert_false,
                        eq_, ok_, raises)
from nose.plugins.attrib import attr

from teamwork_example.wiki.models import Document

from ..models import Team, Role, Policy
from ..backends import TeamworkBackend

from . import TestCaseBase


def render(template, context):
    t = Template(template)
    return t.render(Context(context))


class ObjPermissionsTagTests(TestCaseBase):

    def setUp(self):
        self.obj = Document.objects.create(name='templ_test')
        self.user = User.objects.create_user('noob2', 'noob2@example.com',
                                             'noob2')
        self.policy = Policy.objects.create(content_object=self.obj)
        self.policy.users.add(self.user)
        self.policy.add_permissions_by_name(('hello',))

    def test_simple_policy(self):
        """get_all_obj_permissions tag should work for a simple case"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as "perms" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)
        eq_('wiki.hello', result)

    def test_anon_user(self):
        """get_all_obj_permissions tag should work for an anonymous user"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as "perms" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=AnonymousUser(), obj=self.obj)
        result = render(template, context)
        eq_('', result)

    @raises(Exception)
    def test_bad_user(self):
        """get_all_obj_permissions tag should gripe about a non-user param"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as "perms" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=dict(bad="input"), obj=self.obj)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_format(self):
        """get_all_obj_permissions tag should gripe if syntax is bad"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions blah blah blah %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_context_var(self):
        """get_all_obj_permissions tag should require quoted context var"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as i_should_be_quoted %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)


class PolicyLinksTagTests(TestCaseBase):

    def setUp(self):
        self.admin = User.objects.get(username='admin')

        self.obj1 = Document.objects.create(name='templ_test1')

        self.obj2 = Document.objects.create(name='templ_test2')
        self.policy2_1 = Policy.objects.create(content_object=self.obj2)

        self.obj3 = Document.objects.create(name='templ_test3')
        self.policy3_1 = Policy.objects.create(content_object=self.obj3)
        self.policy3_2 = Policy.objects.create(content_object=self.obj3)

        self.user = User.objects.create_user(
            'noob2', 'noob2@example.com', 'noob2')

    def test_simple_policy(self):
        """get_policy_admin_links tag should work for a simple case"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_policy_admin_links user for obj as "policy_links" %}',
            '{% if policy_links.change_one %}',
            'change_one',
            '{% elif policy_links.change_list %}',
            'change_list',
            '{% elif policy_links.add %}',
            'add',
            '{% endif %}',
        ))
        cases = (
            (self.admin, 'add', 'change_one', 'change_list'),
            (self.user, '', '', ''),
            (AnonymousUser(), '', '', ''),
        )
        for user, ex1, ex2, ex3 in cases:
            obj_cases = (ex1, self.obj1), (ex2, self.obj2), (ex3, self.obj3)
            for expected, obj in obj_cases:
                context = dict(user=user, obj=obj)
                result = render(template, context)
                eq_(expected, result)

    @raises(Exception)
    def test_bad_user(self):
        """get_policy_admin_links tag should gripe about a non-user param"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_policy_admin_links user for obj as "links" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=dict(bad="input"), obj=self.obj1)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_format(self):
        """get_policy_admin_links tag should gripe if syntax is bad"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_policy_admin_links blah blah blah %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj1)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_context_var(self):
        """get_policy_admin_links tag should require quoted context var"""
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_policy_admin_links user for obj as i_should_be_quoted %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj1)
        result = render(template, context)
