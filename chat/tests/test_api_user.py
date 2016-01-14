from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from chat.tests import create_user_loggedin, get_credentials


class UserResourceTest(ResourceTestCase):
    def setUp(self):
        super(UserResourceTest, self).setUp()

        create_user_loggedin(self)

        self.url = '/api/v1/user/'

        self.user2 = User.objects.create_user(username='janderson', email='jandersonfc@maximizeconsultoria.com.br', password='123')
        self.user2.first_name = 'Janderson'
        self.user2.last_name = 'Cardoso'
        self.user2.save()

        self.url_with_identifier = '/api/v1/user/%i' % self.user.id

        self.url_with_identifier2 = '/api/v1/user/%i' % self.user2.id

        self.post_data = {
            'first_name': 'Janderson F. Cardoso'
        }

    def test_get_user_loggedin(self):
        self.assertEqual(User.objects.count(), 2)
        resp = self.api_client.get(self.url, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['id'], self.user.id)

    def test_get_user_with_indentifier(self):
        self.assertEqual(User.objects.count(), 2)
        resp = self.api_client.get(self.url_with_identifier, format='json', authentication=get_credentials(self))
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['id'], self.user.id)

    def test_get_user_with_indentifier_not_found(self):
        self.assertHttpNotFound(self.api_client.get(self.url_with_identifier2,
            format='json', authentication=get_credentials(self)))

    def test_post_user_error_not_allowed(self):
        self.assertEqual(User.objects.count(), 2)
        self.assertHttpMethodNotAllowed(self.api_client.post(self.url, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        self.assertEqual(User.objects.count(), 2)

    def test_put_user_error_not_allowed(self):
        self.assertEqual(self.user.username, "jandersonfc")
        self.post_data["username"] = "janderson"
        self.assertHttpMethodNotAllowed(self.api_client.put(self.url_with_identifier, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.username, "jandersonfc")

    def test_delete_user_error_not_allowed(self):
        self.assertEqual(User.objects.count(), 2)
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))
        self.assertEqual(User.objects.count(), 2)
