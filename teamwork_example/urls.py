from django.conf.urls.defaults import include, patterns, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect, render
from django.views.i18n import javascript_catalog
from django.views.decorators.cache import cache_page


admin.autodiscover()

urlpatterns = patterns('',
    ('', include('base.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^wiki/', include('wiki.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

# Handle 404 and 500 errors
def _error_page(request, status):
    """Render error pages with jinja2."""
    return render(request, '%d.html' % status, status=status)
handler403 = lambda r: _error_page(r, 403)
handler404 = lambda r: _error_page(r, 404)
handler500 = lambda r: _error_page(r, 500)

if settings.SERVE_MEDIA:
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
          {'document_root': settings.MEDIA_ROOT}),
    )

