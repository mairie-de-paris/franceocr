"use strict";
angular.module('myApp.navbar', [])

  .controller('NavbarController', function($scope, $location) {
    $scope.isActive = function(viewLocation) {
      return viewLocation === $location.path();
    };
  });
