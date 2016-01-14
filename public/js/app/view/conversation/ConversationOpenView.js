define([
  'jquery',
  'underscore',
  'backbone',
  'view/chat/ChatView',
  'view/history/HistoryView',
  'view/links/LinkView',
  'view/user/UserView',
  'collection/UserCollection',
  'text!templates/conversation/conversation.html'
], function($, _, Backbone, ChatView, HistoryView, LinkView, UserView, UserCollection, template){

  var ConversationOpenView = Backbone.View.extend({
    el: '#content',
    template:_.template(template),

    initialize: function() {
        this.model.bind("sync", this.render_columns, this)
        this.model.bind("error", this.error, this)
        this.model.fetch({reset: true})
    },

    error: function(model, error){
      if (error.status == 404){
        Backbone.history.navigate('home',{trigger: true, replace: true});
      }
    },

    //events: {
    //  'click #button_add_user': 'open_popup_add_user'
    //},

    chat: function(conversation) {
      this.chatView = new ChatView(conversation, this.socket);
      this.chatView.render();
    },

    history: function(conversation){
      this.historyView = new HistoryView(conversation);
      this.historyView.render();
    },

    links: function(conversation){
      this.linkView = new LinkView(conversation, this.socket);
      this.linkView.render();
    },

    render_columns: function(){
      this.render();

      this.chat(this.model);
      this.history(this.model);
      this.links(this.model);

      this.join_room();
    },

    join_room: function(){
      window.socket.emit('join', 'conversation-'+this.model.id);
    },

    leave_room: function(){
      //clear all chat
      this.chatView.unbind();
      this.chatView.remove();
      this.chatView.model.unbind("reset");
      window.socket.removeAllListeners('refresh_messages');
      window.socket.removeAllListeners('nicknames_in_room');

      //clear all link
      this.linkView.unbind();
      this.linkView.remove();
      this.linkView.model.unbind("reset");
      window.socket.removeAllListeners('refresh_links');
      
      window.socket.emit('leave', 'conversation-'+this.model.id);
    },

    render: function() {
      $(this.el).html(this.template(this.model.toJSON()));

      if (this.model.attributes.users){
        var users = new UserCollection(this.model.attributes.users);
        this.$('#users').html(new UserView({model:users}).render().el);
      }

      return this;
    }

  });

  return ConversationOpenView;

});