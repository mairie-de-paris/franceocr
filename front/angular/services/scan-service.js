"use strict";
angular.module('myApp.scanService', [])
/*
 * Provide scan data
 */
    .service('scanService', function($http, $location) {

        var scan_data;

        this.getScanData = function () {
            // get current scan data
            return scan_data;
        };

        this.setScanData = function (data) {
            // set scan data
            scan_data = data;
        };

        this.refuseScanData = function () {
            // refuse scan data in case of an error from the algorithm
            scan_data = null;
        };
    });