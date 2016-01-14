define([
  'jquery',
  'underscore',
  'backbone',
  'collection/LinkCollection',
  'text!templates/links/links.html',
  'text!templates/links/link-item.html',
], function($, _, Backbone, LinkCollection, template, templateLinkItem){

  var LinkItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'separator',
    template:_.template(templateLinkItem),

    initialize: function() {
        this.model.bind("sync", this.render, this)
    },

    events: {
      "click .favorite": "togle_favorite",
      "click .read": "togle_read",
      "click .link": "read_link"
    },

    togle_favorite: function(){
      this.model.set({favorite: !this.model.get('favorite')});
      this.render();
      this.model.save();
    },

    togle_read: function(){
      this.model.set({read: !this.model.get('read')});
      this.render();
      this.model.save();
    },

    read_link: function(){
      this.model.set({read: true});
      this.render();
      this.model.save();
    },

    render: function(eventName) {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }

  });  

  var LinkView = Backbone.View.extend({
    model: new LinkCollection(),
    el: '#bookmarks',
    template:_.template(template),

    initialize: function(conversation) {
        this.conversation = conversation;
        this.model.bind('reset', this.show_links, this);
        
        var options = {};
        options.search = '#unread';

        var self = this;

        window.socket.on('refresh_links', function () {
            console.log('REFRESH LINKS');
            if ($.trim($('#search-links').val()) === ''){
              self.get_links(options);
            }
        });

        this.get_links(options);
    },

    get_links: function(options){
      if (!_.isEmpty(options)){
        options.conversation = this.conversation.id;
        this.model.fetch({ reset: true, data: $.param(options) });
      }
    },

    unread: function() {
      if ($.trim($('#search-links').val()) === ''){
        var options = {};
        options.search = '#unread';
        this.get_links(options);
      }
    },

    events: {
      'keypress #search-links': 'search_keypress'
    },

    show_links: function(){
      this.$('#links').empty();
      this.$('#search-links').removeClass('loader');

      var links = this.model.clone();

      _.each(links.models.reverse(), function (item) {
          this.$('#links').prepend(new LinkItemView({model:item}).render().el);
      }, this);
    },

    search_links: function(){
      var options = {};
      if ($.trim($('#search-links').val()) !== ''){
        options.search = $('#search-links').val();
        this.$('#search-links').addClass('loader');
      } else {
        this.$('#search-links').addClass('loader');
        options.search = '#unread';
      }
      this.get_links(options);
    },

    search_keypress: function(event){
      if (event.which === 13) {
        event.preventDefault();
        this.search_links();
      }
    },

    render: function(eventName) {
        $(this.el).html(this.template());
        return this;
    }

  });

  return LinkView;

});