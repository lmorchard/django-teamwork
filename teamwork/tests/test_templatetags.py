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


class TemplateTagsTests(TestCaseBase):

    def setUp(self):
        self.obj = Document.objects.create(name='templ_test')
        self.user = User.objects.create_user('noob2', 'noob2@example.com',
                                             'noob2')
        self.policy = Policy.objects.create(content_object=self.obj)
        self.policy.users.add(self.user)
        perms = self.names_to_doc_permissions(('hello',))
        self.policy.permissions.add(*perms)

    def test_simple_policy(self):
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as "perms" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)
        eq_('wiki.hello', result)

    def test_anon_user(self):
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
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as "perms" %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=dict(bad="input"), obj=self.obj)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_format(self):
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions blah blah blah %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)

    @raises(TemplateSyntaxError)
    def test_bad_context_var(self):
        template = ''.join((
            '{% load teamwork_tags %}',
            '{% get_all_obj_permissions user for obj as i_should_be_quoted %}',
            '{{ perms|join:" " }}',
        ))
        context = dict(user=self.user, obj=self.obj)
        result = render(template, context)
