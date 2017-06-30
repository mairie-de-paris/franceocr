"use strict";
angular.module('myApp.results', ['myApp.scanService'])
    .controller('ResultsController', function($scope, scanService) {

        //putting data from scanService in $scope variables
        $scope.scanData = scanService.getScanData();
        $scope.lastName = $scope.scanData.data.last_name_ocr;
        $scope.firstName = $scope.scanData.data.first_name_ocr;
        $scope.birthDate = $scope.scanData.data.birth_date_ocr;
        $scope.birthPlace = $scope.scanData.data.birth_place_ocr;
        //$scope.analyzedImgName = $scope.scanData.data.filename;
        //$scope.imgUrl = "https://mairie.till034.net/cni/scan/";
        $scope.processedImg = $scope.scanData.processedImg;

        $scope.convertDate = function (originalDate) {
            // convert daymonthyear to day/month/year
            return originalDate[0]+originalDate[1]+'/'
                +originalDate[2]+originalDate[3]+'/'
                +originalDate[4]+originalDate[5]+originalDate[6]+originalDate[7];
        }

        $scope.convertFirstName = function (originalName) {
            // convert CAPITAL LETTERS FIRSTNAME to Capital Letters Firstname
            var names = originalName.split(" ");
            var newFirstName = "";
            var i;
            for (i=0; i<names.length; i++) {
                names[i] = names[i][0].toUpperCase()
                    +names[i].slice(1,names[i].length).toLowerCase();
                newFirstName = newFirstName + " " + names[i];
            }
            return newFirstName.slice(1, newFirstName.length); // slice() to remove the first space
        }


    });
