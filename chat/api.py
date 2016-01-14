from django.contrib.auth.models import User
from django.utils.html import urlize
from templatetags.url_target_blank import url_target_blank
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource
from tastypie import http
from chat.models import Message, Links, UserLinks, Notification, UserProfile, ConversationList
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import simplejson
from django.conf import settings
import re
import urllib
import urllib2
from tastypie.http import HttpUnauthorized
from tastypie.utils import dict_strip_unicode_keys
from social_auth.models import UserSocialAuth
from github import Github


class SessionWebAuthentication(BasicAuthentication):

    def _unauthorized(self):
        response = HttpUnauthorized()
        return response

    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
            return True

        return super(SessionWebAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return super(SessionWebAuthentication, self).get_identifier(request)


class UserProfileResource(ModelResource):

    class Meta:
        #accesss only via UserResource
        allowed_methods = []

        queryset = UserProfile.objects.all()
        resource_name = 'profiles'
        excludes = ['id']
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class UserResource(ModelResource):
    profile = fields.ToOneField(UserProfileResource, attribute='userprofile', related_name='user', full=True, null=True, blank=True)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)

    def alter_list_data_to_serialize(self, request, data):
        #return only one object, the user loggedin.
        return data["objects"][0]

    class Meta:
        allowed_methods = ['get']
        queryset = User.objects.prefetch_related('userprofile')
        resource_name = 'user'
        excludes = ['password']
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class UserFollowingResource(Resource):
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    github_url = fields.CharField(attribute='html_url')
    login = fields.CharField(attribute='login')
    avatar_url = fields.CharField(attribute='avatar_url')
    registered = fields.BooleanField(attribute='registered')

    def get_object_list(self, request):
        instance = UserSocialAuth.objects.filter(provider='github').get(user_id=request.user)
        userGitHub = Github(instance.tokens['access_token'])
        followings = userGitHub.get_user().get_following()
        results = []
        for user in followings:
            chat_user = None
            try:
                chat_user = User.objects.get(username=user.login)
            except User.DoesNotExist:
                pass
            if (chat_user):
                user.user = chat_user
                user.registered = True
            else:
                user.registered = False
            results.append(user)

        return results

    def obj_get_list(self, request=None, **kwargs):
        return self.get_object_list(request)

    def apply_sorting(self, obj_list, options=None):
        return sorted(obj_list, key=lambda x: x.registered, reverse=True)

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        resource_name = 'user/following'
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class ConversationListResource(ModelResource):
    users = fields.ToManyField(UserResource, 'users', full=True, null=True)
    pending_notifications = fields.IntegerField(readonly=True)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(users__in=[request.user.id])

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(ConversationListResource, self).obj_create(bundle, request, **kwargs)
        bundle.obj.users.add(request.user)

        return bundle

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def dehydrate_pending_notifications(self, bundle):
        return Notification.objects.filter(
            message__conversation=bundle.obj, user=bundle.request.user, delivered=False).count()

    def dehydrate(self, bundle):
        if (bundle.data['name'] == ''):
            bundle.data['name'] = ', '.join(str(user.first_name) for user in bundle.obj.users.all())
        return bundle

    class Meta:
        allowed_methods = ['get', 'post', 'put']
        queryset = ConversationList.objects.prefetch_related('users')
        resource_name = 'conversation'
        always_return_data = True
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class MessageResource(ModelResource):
    conversation = fields.ForeignKey(ConversationListResource, 'conversation', full=True, null=True)
    user = fields.ForeignKey(UserResource, 'user', full=True)

    def create_notifications_for_users(self, message, type, description, date):
        notification_onwer = {}
        userList = message.conversation.users.all()
        for user in userList:
            if (message.user.id == user.id):
                notification_onwer = Notification(message=message,
                    type=type,
                    description=description,
                    created_at=date,
                    user=user,
                    delivered=True)
                notification_onwer.save()
            else:
                notification = Notification(message=message,
                    type=type,
                    description=description,
                    created_at=date,
                    user=user,
                    delivered=False)
                notification.save()
        return notification_onwer

    def has_image(self, url):
        result = re.findall(settings.REGEX_IMAGE, url)
        if result:
            return True
        else:
            return False

    def create_links_for_users(self, link):
        userList = link.message.conversation.users.all()
        for user in userList:
            userLink = UserLinks(user=user,
                link=link,
                favorite=False,
                read=False)
            userLink.save()

    def extract_url(self, message):
        urls = re.findall(settings.REGEX_URL, message.message)
        for url in urls:
            url_complete = url[0] + url[2] + '.' + url[3] + url[4]

            #no process images in embed.ly api
            if self.has_image(url_complete):
                continue

            url_escape = urllib.quote_plus(url_complete)
            try:
                response_json = urllib2.urlopen('http://api.embed.ly/1/oembed?key=' +
                    settings.EMBEDLY_API_KEY + '&url=' + url_escape + '&maxwidth=500').read()
                response = simplejson.loads(response_json, encoding='utf8')

                if response.get('url') is None:
                    #author_url is populate when is flashplayer
                    response['url'] = response.get('author_url')

                if response['url']:
                    links = Links.objects.filter(url=response.get('url'))
                    if not links:
                        link = Links(message=message,
                            url=response.get('url'),
                            original_url=url_complete,
                            title=response.get('title'),
                            description=response.get('description'),
                            image_url=response.get('thumbnail_url'))
                        link.save()
                        self.create_links_for_users(link)
            except Exception as ex:
                print ex.__str__()

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(MessageResource, self).obj_create(bundle, request, user=request.user, created_at=datetime.now())
        self.extract_url(bundle.obj)
        notification_onwer = self.create_notifications_for_users(bundle.obj, 'M', None, bundle.obj.created_at)

        bundle = NotificationResource().build_bundle(obj=notification_onwer, request=request)
        NotificationResource().full_dehydrate(bundle)

        return bundle

    def post_list(self, request, **kwargs):

        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        updated_bundle = self.obj_create(bundle, request=request, **self.remove_api_resource_names(kwargs))

        if not self._meta.always_return_data:
            return http.HttpCreated()
        else:
            return self.create_response(request, updated_bundle, response_class=http.HttpCreated)

    def alter_detail_data_to_serialize(self, request, data):
        return data

    def dehydrate(self, bundle):
        bundle.data['message'] = url_target_blank(urlize(bundle.obj.message))
        return bundle

    class Meta:
        allowed_methods = ['post']
        queryset = Message.objects.prefetch_related('user__userprofile')
        resource_name = 'user/messages'
        always_return_data = True
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class LinksResource(ModelResource):
    message = fields.ForeignKey(MessageResource, 'message', full=True)

    class Meta:
        # access only via UserLinksResource
        allowed_methods = []
        queryset = Links.objects.prefetch_related('message__user__userprofile')
        resource_name = 'links'
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class UserLinksResource(ModelResource):
    link = fields.ForeignKey(LinksResource, 'link', full=True)

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        old_link = UserLinks.objects.get(id=kwargs['pk'])
        bundle = super(UserLinksResource, self).obj_update(bundle, request, skip_errors, **kwargs)
        if (old_link.favorite == bundle.obj.favorite):
            bundle.obj.link.clicks = bundle.obj.link.clicks + 1
            bundle.obj.link.save()
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(UserLinksResource, self).build_filters(filters)

        search = filters.get("search", '')
        words = str(search).split()

        for word in words:
            if word == '#read':
                orm_filters = dict(orm_filters.items() + {'read__exact': True}.items())
            elif word == '#unread':
                orm_filters = dict(orm_filters.items() + {'read__exact': False}.items())
            elif word == '#favorite':
                orm_filters = dict(orm_filters.items() + {'favorite__exact': True}.items())
            elif word == '#unfavorite':
                orm_filters = dict(orm_filters.items() + {'favorite__exact': False}.items())
            else:
                qset = (Q(link__title__icontains=word) |
                        Q(link__description__icontains=word) |
                        Q(link__original_url__icontains=word) |
                        Q(link__url__icontains=word)
                    )
                orm_filters = dict(orm_filters.items() + {'QSET_' + word: qset}.items())

        link_clicked = filters.get("url", '')
        if (link_clicked != ''):
            qset = (Q(link__url=link_clicked) | Q(link__original_url=link_clicked))
            orm_filters = dict(orm_filters.items() + {'QSET_link_clicked': qset}.items())

        conversation = filters.get("conversation", None)
        if (conversation):
            orm_filters = dict(orm_filters.items() + {'link__message__conversation__id__exact': conversation}.items())

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        filters_commons = {}
        custom_filtered = None

        custom = []
        for key, value in applicable_filters.iteritems():
            if 'QSET' in key:
                custom.append(value)
            else:
                filters_commons = dict(filters_commons.items() + {key: value}.items())

        semi_filtered = super(UserLinksResource, self).apply_filters(request, filters_commons)

        for qset in custom:
            if custom_filtered is not None:
                custom_filtered = custom_filtered | UserLinks.objects.filter(qset)
            else:
                custom_filtered = UserLinks.objects.filter(qset)

        if custom_filtered is not None:
            semi_filtered = semi_filtered & custom_filtered

        return semi_filtered

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user__id=request.user.id)

    def apply_sorting(self, obj_list, options=None):
        return obj_list.order_by('-link__message__created_at')

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    class Meta:
        allowed_methods = ['get', 'put']
        queryset = UserLinks.objects.prefetch_related('link__message__user__userprofile').select_related('user')
        resource_name = 'user/links'
        always_return_data = True
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class NotificationResource(ModelResource):
    message = fields.ForeignKey(MessageResource, 'message', full=True)

    def put_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)

        for object_data in deserialized:
            notification = Notification.objects.get(id=object_data['id'])
            notification.delivered = True
            notification.save()

        return http.HttpNoContent()

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(NotificationResource, self).build_filters(filters)

        conversation = filters.get("conversation", None)
        if (conversation):
            orm_filters = dict(orm_filters.items() + {'message__conversation__id__exact': conversation}.items())

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        # get only notification pending
        default_filter = super(NotificationResource, self).apply_filters(request, applicable_filters)
        return default_filter.filter(delivered=False)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user__id=request.user.id)

    def apply_sorting(self, obj_list, options=None):
        return obj_list.order_by('-created_at')

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def dehydrate(self, bundle):
        bundle.data['owner_message'] = (bundle.obj.message.user.id == bundle.obj.user.id)
        return bundle

    class Meta:
        allowed_methods = ['get', 'put']
        queryset = Notification.objects.prefetch_related('message__user__userprofile').select_related('user')
        resource_name = 'user/notifications'
        excludes = ['message_id']
        always_return_data = True
        authentication = SessionWebAuthentication()
        authorization = Authorization()


