let video;
let canvas;
let nameInput;

function init() {
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    nameInput = document.getElementById("name");

    // Access the webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(error => {
            console.log("Error accessing the webcam", error);
            alert("Cannot access the webcam");
        });
}

function capture() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.style.display = "block"; 
    video.style.display = "none";   

    // Send the captured image to the server to process face landmarks
    const imgData = canvas.toDataURL();

    fetch("/process_face", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ photo_data: imgData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const faceLandmarks = data.face_landmarks;
            
            if (!faceLandmarks || Object.keys(faceLandmarks).length === 0) {
                // If no face landmarks are detected, show an alert message and refresh the page after closing the alert
                alert("No face detected. Please try again.");
                window.location.reload();  // Refresh the page after the alert
            } else {
                drawFaceLandmarks(faceLandmarks, context); // Draw landmarks as dots
            }
        } else {
            alert("Face processing failed. Please try again.");
            window.location.reload();  // Refresh the page after the alert
        }
    })
    .catch(error => {
        console.log("Error", error);
        alert("An error occurred. Please try again.");
        window.location.reload();  // Refresh the page after the alert
    });
}


function drawFaceLandmarks(landmarks, context) {
    context.lineWidth = 2;
    context.strokeStyle = "red"; // Color for drawing the dots

    drawFeature(landmarks['chin'], context);
    drawFeature(landmarks['left_eyebrow'], context);
    drawFeature(landmarks['right_eyebrow'], context);
    drawFeature(landmarks['left_eye'], context);
    drawFeature(landmarks['right_eye'], context);
    drawFeature(landmarks['nose_bridge'], context);
    drawFeature(landmarks['nose_tip'], context);
    drawFeature(landmarks['top_lip'], context);
    drawFeature(landmarks['bottom_lip'], context);
}

function drawFeature(feature, context) {
    for (let i = 0; i < feature.length; i++) {
        const [x, y] = feature[i];
        // Draw a small circle (dot) at each point
        context.beginPath();
        context.arc(x, y, 2, 0, 2 * Math.PI); // Draw a circle with radius 2
        context.fillStyle = "red";  // Fill the circle with red color
        context.fill(); // Actually draw the circle
    }
}

function register() {
    const name = nameInput.value;
    const photoData = canvas.toDataURL();  // Get the photo data URI

    if (!name || !photoData) {
        alert("Name and photo required");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo_data", photoData);  // Send photo data URI

    fetch("/register", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Data successfully registered");
                window.location.href = "/";  // Redirect to the home page after successful registration
            } else {
                alert("Sorry, registration failed");
            }
        })
        .catch(error => {
            console.log("Error", error);
        });
}

function login() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photoData = canvas.toDataURL();  // Get the photo data URI

    if (!photoData) {
        alert("Photo required, please");
        return;
    }

    const formData = new FormData();
    formData.append("photo_data", photoData);  // Send photo data URI

    fetch("/login", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Login successful!");
                window.location.href = "/success?user_name=" + data.name;  // Redirect to success page with the recognized name
            } else {
                alert("Login failed, please try again");
            }
        })
        .catch(error => {
            console.log("Error", error);
        });
}

init();   // Initialize the webcam access and setup
