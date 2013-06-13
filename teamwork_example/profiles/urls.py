from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('profiles.views',
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout')
)
