from django.test import TestCase
from chat.tests import create_user_loggedin


class TestUserLoginMock(TestCase):
    def setUp(self):
        create_user_loggedin(self)

    def test_verify_user_loggedin(self):
        self.assertTrue(self.logged_in)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)


class TestDisconnectView(TestCase):
    def setUp(self):
        create_user_loggedin(self)

    def test_get_disconnect(self):
        response = self.client.get('/disconnect/')
        self.assertEqual(302, response.status_code)
        self.assertNotIn('_auth_user_id', self.client.session)
