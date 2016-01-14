define([
  'jquery',
  'underscore',
  'backbone',
  'collection/HistoryCollection',
  'view/notification/NotificationView',
  'text!templates/history/history.html'
], function($, _, Backbone, HistoryCollection, NotificationView, template){

  var HistoryView = Backbone.View.extend({
    model: new HistoryCollection(),
    el: '#history',
    template:_.template(template),

    initialize: function(conversation) {
        this.conversation = conversation;
        this.days = 1;
        this.model.bind('reset', this.show_notifications, this)
    },

    events: {
      'keypress #search-history': 'search_keypress',
      'click #history-1': function (event) {
        this.filter_history(1);
      },
      'click #history-7': function (event) {
        this.filter_history(7);
      },
      'click #history-14': function (event) {
        this.filter_history(14);
      },
      'click #history-30': function (event) {
        this.filter_history(30);
      },
      'click #history-90': function (event) {
        this.filter_history(90);
      }
    },

    show_notifications: function(){
      this.$('#notifications').empty();
      this.$('#search-history').removeClass('loader');

      _.each(this.model.models, function (item) {
          this.$('#notifications').append(new NotificationView({model:item}).render().el);
      }, this);
    },

    filter_history: function(days){
      if (this.days == days)
        this.days = 0;
      else
        this.days = days;
      this.render();
      this.search_history();
    },

    search_history: function(){
      var options = {}
      if ($.trim($('#search-history').val()) !== ''){
        options.search = $('#search-history').val();
      }
      if (this.days){
        options.days = this.days;
      }
      if (!_.isEmpty(options)){
        options.conversation = this.conversation.id;
        this.$('#search-history').addClass('loader');
        this.model.fetch({ reset: true, data: $.param(options) })
      }
    },

    search_keypress: function(event){
      if (event.which === 13 && event.shiftKey === false) {
        event.preventDefault();
        this.search_history();
      }
    },

    render: function() {
        this.search_history();
        $(this.el).html(this.template({days: this.days, search: $('#search-history').val()}));
        return this;
    }

  });

  return HistoryView;

});