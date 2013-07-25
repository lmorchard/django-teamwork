from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser, User, Permission, Group

from .models import Team, Role, Policy


def get_object_or_404_or_403(perm_name, user, model_cls, **kwargs):
    """
    Wrapper for get_object_or_404 that also tests a permission and throws a
    PermissionDenied if the user doesn't have the permission.
    """
    obj = get_object_or_404(model_cls, **kwargs)
    parts = perm_name.split('.', 1)
    if len(parts) == 1:
        ct = ContentType.objects.get_for_model(obj)
        perm_name = '%s.%s' % (ct.app_label, perm_name)
    if not user.has_perm(perm_name, obj):
        raise PermissionDenied
    return obj


def get_permission_by_name(perm_name, obj=None):
    """
    Fetch a Permission by app_label.codename, or codename when an optional
    Model or object is supplied
    """
    if obj:
        ct = ContentType.objects.get_for_model(obj)
        codename = perm_name.split('.')[-1]
        return Permission.objects.get(content_type__app_label=ct.app_label,
                                      codename=codename)
    try:
        app_label, codename = perm_name.split('.', 1)
    except ValueError:
        raise ValueError("With no object supplied, first parameter needs "
                         "to be formatted as app_label.codename, not %s" %
                         perm_name)
    return Permission.objects.get(content_type__app_label=app_label,
                                  codename=codename)


def build_policy_admin_links(user, obj):
    """Build links to manage Teamwork policies for an object"""
    links = {
        'add': None,
        'change_one': None,
        'change_list': None
    }

    ct = ContentType.objects.get_for_model(obj)

    if user.has_perm('teamwork.add_policy'):
        links['add'] = '%s?content_type=%s&object_id=%s' % (
            reverse('admin:teamwork_policy_add'), ct.id, obj.id)

    policies = [
        p for p in
        Policy.objects.filter(content_type__pk=ct.id,
                              object_id=obj.id).all()
        if user.has_perm('teamwork.change_policy', p)
    ]

    policies_ct = len(policies)
    if policies_ct == 1:
        links['change_one'] = reverse('admin:teamwork_policy_change',
                                      args=(policies[0].id,))
    if policies_ct > 1:
        links['change_list'] = (
            '%s?content_type__exact=%s&object_id__exact=%s' % (
            reverse('admin:teamwork_policy_changelist'), ct.id, obj.id))

    return links
