from django.test import TestCase
from django.contrib.auth.models import User
from chat.models import UserProfile, Message, Links, UserLinks, Notification, ConversationList
from datetime import datetime


class UserProfileModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        # Create a User Profile.
        self.user_profile = UserProfile.objects.create(user=self.user,
                avatar_url='http://www.example.com')

    def test_get_user_in_profile_user(self):
        self.assertEqual(1, self.user_profile.user.pk)

    def test_get_user_profile_in_user(self):
        self.assertEqual('http://www.example.com', self.user.get_profile().avatar_url)


class ConversationListModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)

    def test_create_conversation(self):
        self.assertEqual(1, self.conversation.pk)
        self.assertEqual(self.user.id, self.conversation.pk)

    def test_unicode(self):
        self.assertEqual(u'My Conversation', unicode(self.conversation))


class MessageModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        self.conversation = ConversationList.objects.create()
        self.conversation.users.add(self.user)

        # Create a message.
        self.date = datetime.now()
        self.message = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message', created_at=self.date)

    def test_create_message(self):
        self.assertEqual(1, self.message.pk)

    def test_unicode(self):
        self.assertEqual(u'Test message', unicode(self.message))


class LinksModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        self.conversation = ConversationList.objects.create()
        self.conversation.users.add(self.user)

        # Create a message.
        self.date = datetime.now()
        self.message = Message.objects.create(conversation=self.conversation, user=self.user,
            message='Test message', created_at=self.date)

        # Create a link.
        self.link = Links.objects.create(message=self.message, url='http://someurl.com')

    def test_create_link(self):
        self.assertEqual(1, self.link.pk)


class LinksUserModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        self.conversation = ConversationList.objects.create()
        self.conversation.users.add(self.user)

        # Create a message.
        self.date = datetime.now()
        self.message = Message.objects.create(conversation=self.conversation,
            user=self.user, message='Test message', created_at=self.date)

        # Create a link.
        self.link = Links.objects.create(message=self.message, url='http://someurl.com')

        #Create a userlink
        self.user_link = UserLinks.objects.create(user=self.user, link=self.link, favorite=False, read=False)

    def test_create_user_links(self):
        self.assertEqual(1, self.user_link.pk)


class NotificationModelTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        #Create notifications
        self.date = datetime.now()

        self.notification = Notification.objects.create(user=self.user, type='M',
            description='Test notification', delivered=False, created_at=self.date)

    def test_create_notification(self):
        self.assertEqual(1, self.notification.pk)


class TypeNotificationManagerTest(TestCase):
    def setUp(self):
        # Create a user.
        self.username = 'janderson'
        self.password = '123'
        self.user = User.objects.create_user(self.username, 'jandersonfc.com@gmail.com', self.password)

        #Create notifications
        self.date = datetime.now()

        self.notification_message = Notification.objects.create(user=self.user, type='M',
            description='Test notification with type Message', delivered=False, created_at=self.date)

        self.notification_message_delivered = Notification.objects.create(user=self.user, type='M',
            description='Test notification with type Message and delivered', delivered=True, created_at=self.date)

        self.notification_status = Notification.objects.create(user=self.user, type='S',
            description='Test notification with type Status', delivered=False, created_at=self.date)

        self.notification_github = Notification.objects.create(user=self.user, type='G',
            description='Test notification with type Github', delivered=False, created_at=self.date)

    def test_all_message_pendind(self):
        self.assertEqual(1, Notification.objects.all_message_pendind(self.user).count())

    def test_all_status_pendind(self):
        self.assertEqual(1, Notification.objects.all_status_pendind(self.user).count())

    def test_all_github_pendind(self):
        self.assertEqual(1, Notification.objects.all_github_pendind(self.user).count())
