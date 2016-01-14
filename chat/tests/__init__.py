from django.contrib.auth.models import User
from chat.models import UserProfile
from datetime import datetime

def create_user_loggedin(self):
    self.user = User.objects.create_user(username='jandersonfc', email='jandersonfc.com@gmail.com', password='123')
    self.user.first_name = 'Janderson'
    self.user.last_name = 'Cardoso'
    self.user.save()
    UserProfile.objects.create(user=self.user, avatar_url='http://www.example.com')
    self.logged_in = self.client.login(username='jandersonfc', password='123')
    session = self.client.session
    session['last_activity'] = datetime.now()
    session.save()

def get_credentials(self):
    return self.create_basic(username='jandersonfc', password='123')