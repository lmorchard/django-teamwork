from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('wiki.views',
    url(r'^(?P<name>.+)$', 'view'),
)
