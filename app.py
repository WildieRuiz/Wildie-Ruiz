from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory student data
students = [
    {"id": 1, "name": "Juan Dela Cruz", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Maria Santos", "grade": 9, "section": "Gabriel"},
    {"id": 3, "name": "Jose Rizal", "grade": 11, "section": "Michael"}
]

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Flask Student API!",
        "endpoints": {
            "GET /student": "Get all students",
            "GET /student/<id>": "Get a single student by ID",
            "POST /student": "Add a new student",
            "PUT /student/<id>": "Update a student's information",
            "DELETE /student/<id>": "Delete a student"
        }
    })

# GET all students
@app.route('/student', methods=['GET'])
def get_students():
    return jsonify({
        "status": "success",
        "total": len(students),
        "data": students
    })

# GET student by ID
@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"status": "error", "message": "Student not found"}), 404
    return jsonify({"status": "success", "data": student})

# POST: Add new student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "grade", "section")):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    new_id = max((s["id"] for s in students), default=0) + 1
    new_student = {
        "id": new_id,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"]
    }
    students.append(new_student)
    return jsonify({
        "status": "success",
        "message": "Student added successfully",
        "data": new_student
    }), 201

# PUT: Update student
@app.route('/student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"status": "error", "message": "Student not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    student["name"] = data.get("name", student["name"])
    student["grade"] = data.get("grade", student["grade"])
    student["section"] = data.get("section", student["section"])

    return jsonify({
        "status": "success",
        "message": "Student updated successfully",
        "data": student
    })

# DELETE: Remove student
@app.route('/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    global students
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"status": "error", "message": "Student not found"}), 404

    students = [s for s in students if s["id"] != student_id]
    return jsonify({
        "status": "success",
        "message": f"Student with ID {student_id} deleted successfully"
    })

# Error handler for invalid routes
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Route not found"
    }), 404


if __name__ == '__main__':
    app.run(debug=True)
