from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission

from teamwork.models import Team, Role


class DocumentManager(models.Manager):
    pass


class Document(models.Model):
    name = models.CharField(max_length=80, unique=True)
    content = models.TextField(blank=True, null=True)

    team = models.ForeignKey(Team, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    creator = models.ForeignKey(User, blank=True, null=True)

    objects = DocumentManager()

    class Meta:
        permissions = (
            ('view_document', 'Can view document'),
            ('add_document_child', 'Can add child document'),
            ('frob', 'Can frobulate documents'),
            ('xyzzy', 'Can xyzzy documents'),
            ('hello', 'Can hello documents'),
            ('quux', 'Can quuxify documents'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Build the absolute URL to this document from its full path"""
        return reverse('wiki.views.view', args=[self.name])

    def get_owner_user(self):
        return self.creator

    def get_all_permissions(self, user, permissions):
        """Filter permissions with custom logic"""
        if ('quux' in user.username):
            permissions.add('wiki.quux')
        return permissions

    def get_permission_parents(self):
        """Build a list of parents from self to root"""
        curr, parents = self, []
        while curr.parent:
            curr = curr.parent
            parents.append(curr)
        return parents

    def get_children(self):
        return Document.objects.filter(parent=self).all()
