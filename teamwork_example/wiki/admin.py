from django.contrib import admin
from django.core.urlresolvers import reverse

from teamwork_example.wiki.models import Document


def view_link(self):
    """Public link to the document"""
    link = self.get_absolute_url()
    return '<a target="_blank" href="%s">View</a>' % (link,)

view_link.allow_tags = True
view_link.short_description = "Public"


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', view_link,)


admin.site.register(Document, DocumentAdmin)
