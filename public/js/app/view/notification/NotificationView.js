define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/notification/notification-message.html',
  'collection/LinkCollection'
], function($, _, Backbone, templateNotificationMessage, LinkCollection){

  var NotificationView = Backbone.View.extend({
    linkCollection: new LinkCollection(),
    tagName: 'li',
    className: 'separator',
    template:_.template(templateNotificationMessage),

    initialize: function() {
        this.linkCollection.bind("reset", this.update_link, this)
    },

    events: {
      "click .link":"read_link"
    },

    update_link: function(){

      if (this.linkCollection.length > 0){
        
        _.each(this.linkCollection.models, function (item) {
            item.save({read: true})
            this.linkCollection.remove(item,{silent: true})
        }, this);

      }
    },

    read_link: function(e){
      var url = $(e.target).attr('href');
      if (url){
        this.linkCollection.fetch({ reset: true, data: $.param({url: url}) })
      }
    },

    render: function(eventName) {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }

  });

  return NotificationView;

});