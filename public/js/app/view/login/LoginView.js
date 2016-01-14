define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/login/login.html'
], function($, _, Backbone, template){

  var LoginView = Backbone.View.extend({
    el: '#content',
    template:_.template(template),

    initialize: function() {
        
    },

    render: function(eventName) {
        $(this.el).html(this.template());
        return this;
    }

  });

  return LoginView;

});