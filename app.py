from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store
students = [
    {"name": "Your Name", "grade": 10, "section": "Zechariah"}
]

@app.route('/')
def home():
    return "Welcome to the Enhanced Flask Student API!"

# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# Add a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    grade = data.get('grade')
    section = data.get('section')

    if not name or not grade or not section:
        return jsonify({"error": "Missing required fields"}), 400

    students.append({"name": name, "grade": grade, "section": section})
    return jsonify({"message": "Student added successfully!", "students": students}), 201

# Edit a student by name
@app.route('/students/<string:name>', methods=['PUT'])
def update_student(name):
    data = request.get_json()
    for student in students:
        if student['name'].lower() == name.lower():
            student['grade'] = data.get('grade', student['grade'])
            student['section'] = data.get('section', student['section'])
            return jsonify({"message": "Student updated successfully!", "student": student})
    return jsonify({"error": "Student not found"}), 404

# Delete a student by name
@app.route('/students/<string:name>', methods=['DELETE'])
def delete_student(name):
    for student in students:
        if student['name'].lower() == name.lower():
            students.remove(student)
            return jsonify({"message": f"Student '{name}' deleted successfully!"})
    return jsonify({"error": "Student not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
