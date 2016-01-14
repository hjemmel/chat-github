define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/user/user.html',
], function($, _, Backbone, template){

  var UserView = Backbone.View.extend({
    className: 'avatar',
    template:_.template(template),

    initialize: function() {
        this.model.bind("add", this.render, this);
        this.model.bind("remove", this.render, this);
    },

    render: function(eventName) {
      $(this.el).html(this.template({users: this.model.toJSON()}));
      return this;
    }

  });  

  return UserView;

});