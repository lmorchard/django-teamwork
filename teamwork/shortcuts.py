from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser, User, Permission, Group

from .models import Team, Role


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
