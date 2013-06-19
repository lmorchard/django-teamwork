from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType

from .models import Team, Role


def get_object_or_404_or_403(perm_name, user, model_cls, **kwargs):
    """Wrapper for get_object_or_404 that also tests a permission"""
    obj = get_object_or_404(model_cls, **kwargs)
    parts = perm_name.split('.', 1)
    if len(parts) == 1:
        ct = ContentType.objects.get_for_model(obj)
        perm_name = '%s.%s' % (ct.app_label, perm_name)
    if not user.has_perm(perm_name, obj):
        raise PermissionDenied
    return obj
