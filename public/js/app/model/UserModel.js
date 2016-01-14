define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var User = Backbone.Model.extend({
      urlRoot: "/api/v1/user"
  });

  return User;

});
