"use strict";
angular.module('myApp.results', ['myApp.scanService'])
    .controller('ResultsController', function($scope, $sce, $http, scanService) {

        //putting data from scanService in $scope variables
        $scope.scanData = scanService.getScanData();
        $scope.lastName = $scope.scanData.data.last_name_ocr;
        $scope.firstName = $scope.scanData.data.first_name_ocr;
        $scope.birthDate = $scope.scanData.data.birth_date_ocr;
        $scope.birthPlace = $scope.scanData.data.birth_place_ocr;
        $scope.birthCityExists = $scope.scanData.data.birth_city_exists;
        $scope.convertedBirthPlace = $scope.scanData.data.converted_birth_place;
        $scope.extractedImgUrl = "http://localhost:5000/" + $scope.scanData.image_path;
        $scope.excelDataUrl = "http://localhost:5000" + $scope.scanData.excel_data_path;


        $scope.convertDate = function (originalDate) {
            // convert daymonthyear to day/month/year
            var day = originalDate[0]+originalDate[1];
            var month = originalDate[2]+originalDate[3];
            var year = originalDate[4]+originalDate[5]+originalDate[6]+originalDate[7];
            return day+'/'+month+'/'+year;
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
