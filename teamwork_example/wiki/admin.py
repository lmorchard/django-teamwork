from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic

from teamwork.models import Team, Role, Policy
from teamwork_example.wiki.models import Document


def view_link(self):
    """Public link to the document"""
    link = self.get_absolute_url()
    return '<a target="_blank" href="%s">View</a>' % (link,)

view_link.allow_tags = True
view_link.short_description = "Public"


class PolicyInline(generic.GenericTabularInline):
    model = Policy
    fields = ('team', 'authenticated_permissions', 'anonymous_permissions')
    filter_horizontal = ('anonymous_permissions', 'authenticated_permissions')
    raw_id_fields = ('creator',)
    extra = 0


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', view_link,)
    inlines = (PolicyInline,)


admin.site.register(Document, DocumentAdmin)
