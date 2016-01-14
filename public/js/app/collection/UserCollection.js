define([
  'jquery',
  'underscore',
  'backbone',
  'model/UserModel'
], function($, _, Backbone, User){
  
  var UserCollection = Backbone.Collection.extend({
      model: User,
      url: "/api/v1/users/online",
  });

  return UserCollection;

});
