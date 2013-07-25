"""
``django-teamwork`` template tags, loaded like so:

    {% load teamwork_tags %}
"""
from __future__ import unicode_literals
from django import template
from django.contrib.auth.models import User, Group, AnonymousUser
from django.template import get_library
from django.template import InvalidTemplateLibrary
from django.template.defaulttags import LoadNode

from ..shortcuts import build_policy_admin_links


register = template.Library()


class ObjectPermissionsNode(template.Node):
    def __init__(self, user_var, obj, context_var):
        self.user_var = template.Variable(user_var)
        self.obj = template.Variable(obj)
        self.context_var = context_var

    def render(self, context):
        user_var = self.user_var.resolve(context)
        if isinstance(user_var, User):
            self.user = user_var
        elif isinstance(user_var, AnonymousUser):
            self.user = user_var
        else:
            raise Exception("User instance required (got %s)"
                % user_var.__class__)
        obj = self.obj.resolve(context)

        perms = self.user.get_all_permissions(obj)
        context[self.context_var] = perms
        return ''


@register.tag
def get_all_obj_permissions(parser, token):
    """
    Get all of a user's permissions granted by an object. For example:

    {% get_all_obj_permissions user for obj as "context_var" %}
    """
    bits = token.split_contents()

    format = '{% get_all_obj_permissions user for obj as "context_var" %}'
    
    if len(bits) != 6 or bits[2] != 'for' or bits[4] != 'as':
        raise template.TemplateSyntaxError("get_all_permissions tag should be in "
            "format: %s" % format)

    _, user_var, _, obj, _, context_var = bits
    
    if context_var[0] != context_var[-1] or context_var[0] not in ('"', "'"):
        raise template.TemplateSyntaxError(
            "get_all_obj_permissions tag's context_var argument should be "
            "quoted")
    
    context_var = context_var[1:-1]

    return ObjectPermissionsNode(user_var, obj, context_var)


class PolicyAdminLinksNode(template.Node):
    def __init__(self, user_var, obj, context_var):
        self.user_var = template.Variable(user_var)
        self.obj = template.Variable(obj)
        self.context_var = context_var

    def render(self, context):
        user_var = self.user_var.resolve(context)
        if isinstance(user_var, User):
            self.user = user_var
        elif isinstance(user_var, AnonymousUser):
            self.user = user_var
        else:
            raise Exception("User instance required (got %s)"
                % user_var.__class__)
        obj = self.obj.resolve(context)

        links = build_policy_admin_links(self.user, obj)
        context[self.context_var] = links
        return ''


@register.tag
def get_policy_admin_links(parser, token):
    """
    Get a set of links to admin pages to manage policy for an object by a user

    {% policy_admin_links user for obj as "context_var" %}
    """
    bits = token.split_contents()

    format = '{% policy_admin_links user for obj as "context_var" %}'
    
    if len(bits) != 6 or bits[2] != 'for' or bits[4] != 'as':
        raise template.TemplateSyntaxError("get_all_permissions tag should be in "
            "format: %s" % format)

    _, user_var, _, obj, _, context_var = bits
    
    if context_var[0] != context_var[-1] or context_var[0] not in ('"', "'"):
        raise template.TemplateSyntaxError(
            "policy_admin_links tag's context_var argument should be "
            "quoted")
    
    context_var = context_var[1:-1]

    return PolicyAdminLinksNode(user_var, obj, context_var)

