"use strict";
/*
 * Load app modules
 */
angular.module('myApp', [
  'ngRoute',
  'ngCookies',
  'ngAnimate',

  // Controller for navbar declared in ../index.html
  'myApp.navbar',

  // Partial views
  'myApp.home',
  'myApp.upload',
  // Loading bar for AJAX requests
  'cfp.loadingBarInterceptor',
])
/*
 * Set url routings
 */
  .config(function($routeProvider, cfpLoadingBarProvider) {
    $routeProvider
      .when('/home',
            { templateUrl: 'angular/views/home/home.html',
              controller: 'HomeController'})
      .when('/upload',
            { templateUrl: 'angular/views/upload/upload.html',
              controller: 'UploadController'})
      .otherwise({redirectTo: '/home'});

    // Disable loading bar spinner
    cfpLoadingBarProvider.includeSpinner = true;
  });
