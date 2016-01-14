define([
  'jquery',
  'underscore',
  'backbone',
  'collection/ConversationCollection',
  'collection/UserCollection',
  'model/ConversationModel',
  'view/user/UserView',
  'text!templates/conversation/conversations.html',
  'text!templates/conversation/conversation-item.html'
], function($, _, Backbone, ConversationCollection, UserCollection, ConversationModel, UserView, template, templateConversationItem){

  var ConversationItemView = Backbone.View.extend({
    template:_.template(templateConversationItem),

    initialize: function() {
        this.model.bind("sync", this.render, this)

        var self = this;
        window.socket.on('nicknames', function (nicknames) {
          console.log(nicknames);
          self.refresh_users($.parseJSON(nicknames));
        });

        window.socket.on('disconnect', function () {
          console.log('disconnect');
          self.refresh_users([]);
        });
    },

    events: {
      'keypress #name': 'save_keypress',
      "click #edit"   : "edit",
      "click #save"   : "save",
      "click #cancel" : "cancel",
    },

    edit: function(){
      event.preventDefault();
      this.render(true);
    },

    save_keypress: function(event){
      if (event.which === 13) {
        event.preventDefault();
        this.save();
      }
    },

    save: function(){
      var name = $('#name').val();
      this.model.save({name: name});
    },

    cancel: function(){
      event.preventDefault();
      this.render(false);
    },

    refresh_users: function(nicknames){
      if (this.model.attributes.users){
        var users = new UserCollection(this.model.attributes.users);
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

    render: function(editState) {
      if (editState == undefined) editState = false;
      $(this.el).html(this.template({model: this.model.toJSON(), editState: editState}));

      this.refresh_users([]);

      return this;
    }

  });

  var ConversationView = Backbone.View.extend({
    model: new ConversationCollection(),
    el: '#conversations',
    template:_.template(template),

    initialize: function() {
        this.model.bind('reset', this.show_conversations, this);
    },

    events: {
      "click #new-conversation" : "new_conversation"
    },

    new_conversation: function(){
      var conversation = new ConversationModel();

      conversation.bind('sync',this.returnConversation, this);

      conversation.save();
    },

    returnConversation: function(result){
      this.model.fetch({reset: true});
    },

    show_conversations: function(){
      this.$('#conversation-list').empty();

      var conversations = this.model.clone()

      _.each(conversations.models.reverse(), function (item) {
        this.$('#conversation-list').append(new ConversationItemView({model:item}).render().el);
      }, this);
    },

    render: function(eventName) {
        this.model.fetch({reset: true});
        $(this.el).html(this.template());
        return this;
    }

  });

  return ConversationView;
});