from django.conf.urls.defaults import *
from tastypie.api import Api
from chat.api import *
from settings.base import STATIC_ROOT

# Tastypie
api = Api(api_name='v1')
api.register(UserProfileResource())
api.register(UserResource())
api.register(MessageResource())
api.register(LinksResource())
api.register(UserLinksResource())
api.register(NotificationResource())
api.register(HistoryResource())
api.register(ConversationListResource())
api.register(UserFollowingResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'chat.views.login', name='login'),

    url(r'^disconnect/$', 'chat.views.disconnect', name='disconnect'),
    url(r'', include('social_auth.urls')),
    url(r'^api/', include(api.urls)),

    url(r'^chat/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT, }),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url('^socket\.io', 'chat.views.socketio'),
)
