from django.db import models, transaction


class ContentPage(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()

    class Meta:
        permissions = (
            ('can_review', 'Can review changes to pages'),
            ('can_move', 'Can move pages'),
            ('can_frob', 'Cab frobulate pages'),
        )
