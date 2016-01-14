define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var HistoryModel = Backbone.Model.extend({
      urlRoot: "/api/v1/user/history"
  });

  return HistoryModel;

});
