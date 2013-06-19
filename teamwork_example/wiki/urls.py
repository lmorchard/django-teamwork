from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('wiki.views',
    url(r'^\$create$', 'create'),
    url(r'^(?P<name>.+)\$edit$', 'edit'),
    url(r'^(?P<name>.+)\$delete$', 'delete'),
    url(r'^(?P<name>.+)$', 'view'),
)
