from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('profiles.views',
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout'),
    url(r'^teams/(?P<name>.+)$', 'team_detail'),
    url(r'^users/(?P<username>.+)$', 'user_detail'),
)
