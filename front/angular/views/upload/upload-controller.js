"@ strict";

angular.module('myApp.upload', ['angularFileUpload', 'myApp.scanService'])
    .controller('UploadController', function($scope, $upload, $location, $timeout, $window, scanService) {

        // initializing scan data to "null" and error to false
        scanService.refuseScanData();
        $scope.error = false;

        $scope.onFileSelect = function($files) {
            console.log("selecting files");
            $scope.loading = true;
            $scope.error = false;
            $timeout(function() {
                // Fadein loading text nicely
                $scope.loadingText = true;
            }, 400);
            //$files: an array of files selected, each file has name, size, and type.
            for (var i = 0; i < $files.length; i++) {
                var file = $files[i];
                $scope.upload = $upload.upload({
                    url: '/cni/scan',
                    fileFormDataName: 'image',
                    method: 'POST',
                    file: file
                })
                    .progress(function(evt) {
                        console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
                        $scope.uploadPercent =  parseInt(100.0 * evt.loaded / evt.total);
                    }).success(function(data, status, headers, config) {
                        // file is uploaded successfully
                        console.log("Upload success, redirecting, response data:");
                        console.log(data);
                        scanService.setScanData(data);
                        $scope.loading = false;
                        //$window.location.href = "#/results";
                        $window.location.assign("#/results");

                    }).error(function(er) {
                        // file is not uploaded or scanned successfully
                        console.log("Upload error, let's try scanning again");
                        console.log(er);
                        $timeout(function() {
                            // Fadein error text nicely
                            $scope.error = true;
                        }, 200);
                        $scope.errorMessage = er.message;
                        scanService.refuseScanData();
                        $scope.loading = false;
                        //$window.location.href = "#/upload";
                        $window.location.assign("#/upload");
                    });
                //.then(success, error, progress);
                // access or attach event listeners to the underlying XMLHttpRequest.
                //.xhr(function(xhr){xhr.upload.addEventListener(...)})
            }
            /* alternative way of uploading, send the file binary with the file's content-type.
             Could be used to upload files to CouchDB, imgur, etc... html5 FileReader is needed.
             It could also be used to monitor the progress of a normal http post/put request with large data*/
            // $scope.upload = $upload.http({...})  see 88#issuecomment-31366487 for sample code.
        };
        /*
         * Change drop-box area css class when dragging file
         */
        $scope.dragOverClass = function($event) {
            var items = $event.dataTransfer.items;
            var hasFile = false;
            if (items != null) {
                for (var i = 0 ; i < items.length; i++) {
                    if (items[i].kind == 'file') {
                        hasFile = true;
                        break;
                    }
                }
            } else {
                hasFile = true;
            }
            return hasFile ? "upload-drop-box-dragover" : "upload-drop-box-dragover-err";
        };
    });
