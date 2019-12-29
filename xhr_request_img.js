window.downloadImageToBase64 = function (url) {
    // Put these constants out of the function to avoid creation of objects.
    var STATE_DONE = 4;
    var HTTP_OK = 200;
    var xhr = new XMLHttpRequest();
    var flag = -1;
    var base64data = "-1"
    xhr.onreadystatechange = function () {
        // Wait for valid response
        if (xhr.readyState == STATE_DONE && xhr.status == HTTP_OK) {
            var blob = new Blob([xhr.response], {
                type: xhr.getResponseHeader("Content-Type")
            });
            // Create file reader and convert blob array to Base64 string
            var reader = new window.FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function () {
                base64data = reader.result;
                // console.log(base64data);
                flag = 1;
            }

        }
    };
    xhr.responseType = "arraybuffer";
    // Load async
    xhr.open("GET", url, true);
    xhr.send();
    while(flag != -1){
        return base64data;
    }
    return "-1";
};