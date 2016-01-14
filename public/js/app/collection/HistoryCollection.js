define([
  'jquery',
  'underscore',
  'backbone',
  'model/HistoryModel'
], function($, _, Backbone, HistoryModel){
  
  var HistoryCollection = Backbone.Collection.extend({
      model: HistoryModel,
      url: "/api/v1/user/history",
  });

  return HistoryCollection;

});
