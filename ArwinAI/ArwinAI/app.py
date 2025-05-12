import os
import datetime
import face_recognition
import base64
import json
import numpy as np
from flask import Flask, jsonify, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="face_recognition"
)
db_cursor = db_connection.cursor()

@app.route("/")
def home():
    return redirect("/scanner")

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    photo_data = request.form.get("photo_data")

    if not name or not photo_data:
        return jsonify({"success": False, "message": "Name and photo data are required"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp.jpg", "wb") as f:
        f.write(img_data)

    image = face_recognition.load_image_file("temp.jpg")
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return jsonify({"success": False, "message": "No face found in the image"})

    face_encoding = face_encodings[0]

    face_encoding_str = json.dumps(face_encoding.tolist())

    insert_query = "INSERT INTO users (name, face_encoding) VALUES (%s, %s)"
    db_cursor.execute(insert_query, (name, face_encoding_str))
    db_connection.commit()

    return jsonify({"success": True, "name": name})

@app.route("/login", methods=["POST"])
def login():
    photo_data = request.form.get("photo_data")

    if not photo_data:
        return jsonify({"success": False, "message": "Photo data is required"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp_login.jpg", "wb") as f:
        f.write(img_data)

    login_image = face_recognition.load_image_file("temp_login.jpg")
    login_face_encodings = face_recognition.face_encodings(login_image)

    if not login_face_encodings:
        return jsonify({"success": False, "message": "No face found in the image"})

    login_face_encoding = login_face_encodings[0]

    select_query = "SELECT name, face_encoding FROM users"
    db_cursor.execute(select_query)
    users = db_cursor.fetchall()

    for user in users:
        name = user[0]
        stored_face_encoding = json.loads(user[1])

        matches = face_recognition.compare_faces([stored_face_encoding], login_face_encoding)

        if matches[0]:
            return jsonify({"success": True, "name": name})

    return jsonify({"success": False, "message": "No match found"})

@app.route("/success")
def success():
    user_name = request.args.get('user_name')
    return render_template("success.html", user_name=user_name)

@app.route("/process_face", methods=["POST"])
def process_face():
    photo_data = request.json.get("photo_data")

    if not photo_data:
        return jsonify({"success": False, "message": "No photo data received"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp_capture.jpg", "wb") as f:
        f.write(img_data)

    image = face_recognition.load_image_file("temp_capture.jpg")
    face_landmarks_list = face_recognition.face_landmarks(image)

    if not face_landmarks_list:
        return jsonify({"success": False, "message": "No face detected"})

    face_landmarks = face_landmarks_list[0]

    return jsonify({"success": True, "face_landmarks": face_landmarks})

if __name__ == "__main__":
    app.run(debug=True)
