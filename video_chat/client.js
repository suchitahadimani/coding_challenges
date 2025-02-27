//navigator is a builtin js function that can be used to obtain user information:

// Get user's geolocation
navigator.geolocation.getCurrentPosition(
    pos => console.log(pos.coords.latitude, pos.coords.longitude),
    err => console.error("Location error:", err)
);


function hasUserMedia() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

if (hasUserMedia()) {
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })

    //.then is typically used for asynchronous calls and runs when the "promise" is returned either result from request or permission granted for the camera.
        .then(function (stream) {
            var video = document.querySelector('video');
            video.muted = true;  // by default stream does both video and audio, i dont want it to echo so i muted the sound
            if (video) {
                video.srcObject = stream;
            }
        })
    //if permission not granted, .catch runs. the full form is promise.catch and promise.then
        .catch(function (err) {
            console.error("Error accessing media devices:", err);
        });
} 

else {
    alert("WebRTC is not supported in this browser");
}
