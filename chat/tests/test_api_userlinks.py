from django.contrib.auth.models import User
from chat.models import UserProfile, Message, Links, UserLinks, ConversationList
from tastypie.test import ResourceTestCase
from datetime import datetime
from chat.tests import create_user_loggedin, get_credentials


class UserLinksResourceTest(ResourceTestCase):
    def setUp(self):
        super(UserLinksResourceTest, self).setUp()

        create_user_loggedin(self)

        self.user2 = User.objects.create_user(username='maximize', email='do@howtomaximize.com', password='123')
        UserProfile.objects.create(user=self.user2, avatar_url='http://www.howtomaximize.com')

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)
        self.conversation.users.add(self.user2)

        # Create a message.
        self.date = datetime.now()
        self.message = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message', created_at=self.date)

        # Create a link unread.
        self.link_unread = Links.objects.create(message=self.message, url='http://unread.com')
        self.user_link_unread = UserLinks.objects.create(user=self.user, link=self.link_unread, favorite=False, read=False)

        # Create a link read.
        self.link_read = Links.objects.create(message=self.message, url='http://read.com')
        self.user_link_read = UserLinks.objects.create(user=self.user, link=self.link_read, favorite=False, read=True)

        # Create a link unfavorite.
        self.link_unfavorite = Links.objects.create(message=self.message, url='http://unfavorite.com')
        self.user_link_unfavorite = UserLinks.objects.create(user=self.user, link=self.link_unfavorite, favorite=False, read=False)

        # Create a link favorite.
        self.link_favorite = Links.objects.create(message=self.message, url='http://favorite.com',
            original_url='http://read.com')
        self.user_link_favorite = UserLinks.objects.create(user=self.user, link=self.link_favorite, favorite=True, read=True)

        # Create a link search in description.
        self.link_description = Links.objects.create(message=self.message, url='http://ops.com',
            original_url='http://zica.com', description='here have search in text.', title='Blabla title')
        self.user_link_description = UserLinks.objects.create(user=self.user, link=self.link_description, favorite=False, read=False)

        # Create a link search in title.
        self.link_title = Links.objects.create(message=self.message, url='http://ops.com',
            description='here do not have blabla in text.', title='Search Title ')
        self.user_link_title = UserLinks.objects.create(user=self.user, link=self.link_title, favorite=True, read=False)

        # Create a link search in title for other user.
        self.user_link_title2 = UserLinks.objects.create(user=self.user2, link=self.link_title, favorite=True, read=False)

        self.url = '/api/v1/user/links'

        self.url_with_identifier = '/api/v1/user/links/%i' % self.link_unread.id

        self.post_data = {
            'original_url': 'http://www.example.com',
            'url': 'http://www.example.com',
            'message': {
                'id': 1
            }
        }

    def test_get_userlinks_search_without_words(self):
        data = {'search': ''}
        self.assertEqual(UserLinks.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 6)

    def test_get_userlinks_search_with_word_in_title(self):
        data = {'search': 'Title'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_search_with_word_in_description(self):
        data = {'search': 'have'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_search_with_word_in_url(self):
        data = {'search': 'ops'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_search_with_word_in_original_url(self):
        data = {'search': 'zica'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)

    def test_get_userlinks_search_with_word_in_title_and_description(self):
        data = {'search': 'search'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_search_with_words_and_favorite(self):
        data = {'search': '#favorite search'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)
        self.assertEqual(self.deserialize(resp)[0]['favorite'], True)

    def test_get_userlinks_search_with_read(self):
        data = {'search': '#read'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)
        self.assertEqual(self.deserialize(resp)[0]['read'], True)

    def test_get_userlinks_search_with_unread(self):
        data = {'search': '#unread'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 4)
        self.assertEqual(self.deserialize(resp)[0]['read'], False)

    def test_get_userlinks_search_with_favorite(self):
        data = {'search': '#favorite'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)
        self.assertEqual(self.deserialize(resp)[0]['favorite'], True)

    def test_get_userlinks_search_unfavorite(self):
        data = {'search': '#unfavorite'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 4)
        self.assertEqual(self.deserialize(resp)[0]['favorite'], False)

    def test_get_userlinks_search_with_two_word(self):
        data = {'search': 'read favorite'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 4)

    def test_get_userlinks_search_with_two_word_and_favorite(self):
        data = {'search': 'read favorite #favorite'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)

    def test_get_userlinks_filter_url_with_url(self):
        data = {'url': 'http://ops.com'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_filter_url_with_original_url(self):
        data = {'url': 'http://zica.com'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)

    def test_get_userlinks_filter_url_with_url_and_original_url(self):
        data = {'url': 'http://read.com'}
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_userlinks_with_indentifier(self):
        resp = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['id'], self.link_unread.id)

    def test_post_userlinks_error_not_allowed(self):
        self.assertEqual(UserLinks.objects.count(), 7)
        self.assertHttpMethodNotAllowed(self.api_client.post(self.url, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        self.assertEqual(UserLinks.objects.count(), 7)

    def test_put_userlink_udpate_read(self):
        old_link = UserLinks.objects.get(id=self.link_unread.id)
        self.assertEqual(old_link.read, False)
        self.assertEqual(old_link.link.clicks, 0)

        userlink_original = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        userlink_original = self.deserialize(userlink_original)
        userlink_original["read"] = True

        self.assertHttpAccepted(self.api_client.put(self.url_with_identifier, format='json',
            data=userlink_original, authentication=get_credentials(self)))

        new_userlinks = UserLinks.objects.get(id=self.link_unread.id)
        self.assertEqual(new_userlinks.read, True)
        self.assertEqual(new_userlinks.link.clicks, 1)

    def test_put_userlink_udpate_favorite(self):
        old_link = UserLinks.objects.get(id=self.link_unread.id)
        self.assertEqual(old_link.favorite, False)
        self.assertEqual(old_link.link.clicks, 0)

        userlink_original = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        userlink_original = self.deserialize(userlink_original)
        userlink_original["favorite"] = True

        self.assertHttpAccepted(self.api_client.put(self.url_with_identifier, format='json',
            data=userlink_original, authentication=get_credentials(self)))

        new_userlinks = UserLinks.objects.get(id=self.link_unread.id)
        self.assertEqual(new_userlinks.favorite, True)
        self.assertEqual(new_userlinks.link.clicks, 0)

    def test_delete_userlinks_error_not_allowed(self):
        self.assertEqual(UserLinks.objects.count(), 7)
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))
        self.assertEqual(UserLinks.objects.count(), 7)
