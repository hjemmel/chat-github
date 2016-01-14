define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var Notification = Backbone.Model.extend({
      urlRoot: "/api/v1/user/notifications"
  });

  return Notification;

});
