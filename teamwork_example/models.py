from django.db import models, transaction
from teamwork.models import Team

class Document(models.Model):
    title = models.CharField(max_length=80)
    team = models.ForeignKey(Team)

    class Meta:
        permissions = (
            ('can_review', 'Can review changes to pages'),
            ('can_move', 'Can move pages'),
            ('can_frob', 'Can frobulate pages'),
            ('can_xyzzy', 'Can xyzzy pages'),
            ('can_hello', 'Can hello pages'),
        )

    def __unicode__(self):
        return '[doc %s]' % self.title
