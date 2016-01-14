# coding: utf-8
from django.contrib.auth import logout
from social_auth.models import UserSocialAuth
from github import Github
from models import UserProfile
from django.http import HttpResponseRedirect, HttpResponse
from sockets import ChatNamespace
from socketio import socketio_manage


def disconnect(request):
    logout(request)
    return HttpResponseRedirect('/chat/index.html')


def login(request):
    if request.user.is_authenticated():
        github_user = get_github_user(request.user)
        try:
            request.user.first_name = github_user.name
            if github_user.email:
                request.user.email = github_user.email
            request.user.save()

            profile = request.user.get_profile()
            #update avatar_url of github
            profile.avatar_url = github_user.avatar_url

            profile.save()
        except UserProfile.DoesNotExist:
            #create userprofile
            UserProfile.objects.create(user=request.user,
                avatar_url=github_user.avatar_url)
    return HttpResponseRedirect('/chat/index.html')


def get_github_user(user):
    instance = UserSocialAuth.objects.filter(provider='github').get(user_id=user)
    userGitHub = Github(instance.tokens['access_token'])
    return userGitHub.get_user()


def socketio(request):
    socketio_manage(request.environ,
        {
            '': ChatNamespace,
        }, request=request
    )
    return HttpResponse()
