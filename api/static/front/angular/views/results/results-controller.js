"use strict";
angular.module('myApp.results', ['myApp.scanService'])
    .controller('ResultsController', function($scope, $sce, $http, scanService) {

        //putting data from scanService in $scope variables
        $scope.scanData = scanService.getScanData();
        $scope.prettyScanData = JSON.stringify($scope.scanData, null, 4);
        $scope.lastName = $scope.scanData.data.validated.last_name;
        $scope.firstName = $scope.scanData.data.validated.first_name;
        $scope.birthDate = $scope.scanData.data.validated.birth_date;
        $scope.birthPlace = $scope.scanData.data.ocr.birth_place;
        $scope.birthCityExists = $scope.scanData.data.validated.birth_place_exists;
        $scope.convertedBirthPlace = $scope.scanData.data.validated.birth_place;
        $scope.similarBirthCities = $scope.scanData.data.validated.birth_place_similar;
        $scope.extractedImgUrl = "/" + $scope.scanData.image_path;
        $scope.excelDataUrl = "/" + $scope.scanData.excel_data_path;

        if (Object.keys($scope.similarBirthCities).length !== 0){
            console.log('Similar birth cities with their associated score : ' + $scope.similarBirthCities)
        }

        $scope.convertDate = function (originalDate) {
            // convert daymonthyear to day/month/year

            var day = originalDate[8] + originalDate[9];
            var month = originalDate[5] + originalDate[6];
            var year = originalDate[0] + originalDate[1] + originalDate[2] + originalDate[3];
            return day + '/' + month + '/' + year;
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

        $scope.correctBirthPlace = function(birthCityExists) {
            //Translate de boolean information into an user-understandable sentence
            if (birthCityExists) {
                return "Le lieu de naissance est correct";
            }
            else{return "Le lieu de naissance semble erroné";}
        }


    });
