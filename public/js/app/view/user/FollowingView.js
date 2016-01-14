define([
  'jquery',
  'underscore',
  'backbone',
  'collection/UserFollowingCollection',
  'model/ConversationModel',
  'text!templates/user/following.html',
  'text!templates/user/following-item.html',
  'poller'
], function($, _, Backbone, UserFollowingCollection, ConversationModel, template, templateFollowingItem){

  var FollowingItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'separator',
    template:_.template(templateFollowingItem),

    initialize: function() {
        this.model.bind("sync", this.render, this)
    },

    events: {
      "click .add-conversation": "add_conversation",
      "click .invite-user": "invite_user"
    },

    add_conversation: function(){
      var conversation = new ConversationModel();

      conversation.bind('sync',this.returnConversation, this);

      conversation.save({
        users: [ this.model.attributes.user ]
      });

    },

    returnConversation: function(result){
      Backbone.history.navigate('/conversation/'+result.get('id'),{trigger: true, replace: true})
    },

    invite_user: function(){
      //TODO: implement here
    },

    render: function(eventName) {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }

  });  

  var FollowingView = Backbone.View.extend({
    model: new UserFollowingCollection(),
    el: '#contacts',
    template:_.template(template),

    initialize: function() {
        this.model.bind('reset', this.show_following, this);
        
        this.poller = Backbone.Poller.get(this.model, {delay: 300000}); // 5 minutes 

        this.refresh(this);
    },

    refresh: function(that){
      if (!that.poller.active()) that.poller.start();
      setTimeout(function(){
        that.refresh(that);
      }, 60000);
    },

    events: {
      'keypress #search-following': 'search_keypress'
    },

    show_following: function(){
      this.$('#following-list').empty();

      _.each(this.model.models, function (item) {
          this.$('#following-list').append(new FollowingItemView({model:item}).render().el);
      }, this);
    },

    search_following: function(){
      //TODO: implement here
    },

    search_keypress: function(event){
      if (event.which === 13) {
        event.preventDefault();
        this.search_following();
      }
    },

    render: function(eventName) {
        $(this.el).html(this.template());
        return this;
    }

  });

  return FollowingView;

});