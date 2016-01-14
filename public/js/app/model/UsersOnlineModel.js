define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var UsersOnline = Backbone.Model.extend({
      urlRoot: "/api/v1/users/online"
  });

  return UsersOnline;

});