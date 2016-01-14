require.config({
  paths: {
    jquery: '../libs/jquery-1.8.2.min',
    playsound: '../libs/jquery.playsound',
    underscore: '../libs/underscore',
    backbone: '../libs/backbone',
    poller: '../libs/backbone.poller',
    text: '../libs/text',
    moment: '../libs/moment.min',
    socket: '../libs/socket.io',
    templates: '../../templates'
  },
  shim: {
        'backbone': {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        'underscore': {
            exports: '_'
        },
        'moment': {
            exports: 'moment'
        },
        'poller': {
            deps: ['backbone'],
            exports: 'poller'
        },
        'playsound': {
            deps: ['jquery'],
            exports: 'jQuery.fn.playSound'
        },
        'socket': {
            exports: 'io'
        }
    }
});

require([
  'backbone',  
  'router'
], function(Backbone, Router){
    var app = new Router
    Backbone.history.start();
});
