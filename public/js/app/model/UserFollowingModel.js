define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var UserFollowing = Backbone.Model.extend({
      urlRoot: "/api/v1/users/following"
  });

  return UserFollowing;

});