define([
  'jquery',
  'underscore',
  'backbone',
  'model/UsersOnlineModel'
], function($, _, Backbone, UsersOnline){
  
  var UsersOnlineCollection = Backbone.Collection.extend({
      model: UsersOnline,
      url: "/api/v1/users/online",
  });

  return UsersOnlineCollection;

});
