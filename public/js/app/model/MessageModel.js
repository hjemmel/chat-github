define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var Message = Backbone.Model.extend({
      urlRoot: "/api/v1/user/messages"
  });

  return Message;

});
