from chat.models import Message, Links, ConversationList
from tastypie.test import ResourceTestCase
from datetime import datetime
from chat.tests import create_user_loggedin, get_credentials


class LinksResourceTest(ResourceTestCase):
    def setUp(self):
        super(LinksResourceTest, self).setUp()

        create_user_loggedin(self)

        self.conversation = ConversationList.objects.create(name='My Conversation')
        self.conversation.users.add(self.user)

        # Create a message.
        self.date = datetime.now()
        self.message = Message.objects.create(conversation=self.conversation,
            user=self.user, message='Test message', created_at=self.date)

        # Create a link.
        self.link = Links.objects.create(message=self.message, url='http://someurl.com')

        self.url = '/api/v1/links'

        self.url_with_identifier = '/api/v1/links/%i' % 1

        self.post_data = {
            'original_url': 'http://www.example.com',
            'url': 'http://www.example.com',
            'message': {
                'id': 1
            }
        }

    def test_get_all_links_error_not_allowed(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.url, format='json',
            authentication=get_credentials(self)))

    def test_get_link_error_not_allowed(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))

    def test_post_link_error_not_allowed(self):
        self.assertEqual(Links.objects.count(), 1)
        self.assertHttpMethodNotAllowed(self.api_client.post(self.url, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        self.assertEqual(Links.objects.count(), 1)

    def test_put_link_error_not_allowed(self):
        self.assertEqual(self.link.url, "http://someurl.com")
        self.assertHttpMethodNotAllowed(self.api_client.put(self.url_with_identifier, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        new_link = Links.objects.get(id=self.link.id)
        self.assertEqual(new_link.url, "http://someurl.com")

    def test_delete_profile_error_not_allowed(self):
        self.assertEqual(Links.objects.count(), 1)
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))
        self.assertEqual(Links.objects.count(), 1)
