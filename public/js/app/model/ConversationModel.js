define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var ConversationModel = Backbone.Model.extend({
      urlRoot: "/api/v1/conversation"
  });

  return ConversationModel;

});
