define([
  'jquery',
  'underscore',
  'socket',
  'backbone',
  'moment',
  'model/MessageModel',
  'collection/NotificationCollection',
  'collection/UserCollection',
  'view/notification/NotificationView',
  'view/user/UserView',
  'collection/UsersOnlineCollection',
  'text!templates/chat/chat.html',
  'playsound'
], function($, _, io, Backbone, moment, Message, NotificationCollection, UserCollection,  NotificationView, UserView, UsersOnlineCollection, template){

  var isForNotify = false;
  window.addEventListener('focus', function() {
      isForNotify = false;
  });

  window.addEventListener('blur', function() {
      isForNotify = true;
  });

  var ChatView = Backbone.View.extend({
    model: new NotificationCollection(),
    online: new UsersOnlineCollection(),
    el: '#chat',
    template:_.template(template),

    initialize: function(conversation) {
        this.conversation = conversation;
        this.model.bind("reset", this.update_model, this);

        this.refresh_messages();

        this.socket = socket;

        var self = this;

        window.socket.on('disconnect', function () {
          console.log('disconnect');
          self.refresh_users([]);
        });

        window.socket.on('refresh_messages', function () {
          console.log('NEW MENSAGEM');
          self.refresh_messages();
        });

        window.socket.on('nicknames_in_room', function (nicknames) {
          console.log('ROOM ' + nicknames);
          $('#button_send').removeAttr('disabled');
          $('#id_message').removeAttr('disabled');
          self.refresh_users($.parseJSON(nicknames));
        });
    },

    refresh_messages: function (){
      var options = {}
      options.conversation = this.conversation.id;
      options.reset = true;
      this.model.fetch(options);
    },

    update_model: function(){
      var quantNotifications = this.model.length;
      if (quantNotifications > 0){

        if (quantNotifications > 4){
            if (window.webkitNotifications) {
                if (window.webkitNotifications.checkPermission() === 0 && isForNotify === true) {
                    var notification = window.webkitNotifications.createNotification(null, quantNotifications+' New messages', 'You have '+quantNotifications+' new messages in the Chat for Github');

                    notification.onclick = function(){
                        window.focus();
                        notification.close();
                    };

                    notification.show();
                    $.playSound(window.location.origin + '/chat/media/notification.mp3');
                }
            }
        }

        _.each(this.model.models.reverse(), function (item) {
          if (quantNotifications <=4) {
            if (window.webkitNotifications) {
              if (window.webkitNotifications.checkPermission() === 0 &&
                  isForNotify === true &&
                  item.get('owner_message') === false) {
                  var name = item.get('message').user.first_name + ' ' + item.get('message').user.last_name;
                  var notification = window.webkitNotifications.createNotification(item.get('message').user.profile.avatar_url, name, item.get('message').message);

                  notification.onclick = function() {
                      window.focus();
                      notification.close();
                  };

                  notification.show();
                  $.playSound(window.location.origin + '/chat/media/notification.mp3');
              }
            }
          }
          this.renderNotification(item);
        }, this);

        this.model.markAsRead();

      }
    },

    events: {
      'keypress #id_message': 'submit_keypress',
      'click #button_send': 'submit',
      'click #button_notification': 'notificationSetup'
    },

    submit: function(){
      var message = $('#id_message').val();
      if ($.trim($('#id_message').val()) !== ''){
        
        var objMessage = new Message();
        objMessage.bind('request',this.request, this);
        objMessage.bind('sync',this.sync, this);

        objMessage.save({
          conversation: this.conversation,
          message: message
        });

      }
      return false;
    },

    submit_keypress: function(event){
      if (event.which === 13 && event.shiftKey === false) {
        event.preventDefault();
        this.submit();
      }
    },

    request: function(result) {
      $('#button_send').attr('disabled','disabled');
      $('#id_message').attr('disabled','disabled');
    },

    sync: function(result) {
      var date = moment(result.get('created_at')).format('DD/MM/YYYY HH:mm:ss');
      $('#id_message').val('');
      $('#id_message').focus();
      $('#return_send').html('<p><small>Latest message at '+date+'</small></p>');
      $('#button_send').removeAttr('disabled');
      $('#id_message').removeAttr('disabled');

      this.renderNotification(result);

      //notify for others users a new message
      this.socket.emit('message', true);
    },

    notificationSetup: function(){
      if (window.webkitNotifications) {
          window.webkitNotifications.requestPermission(function() {
              if (window.webkitNotifications.checkPermission() === 0){
                  $('#button_notification').hide();
              }
          });
          if (window.webkitNotifications.checkPermission() === 0){
              $('#button_notification').hide();
          }else {
              $('#button_notification').show();
          }
      }
    },

    renderNotification: function(notification){
      $(new NotificationView({model:notification}).render().el).hide().prependTo("#chat_live").fadeIn("slow");
    },

    refresh_users: function(nicknames){
      if (this.conversation.attributes.users){
        var users = new UserCollection(this.conversation.attributes.users);
        for (var i in users.models){
          users.models[i].set("online", false);
          for (var j in nicknames){
            if (nicknames[j] == users.models[i].get('username')) {
              users.models[i].set("online", true);
            }
          }
        }
        this.$('#users').html(new UserView({model:users}).render().el);
      }
    },

    render: function() {

      $(this.el).html(this.template());

      this.refresh_users([]);

      this.notificationSetup();
      return this;
    }


  });

  return ChatView;

});