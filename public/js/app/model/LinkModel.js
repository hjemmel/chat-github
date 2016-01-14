define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){
  
  var LinkModel = Backbone.Model.extend({
      urlRoot: "/api/v1/user/links"
  });

  return LinkModel;

});
