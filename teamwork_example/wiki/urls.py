from django.conf.urls import *

urlpatterns = patterns('wiki.views',
    url(r'^\$create$', 'create'),
    url(r'^(?P<name>.+)\$edit$', 'edit'),
    url(r'^(?P<name>.+)\$delete$', 'delete'),
    url(r'^(?P<name>.+)$', 'view'),
)
