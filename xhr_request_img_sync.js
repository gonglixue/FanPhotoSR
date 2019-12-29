window.downloadImageToBase64 = function (url) {
    // Put these constants out of the function to avoid creation of objects.
    var STATE_DONE = 4;
    var HTTP_OK = 200;
    var xhr = new XMLHttpRequest();

    function stateChange() {
        // Wait for valid response
        if (xhr.readyState == STATE_DONE && xhr.status == HTTP_OK) {
            var blob = new Blob([xhr.response], {
                type: xhr.getResponseHeader("Content-Type")
            });
            // Create file reader and convert blob array to Base64 string
            var reader = new window.FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function () {
                var base64data = reader.result;
                console.log(base64data);
            }

        }
    };
   //  xhr.responseType = "arraybuffer";
    // Load async
    xhr.open("GET", url, false); // sync request
    xhr.send(null);

    //console.log(xhr.readyState)
    //console.log(xhr.status)
    // stateChange();
    //console.log(xhr.response)
   if (xhr.status == HTTP_OK && xhr.readyState==STATE_DONE)
   {
       return xhr.response;
   }
   else{
       return "-1";
   }
};