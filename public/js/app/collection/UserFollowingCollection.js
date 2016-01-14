define([
  'jquery',
  'underscore',
  'backbone',
  'model/UserFollowingModel'
], function($, _, Backbone, UserFollowing){
  
  var UserFollowingCollection = Backbone.Collection.extend({
      model: UserFollowing,
      url: "/api/v1/user/following",
  });

  return UserFollowingCollection;

});
