define([
  'jquery',
  'underscore',
  'backbone',
  'model/LinkModel'
], function($, _, Backbone, LinkModel){
  
  var LinkCollection = Backbone.Collection.extend({
      model: LinkModel,
      url: "/api/v1/user/links",

      markAsRead: function(){
        return this.sync('update', this);
      }
  });

  return LinkCollection;

});
