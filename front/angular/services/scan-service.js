"use strict";
angular.module('myApp.scanService')
/*
 * Provide scan data
 */
    .service('scanService', function($http, $location) {

        var scan_data = null;

        this.getScanData = function () {
            // get current receipt or one specified by id
            return scan_data;
        };

        this.setScanData = function (data) {
            scan_data = data;
        };

        // Refuse scan data in case of an error from the algorithm
        this.refuseScanData = function () {
            scan_data = null;
            $location.path('/upload');
        };
    });