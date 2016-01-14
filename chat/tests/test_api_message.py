from django.contrib.auth.models import User
from chat.models import UserProfile, Message, Notification, Links, UserLinks, ConversationList
from tastypie.test import ResourceTestCase
from datetime import datetime
from chat.tests import create_user_loggedin, get_credentials


class MessageResourceTest(ResourceTestCase):
    def setUp(self):
        super(MessageResourceTest, self).setUp()

        self.user2 = User.objects.create_user(username='maximize', email='do@howtomaximize.com', password='123')
        UserProfile.objects.create(user=self.user2, avatar_url='http://www.howtomaximize.com')

        create_user_loggedin(self)

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)
        self.conversation.users.add(self.user2)

        self.message = Message.objects.create(conversation=self.conversation, message="teste message",
            created_at=datetime.now(), user=self.user)

    def test_post_message(self):
        data = {
            'message': 'test message',
            'conversation': {'id': self.conversation.pk}
        }

        self.assertEqual(Message.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(Message.objects.count(), 2)

    def test_post_verify_if_created_notifications(self):
        data = {
            'message': 'test message',
            'conversation': {'id': self.conversation.pk}
        }

        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(2, Notification.objects.all().count())
        self.assertEqual(1, Notification.objects.filter(user=self.user).count())
        self.assertEqual(1, Notification.objects.filter(user=self.user2).count())

    def test_post_new_message_without_link(self):
        data = {
            'message': 'Test Message',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(0, Links.objects.all().count())
        self.assertEqual(0, UserLinks.objects.all().count())

    def test_post_new_message_with_one_link(self):
        data = {
            'message': 'Test Message http://www.jandersonfc.com',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(1, Links.objects.all().count())
        self.assertEqual(2, UserLinks.objects.all().count())
        self.assertEqual(1, UserLinks.objects.filter(user=self.user).count())
        self.assertEqual(1, UserLinks.objects.filter(user=self.user2).count())

    def test_post_new_message_with_two_link(self):
        data = {
            'message': 'Test Message http://www.jandersonfc.com google.com',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(2, Links.objects.all().count())
        self.assertEqual(4, UserLinks.objects.all().count())
        self.assertEqual(2, UserLinks.objects.filter(user=self.user).count())
        self.assertEqual(2, UserLinks.objects.filter(user=self.user2).count())

    def test_post_new_message_link_is_image(self):
        data = {
            'message': 'Test Message http://www.jandersonfc.com/opa.jpg',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(0, Links.objects.all().count())
        self.assertEqual(0, UserLinks.objects.all().count())

    def test_post_new_message_with_link_owner_mark_as_unread(self):
        data = {
            'message': 'Test Message Test Message http://www.jandersonfc.com',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(1, Links.objects.all().count())
        self.assertEqual(2, UserLinks.objects.all().count())
        link1 = UserLinks.objects.get(user=self.user)
        link2 = UserLinks.objects.get(user=self.user2)
        self.assertFalse(link1.read)
        self.assertFalse(link2.read)

    def test_post_new_message_with_delivered_to_owner_of_message(self):
        data = {
            'message': 'Test Message Test Message http://www.jandersonfc.com',
            'conversation': {'id': self.conversation.pk}
        }
        self.assertHttpCreated(self.api_client.post('/api/v1/user/messages', format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(2, Notification.objects.all().count())
        self.assertEqual(1, Notification.objects.filter(user=self.user).count())
        self.assertEqual(1, Notification.objects.filter(user=self.user2).count())
        notification1 = Notification.objects.get(user=self.user)
        notification2 = Notification.objects.get(user=self.user2)
        self.assertTrue(notification1.delivered)
        self.assertFalse(notification2.delivered)
