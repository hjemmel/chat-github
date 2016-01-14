# coding: utf-8
from django.db import models
from django.contrib.auth.models import User


class TypeNotificationManager(models.Manager):

    def _all_notification_query(self, type, user):
        qs = self.filter(type=type)
        qs = qs.filter(delivered=False)
        qs = qs.filter(user=user)
        qs = qs.order_by('created_at')
        return qs

    def all_message_pendind(self, user):
        return self._all_notification_query('M', user)

    def all_status_pendind(self, user):
        return self._all_notification_query('S', user)

    def all_github_pendind(self, user):
        return self._all_notification_query('G', user)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar_url = models.URLField()


class ConversationList(models.Model):
    name = models.CharField(max_length=255, null=False, blank=True, default='')
    users = models.ManyToManyField(User, related_name="users")

    def __unicode__(self):
        return self.name


class Message(models.Model):
    conversation = models.ForeignKey(ConversationList, null=True)
    user = models.ForeignKey(User)
    message = models.TextField()
    created_at = models.DateTimeField()

    def __unicode__(self):
        return self.message


class Links(models.Model):
    message = models.ForeignKey(Message)
    url = models.URLField(blank=False, null=False)
    original_url = models.URLField(null=False, blank=True, default='')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    clicks = models.IntegerField(default=0)


class UserLinks(models.Model):
    user = models.ForeignKey(User)
    link = models.ForeignKey(Links)
    favorite = models.BooleanField()
    read = models.BooleanField()


class Notification(models.Model):
    TYPES = (
        ('M', 'Message'),
        ('S', 'Status'),
        ('G', 'Github'),
    )

    objects = TypeNotificationManager()

    user = models.ForeignKey(User)
    type = models.CharField(max_length=1, choices=TYPES)
    message = models.ForeignKey(Message, null=True)
    description = models.CharField(max_length="100", blank=True, null=True,)
    delivered = models.BooleanField()
    created_at = models.DateTimeField()
