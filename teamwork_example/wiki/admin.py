import logging

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from teamwork.models import Team, Role, Policy
from teamwork.admin import PolicyInline

from teamwork_example.wiki.models import Document


def view_link(self):
    """Public link to the document"""
    try:
        link = self.get_absolute_url()
        return '<a target="_blank" href="%s">View</a>' % (link,)
    except:
        return ''

view_link.allow_tags = True
view_link.short_description = "Public"


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', view_link,)
    inlines = (PolicyInline,)


admin.site.register(Document, DocumentAdmin)
