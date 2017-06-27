"use strict";
angular.module('myApp.results', ['myApp.scanService'])
    .controller('ResultsController', function($scope, scanService) {

        $scope.scanData = scanService.getScanData();
        $scope.lastName = $scope.scanData.data.last_name_ocr;
        $scope.firstName = $scope.scanData.data.first_name_ocr;
        $scope.birthDate = $scope.scanData.data.birth_date_ocr;
        $scope.birthPlace = $scope.scanData.data.birth_place_ocr;

        $scope.convertDate = function (originalDate) {
            return originalDate[0]+originalDate[1]+'/'
                    +originalDate[2]+originalDate[3]+'/'
                    +originalDate[4]+originalDate[5]+originalDate[6]+originalDate[7];
        }

        $scope.convertFirstName = function (originalName) {
            var names = originalName.split(" ");
            var newFirstName = "";
            var name;
            for (name in names) {
                name = name[0].toUpperCase()
                +name.slice(1,name.length).toLowerCase();
                newFirstName = newFirstName + name;
            }
            return newFirstName;
        }


    });
