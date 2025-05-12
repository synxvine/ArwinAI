let video;
let canvas;

function init() {
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(error => {
            console.error("Webcam access error", error);
            alert("Cannot access webcam");
        });
}

function capture() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.style.display = "block";
    video.style.display = "none";

    const imgData = canvas.toDataURL();

    fetch("/process_face", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_data: imgData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            drawFaceLandmarks(data.face_landmarks, context);
        } else {
            alert("No face detected.");
            window.location.reload();
        }
    });
}

function drawFaceLandmarks(landmarks, context) {
    context.lineWidth = 2;
    context.strokeStyle = "red";
    for (let key in landmarks) {
        landmarks[key].forEach(([x, y]) => {
            context.beginPath();
            context.arc(x, y, 2, 0, 2 * Math.PI);
            context.fillStyle = "red";
            context.fill();
        });
    }
}

function register() {
    const studentId = document.getElementById("studentId").value;
    const lastName = document.getElementById("lastName").value;
    const firstName = document.getElementById("firstName").value;
    const middleName = document.getElementById("middleName").value;
    const photoData = canvas.toDataURL();

    if (!studentId || !lastName || !firstName || !photoData) {
        alert("Please fill required fields and capture photo.");
        return;
    }

    const formData = new FormData();
    formData.append("studentId", studentId);
    formData.append("lastName", lastName);
    formData.append("firstName", firstName);
    formData.append("middleName", middleName);
    formData.append("photo_data", photoData);

    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Registered successfully!");
            window.location.href = "/";
        } else {
            alert("Registration failed");
        }
    });
}

function login() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photoData = canvas.toDataURL();

    const formData = new FormData();
    formData.append("photo_data", photoData);

    fetch("/login", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);  

            canvas.style.display = "none";
            video.style.display = "block";
        } else {
            alert("Login failed. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again.");
    });
}

function logout() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photoData = canvas.toDataURL();

    const formData = new FormData();
    formData.append("photo_data", photoData);

    fetch("/logout", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            canvas.style.display = "none";
            video.style.display = "block";
        } else {
            alert("Logout failed. " + data.message);
        }
    })
    .catch(error => {
        console.error("Error during logout:", error);
        alert("An error occurred. Please try again.");
    });
}


init();
