from chat.models import UserProfile
from tastypie.test import ResourceTestCase
from chat.tests import create_user_loggedin, get_credentials


class UserProfileResourceTest(ResourceTestCase):
    def setUp(self):
        super(UserProfileResourceTest, self).setUp()

        create_user_loggedin(self)

        self.url = '/api/v1/profiles/'

        self.url_with_identifier = '/api/v1/profiles/%i' % self.user.get_profile().id

        self.post_data = {
            'avatar_url': 'http://www.example.com',
            'user': {
                'id': self.user.id
            }
        }

    def test_get_all_profiles_error_not_allowed(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.url, format='json',
            authentication=get_credentials(self)))

    def test_get_profile_error_not_allowed(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))

    def test_post_profile_error_not_allowed(self):
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertHttpMethodNotAllowed(self.api_client.post(self.url, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_put_profile_error_not_allowed(self):
        self.assertEqual(self.user.get_profile().avatar_url, "http://www.example.com")
        self.post_data["avatar_url"] = "www.update.com"
        self.assertHttpMethodNotAllowed(self.api_client.put(self.url_with_identifier, format='json',
            data=self.post_data, authentication=get_credentials(self)))
        new_userprofile = UserProfile.objects.get(id=self.user.get_profile().id)
        self.assertEqual(new_userprofile.avatar_url, "http://www.example.com")

    def test_delete_profile_error_not_allowed(self):
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.url_with_identifier, format='json',
            authentication=get_credentials(self)))
        self.assertEqual(UserProfile.objects.count(), 1)