class HistoryResource(ModelResource):
    message = fields.ForeignKey(MessageResource, 'message', full=True)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(HistoryResource, self).build_filters(filters)

        search = filters.get("search", '')
        words = str(search).split()
        for word in words:
            qset = Q(message__message__contains=word)
            orm_filters = dict(orm_filters.items() + {'QSET_' + word: qset}.items())

        days = filters.get("days", '')
        if (days != ''):
            orm_filters = dict(orm_filters.items() +
                {'created_at__gte': datetime.now().date() - timedelta(days=int(days))}.items())

        conversation = filters.get("conversation", None)
        if (conversation):
            orm_filters = dict(orm_filters.items() + {'message__conversation__id__exact': conversation}.items())

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        filters_commons = {}
        custom_filtered = None

        custom = []
        for key, value in applicable_filters.iteritems():
            if 'QSET' in key:
                custom.append(value)
            else:
                filters_commons = dict(filters_commons.items() + {key: value}.items())

        semi_filtered = super(HistoryResource, self).apply_filters(request, filters_commons)

        for qset in custom:
            if custom_filtered is not None:
                custom_filtered = custom_filtered | Notification.objects.filter(qset)
            else:
                custom_filtered = Notification.objects.filter(qset)

        if custom_filtered is not None:
            semi_filtered = semi_filtered & custom_filtered

        return semi_filtered.filter(delivered=True)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user__id=request.user.id)

    def apply_sorting(self, obj_list, options=None):
        return obj_list.order_by('-created_at')

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]

    def dehydrate(self, bundle):
        bundle.data['owner_message'] = (bundle.obj.message.user.id == bundle.obj.user.id)
        return bundle

    class Meta:
        allowed_methods = ['get']
        queryset = Notification.objects.prefetch_related('message__user__userprofile').select_related('user')
        resource_name = 'user/history'
        always_return_data = True
        authentication = SessionWebAuthentication()
        authorization = Authorization()
