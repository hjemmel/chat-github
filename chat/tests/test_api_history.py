from django.contrib.auth.models import User
from chat.models import UserProfile, Message, Notification, ConversationList
from tastypie.test import ResourceTestCase
from datetime import datetime, timedelta
from chat.tests import create_user_loggedin, get_credentials


class HistoryResourceTest(ResourceTestCase):
    def setUp(self):
        super(HistoryResourceTest, self).setUp()

        create_user_loggedin(self)

        self.user2 = User.objects.create_user(username='maximize', email='do@howtomaximize.com', password='123')
        UserProfile.objects.create(user=self.user2, avatar_url='http://www.howtomaximize.com')

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)
        self.conversation.users.add(self.user2)

         # Create a message 1 day.
        self.date_1day = datetime.now() - timedelta(days=1)

        self.message_1day = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message 1 day ago', created_at=self.date_1day)

        self.notification_1day = Notification.objects.create(
            message=self.message_1day, created_at=self.date_1day,
            user=self.user, delivered=True)

        # Create a message 1 week ago.
        self.date_1week = datetime.now() - timedelta(days=7)

        self.message_1week = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message 1 week ago', created_at=self.date_1week)

        self.notification_1week = Notification.objects.create(
            message=self.message_1week, created_at=self.date_1week,
            user=self.user, delivered=True)

        # Create a message 2 week ago.
        self.date_2weeks = datetime.now() - timedelta(days=14)
        self.message_2weeks = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message 2 weeks ago', created_at=self.date_2weeks)

        self.notification_2weeks = Notification.objects.create(
            message=self.message_2weeks, created_at=self.date_2weeks,
            user=self.user, delivered=True)

        # Create a message 1 month ago.
        self.date_1month = datetime.now() - timedelta(days=30)
        self.message_1month = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message 1 month ago', created_at=self.date_1month)

        self.notification_1month = Notification.objects.create(
            message=self.message_1month, created_at=self.date_1month,
            user=self.user, delivered=True)

        self.notification_1month_other_user = Notification.objects.create(
            message=self.message_1month, created_at=self.date_1month,
            user=self.user2, delivered=False)

        # Create a message 3 months ago.
        self.date_3months = datetime.now() - timedelta(days=90)

        self.message_3months = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message 3 months ago', created_at=self.date_3months)

        self.notification_3months_other_user = Notification.objects.create(
            message=self.message_3months, created_at=self.date_3months,
            user=self.user, delivered=True)

        self.notification_3months = Notification.objects.create(
            message=self.message_3months, created_at=self.date_3months,
            user=self.user2, delivered=True)

        self.url = '/api/v1/user/history'

        self.url_with_identifier = '/api/v1/user/history/%i' % self.notification_3months.id

        self.post_data = {
            'original_url': 'http://www.example.com',
            'url': 'http://www.example.com',
            'message': {
                'id': 1
            }
        }

    def test_get_history_without_filters(self):
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 5)
        self.assertEqual(u'Test message 1 day ago', self.deserialize(resp)[0]['message']['message'])

    def test_get_history_filter_1day(self):
        data = {'days': 1}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)
        self.assertEqual(u'Test message 1 day ago', self.deserialize(resp)[0]['message']['message'])

    def test_get_history_filter_1week(self):
        data = {'days': 7}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)
        self.assertEqual(u'Test message 1 week ago', self.deserialize(resp)[1]['message']['message'])

    def test_get_history_filter_2weeks(self):
        data = {'days': 14}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 3)
        self.assertEqual(u'Test message 2 weeks ago', self.deserialize(resp)[2]['message']['message'])

    def test_get_history_filter_1month(self):
        data = {'days': 30}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 4)
        self.assertEqual(u'Test message 1 month ago', self.deserialize(resp)[3]['message']['message'])

    def test_get_history_filter_3months(self):
        data = {'days': 90}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 5)
        self.assertEqual(u'Test message 3 months ago', self.deserialize(resp)[4]['message']['message'])

    def test_get_history_search_without_words(self):
        data = {'search': ''}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 5)

    def test_get_history_search_with_word(self):
        data = {'search': 'week'}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)

    def test_get_history_search_with_two_words(self):
        data = {'search': 'week day'}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 3)

    def test_get_history_search_with_search_and_days(self):
        data = {'search': 'week', 'days': 7}
        self.assertEqual(Notification.objects.count(), 7)
        resp = self.api_client.get(self.url, format='json', data=data, authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)

    def test_post_history_error_not_allowed(self):
        self.assertEqual(Notification.objects.count(), 7)

        self.assertHttpMethodNotAllowed(self.api_client.post(self.url,
            format='json', data=self.post_data,
            authentication=get_credentials(self)))

        self.assertEqual(Notification.objects.count(), 7)

    def test_put_history_error_not_allowed(self):
        self.assertEqual(self.notification_3months.delivered, True)

        self.assertHttpMethodNotAllowed(
            self.api_client.put(self.url_with_identifier, format='json',
            data=self.post_data, authentication=get_credentials(self)))

        notification = Notification.objects.get(id=self.notification_3months.id)
        self.assertEqual(notification.delivered, True)

    def test_delete_history_error_not_allowed(self):
        self.assertEqual(Notification.objects.count(), 7)

        self.assertHttpMethodNotAllowed(
            self.api_client.delete(self.url_with_identifier,
                format='json', authentication=get_credentials(self)))

        self.assertEqual(Notification.objects.count(), 7)
