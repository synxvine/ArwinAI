import os
import base64
import json
import face_recognition
from flask import Flask, jsonify, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# DB Connection
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
    return render_template("scannerIn.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    student_id = request.form.get("studentId")
    last_name = request.form.get("lastName")
    first_name = request.form.get("firstName")
    middle_name = request.form.get("middleName") or ""
    photo_data = request.form.get("photo_data")

    if not student_id or not last_name or not first_name or not photo_data:
        return jsonify({"success": False, "message": "Required fields missing"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp.jpg", "wb") as f:
        f.write(img_data)

    image = face_recognition.load_image_file("temp.jpg")
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return jsonify({"success": False, "message": "No face found"})

    face_encoding_str = json.dumps(face_encodings[0].tolist())

    insert_query = """
        INSERT INTO student (studentId, lastName, firstName, middleName, face_encoding)
        VALUES (%s, %s, %s, %s, %s)
    """
    db_cursor.execute(insert_query, (student_id, last_name, first_name, middle_name, face_encoding_str))
    db_connection.commit()

    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    photo_data = request.form.get("photo_data")
    if not photo_data:
        return jsonify({"success": False, "message": "Photo data missing"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp_login.jpg", "wb") as f:
        f.write(img_data)

    login_image = face_recognition.load_image_file("temp_login.jpg")
    login_face_encodings = face_recognition.face_encodings(login_image)

    if not login_face_encodings:
        return jsonify({"success": False, "message": "No face detected"})

    login_encoding = login_face_encodings[0]

    db_cursor.execute("SELECT studentId, firstName, middleName, lastName, face_encoding FROM student")
    students = db_cursor.fetchall()

    for student in students:
        student_id, first_name, middle_name, last_name, encoding_json = student
        stored_encoding = json.loads(encoding_json)
        match = face_recognition.compare_faces([stored_encoding], login_encoding)[0]

        if match:
            insert_attendance_query = """
                INSERT INTO attendance (studentId, lastName, firstName, middleName)
                VALUES (%s, %s, %s, %s)
            """
            db_cursor.execute(insert_attendance_query, (student_id, last_name, first_name, middle_name))
            db_connection.commit()

            return jsonify({
                "success": True, 
                "message": "Time-in successful!",
                "studentId": student_id, 
                "name": f"{first_name} {middle_name or ''} {last_name}".strip()
            })

    return jsonify({"success": False, "message": "No match"})

    from datetime import datetime, date

@app.route("/logout", methods=["POST"])
def logout():
    photo_data = request.form.get("photo_data")
    if not photo_data:
        return jsonify({"success": False, "message": "Photo data missing"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp_logout.jpg", "wb") as f:
        f.write(img_data)

    logout_image = face_recognition.load_image_file("temp_logout.jpg")
    logout_face_encodings = face_recognition.face_encodings(logout_image)

    if not logout_face_encodings:
        return jsonify({"success": False, "message": "No face detected"})

    logout_encoding = logout_face_encodings[0]

    db_cursor.execute("SELECT studentId, firstName, middleName, lastName, face_encoding FROM student")
    students = db_cursor.fetchall()

    for student in students:
        student_id, first_name, middle_name, last_name, encoding_json = student
        stored_encoding = json.loads(encoding_json)
        match = face_recognition.compare_faces([stored_encoding], logout_encoding)[0]

        if match:
            today = date.today()
            time_now = datetime.now().strftime('%H:%M:%S')

            # Check if student already has a time-in today
            db_cursor.execute("""
                SELECT id FROM attendance 
                WHERE studentId = %s AND DATE(timestamp) = %s
            """, (student_id, today))
            attendance = db_cursor.fetchone()

            if attendance:
                # Update time_out
                db_cursor.execute("""
                    UPDATE attendance
                    SET time_out = %s
                    WHERE id = %s
                """, (time_now, attendance[0]))
            else:
                # Insert new record with time_out only
                db_cursor.execute("""
                    INSERT INTO attendance (studentId, lastName, firstName, middleName, time_in, time_out, timestamp)
                    VALUES (%s, %s, %s, %s, NULL, %s, NOW())
                """, (student_id, last_name, first_name, middle_name, time_now))

            db_connection.commit()

            return jsonify({
                "success": True,
                "message": "Time-out successful!",
                "studentId": student_id,
                "name": f"{first_name} {middle_name or ''} {last_name}".strip()
            })

    return jsonify({"success": False, "message": "No match found in database."})


@app.route("/process_face", methods=["POST"])
def process_face():
    photo_data = request.json.get("photo_data")

    if not photo_data:
        return jsonify({"success": False, "message": "Missing photo data"})

    img_data = base64.b64decode(photo_data.split(",")[1])
    with open("temp.jpg", "wb") as f:
        f.write(img_data)

    image = face_recognition.load_image_file("temp.jpg")
    landmarks = face_recognition.face_landmarks(image)

    if landmarks:
        return jsonify({"success": True, "face_landmarks": landmarks[0]})
    return jsonify({"success": False, "message": "No face landmarks found"})

@app.route("/success")
def success():
    user_name = request.args.get("user_name")
    return render_template("success.html", user_name=user_name)

if __name__ == "__main__":
    app.run(debug=True)
