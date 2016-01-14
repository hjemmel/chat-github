define([
  'jquery',
  'underscore',
  'backbone',
  'model/ConversationModel'
], function($, _, Backbone, ConversationModel){
  
  var ConversationCollection = Backbone.Collection.extend({
      model: ConversationModel,
      url: "/api/v1/conversation",
  });

  return ConversationCollection;

});
