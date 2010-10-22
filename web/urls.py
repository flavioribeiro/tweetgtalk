from django.conf.urls.defaults import *
from web.users import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^onetime/', include('onetime.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^users/$', 'web.users.views.index'),
	(r'^admin/', include(admin.site.urls)),
	(r'^public/(?P<path>.*)$', 'django.views.static.serve',{'document_root' : settings.STATIC_DOC_ROOT}),
)
