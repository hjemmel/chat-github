define([
  'jquery',
  'underscore',
  'backbone',
  'model/UserModel',
  'model/ConversationModel',
  'view/SidebarView',
  'view/login/LoginView',
  'view/home/HomeView',
  'view/conversation/ConversationOpenView'
], function($, _, Backbone, User, ConversationModel, SidebarView, LoginView, HomeView, ConversationOpenView){

    window.socket = io.connect();

    window.socket.on('connect', function () {
        console.log('Connected');
        window.socket.emit('connect');
    });

    window.socket.on('reconnect', function () {
        console.log('Reconnected in Application');
        window.socket.emit('connect');
    });

    window.socket.on('error', function (e) {
        console.log('System', e ? e : 'A unknown error occurred');
    });

    window.socket.on('announcement', function (msg) {
        console.log(msg);
    });

    var AppRouter = Backbone.Router.extend({
      
      routes:{
          "":"index",
          "home":"home",
          "login":"login",
          "conversation/:id":"conversation_open"
      },

      setCurrentUser: function(){
        this.user = new User(); 
        this.user.bind("sync", this.loggedIn, this);
        this.user.bind("error", this.error, this);
        this.user.fetch({reset: true});
      },

      loggedIn: function(){
        if (this.conversationOpenView){
          this.conversationOpenView.leave_room();
        }
        var direct_to = Backbone.history.fragment;
        if (direct_to == '') direct_to = 'home'
        Backbone.history.loadUrl(direct_to,{trigger: true, replace: true});
      },

      error: function(model, error){
        if (error.status == 401){
          Backbone.history.loadUrl('login',{trigger: true, replace: true});
        }
      },

      index: function(){
        this.setCurrentUser();
      },

      login: function() {
          this.loginView = new LoginView();
          this.loginView.render();
      },

      sidebar: function(){
        if (!this.user){
          this.setCurrentUser()
          return false;
        }
        if (!this.sidebarView) {
          this.sidebarView = new SidebarView({model: this.user})
          this.sidebarView.render();
        } 
        return true;
      },

      home: function() {
        this.sidebar();
        this.homeView = new HomeView();
        this.homeView.render();
      },

      conversation_open: function(id){
        if (this.sidebar()){
          this.conversationModel = new ConversationModel({id: id});
          this.conversationOpenView = new ConversationOpenView({model:this.conversationModel})
        }
      }

  });
  
  return AppRouter;

});