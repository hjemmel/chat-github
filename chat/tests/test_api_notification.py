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
            user=self.user, delivered=False)

        self.notification_1day_other_user = Notification.objects.create(
            message=self.message_1day, created_at=self.date_1day,
            user=self.user2, delivered=False)

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
            user=self.user, delivered=False)

        self.url = '/api/v1/user/notifications'

        self.url_with_identifier = '/api/v1/user/notifications/%i' % self.notification_1day.id

        self.post_data = {
            'original_url': 'http://www.example.com',
            'url': 'http://www.example.com',
            'message': {
                'id': 1
            }
        }

    def test_get_history_search_with_search_and_days(self):
        self.assertEqual(Notification.objects.count(), 4)
        resp = self.api_client.get(self.url, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 2)
        self.assertEqual(self.deserialize(resp)[0]['delivered'], False)

    def test_post_notification_error_not_allowed(self):
        self.assertEqual(Notification.objects.count(), 4)

        self.assertHttpMethodNotAllowed(self.api_client.post(self.url,
            format='json', data=self.post_data,
            authentication=get_credentials(self)))

        self.assertEqual(Notification.objects.count(), 4)

    def test_put_detail_notification(self):
        notification_1day = Notification.objects.get(id=self.notification_1day.id)
        self.assertFalse(notification_1day.delivered)

        notification = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        notification = self.deserialize(notification)
        notification["delivered"] = True

        self.assertHttpAccepted(self.api_client.put(self.url_with_identifier, format='json',
            data=notification, authentication=get_credentials(self)))

        notification_1day = Notification.objects.get(id=self.notification_1day.id)
        self.assertTrue(notification_1day.delivered)

    def test_put_list_notification(self):
        notification_1day = Notification.objects.get(id=self.notification_1day.id)
        self.assertFalse(notification_1day.delivered)

        notification_2weeks = Notification.objects.get(id=self.notification_2weeks.id)
        self.assertFalse(notification_2weeks.delivered)

        all_notification = self.api_client.get(self.url, format='json', authentication=get_credentials(self))
        all_notification = self.deserialize(all_notification)
        self.assertFalse(all_notification[0]["delivered"])
        self.assertFalse(all_notification[1]["delivered"])

        self.assertHttpAccepted(self.api_client.put(self.url, format='json',
            data=all_notification, authentication=get_credentials(self)))

        notification_1day = Notification.objects.get(id=self.notification_1day.id)
        self.assertTrue(notification_1day.delivered)

        notification_2weeks = Notification.objects.get(id=self.notification_2weeks.id)
        self.assertTrue(notification_2weeks.delivered)

    def test_delete_notification_error_not_allowed(self):
        self.assertEqual(Notification.objects.count(), 4)

        self.assertHttpMethodNotAllowed(
            self.api_client.delete(self.url_with_identifier,
                format='json', authentication=get_credentials(self)))

        self.assertEqual(Notification.objects.count(), 4)
