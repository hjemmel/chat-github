define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/sidebar.html'
], function($, _, Backbone, template){

  var SidebarView = Backbone.View.extend({
    el: '#user',
    template:_.template(template),

    initialize: function() {
      this.model.bind("reset", this.render, this);
    },

    render: function(eventName) {
      $(this.el).html(this.template({user: this.model.toJSON()}));
      return this;
    }

  });

  return SidebarView;

});