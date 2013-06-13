from django.db import models, transaction
from django.core.urlresolvers import reverse

from teamwork.models import Team, Role


class DocumentManager(models.Manager):
    pass

class Document(models.Model):
    name = models.CharField(max_length=80, unique=True)
    team = models.ForeignKey(Team, null=True)
    parent = models.ForeignKey('self', null=True)
    content = models.TextField(blank=True, null=True)

    objects = DocumentManager()

    class Meta:
        permissions = (
            ('can_frob', 'Can frobulate pages'),
            ('can_xyzzy', 'Can xyzzy pages'),
            ('can_hello', 'Can hello pages'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Build the absolute URL to this document from its full path"""
        return reverse('wiki.views.view', args=[self.name])
