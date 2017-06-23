"use strict";
angular.module('myApp.home', [])
  .controller('HomeController', function($scope, $location, $timeout) {
    // Pagination values
    $scope.currentPage = 0;
    $scope.pageSize = 10;

    // Minimum animation delay
    $timeout(function() {
      $scope.delaySpent = true;
    },500);
  })
  .filter('startFrom', function() {
    /*
     * For home page pagination. Used with builtin LimitTo filter.
     */
    return function(input, start) {
      // HACKFIX missing input
      var input0 = input || "";
      start = +start; //parse to int
      return input0.slice(start);
    };
  });
