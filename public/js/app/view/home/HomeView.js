define([
  'jquery',
  'underscore',
  'backbone',
  'view/conversation/ConversationView',
  'view/user/FollowingView',
  'text!templates/home/home.html'
], function($, _, Backbone, ConversationView, FollowingView, template){

  var HomeView = Backbone.View.extend({
    el: '#content',
    template:_.template(template),

    initialize: function() {

    },

    following: function(){
      this.followingView = new FollowingView();
      this.followingView.render();
    },
    
    conversation: function(){
      this.conversationView = new ConversationView();
      this.conversationView.render();
    },

    render: function(eventName) {
      $(this.el).html(this.template());
      
      this.conversation();
      this.following();
      
      return this;
    }

  });

  return HomeView;

});