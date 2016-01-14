from django.contrib.auth.models import User
from chat.models import UserProfile, ConversationList
from tastypie.test import ResourceTestCase
from chat.tests import create_user_loggedin, get_credentials


class ConversationListResourceTest(ResourceTestCase):
    def setUp(self):
        super(ConversationListResourceTest, self).setUp()

        create_user_loggedin(self)

        self.user2 = User.objects.create_user(username='maximize', email='do@howtomaximize.com', password='123')
        UserProfile.objects.create(user=self.user2, avatar_url='http://www.howtomaximize.com')

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)

        self.url = '/api/v1/conversation'

        self.url_with_identifier = '/api/v1/conversation/%i' % self.conversation.id

    def test_get_my_conversation(self):
        self.assertEqual(ConversationList.objects.count(), 1)
        resp = self.api_client.get(self.url, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)), 1)

    def test_post_conversation(self):
        data = {
            'name': 'maximize ideas',
            'users': [
               {'id':2}
            ]
        }

        self.assertEqual(ConversationList.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post(self.url, format='json',
            data=data, authentication=get_credentials(self)))
        self.assertEqual(ConversationList.objects.count(), 2)

    def test_put_conversation(self):
        self.assertEqual(self.conversation.name, 'My Conversation')

        conversation_original = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        conversation_original = self.deserialize(conversation_original)
        conversation_original["name"] = 'maximize ideas'

        self.assertHttpAccepted(
            self.api_client.put(self.url_with_identifier, format='json',
            data=conversation_original, authentication=get_credentials(self)))

        conversation = ConversationList.objects.get(id=self.conversation.id)
        self.assertEqual(conversation.name, 'maximize ideas')

    def test_delete_conversation_error_not_allowed(self):
        self.assertEqual(ConversationList.objects.count(), 1)

        self.assertHttpMethodNotAllowed(
            self.api_client.delete(self.url_with_identifier,
                format='json', authentication=get_credentials(self)))

        self.assertEqual(ConversationList.objects.count(), 1)
