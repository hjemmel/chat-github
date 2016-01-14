define([
  'jquery',
  'underscore',
  'backbone',
  'model/NotificationModel'
], function($, _, Backbone, Notification){
  
  var NotificationCollection = Backbone.Collection.extend({
      model: Notification,
      url: "/api/v1/user/notifications",

      markAsRead: function(){
        return this.sync('update', this);
      }
  });

  return NotificationCollection;

});
