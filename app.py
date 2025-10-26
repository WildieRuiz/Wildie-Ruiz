from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store
students = [
    {"name": "Your Name", "grade": 10, "section": "Zechariah"}
]

@app.route('/')
def home():
    return '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Student Manager</title>
  <style>
    :root{
      --bg: #f5f7fb;
      --card: #ffffff;
      --accent: #003366;
      --accent-2: #0055aa;
      --muted: #6b7280;
      --success: #16a34a;
      --danger: #ef4444;
      --radius: 12px;
      --shadow: 0 6px 18px rgba(2,6,23,0.06);
    }
    *{box-sizing: border-box}
    html,body{height:100%}
    body{
      margin:0;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      background: linear-gradient(180deg, #eef2ff 0%, var(--bg) 100%);
      color: #111827;
      padding:32px;
    }
    .container{max-width:980px;margin:0 auto;}
    header{text-align:center;margin-bottom:20px;}
    header h1{margin:0;font-size:28px;color:var(--accent);}
    header .subtitle{color:var(--muted);margin-top:6px;font-size:14px;}
    .card{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px;margin-bottom:18px;}
    #student-form .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;}
    #student-form input{flex:1 1 180px;padding:10px 12px;border:1px solid #e6e9ef;border-radius:10px;font-size:14px;}
    #student-form button{padding:10px 14px;border-radius:10px;border:0;cursor:pointer;font-weight:600;}
    #submit-btn{background:var(--accent);color:white;}
    #cancel-edit{background:#f3f4f6;color:var(--muted);}
    .students-list{display:grid;gap:10px;margin-top:12px;}
    .student{display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:10px;border:1px solid #f0f2f7;background:linear-gradient(180deg,#ffffff,#fbfdff);}
    .student .meta{display:flex;gap:12px;align-items:center;}
    .avatar{width:44px;height:44px;border-radius:8px;background:linear-gradient(135deg,var(--accent),var(--accent-2));color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;}
    .info .name{font-weight:700;color:#111827;}
    .info .sub{color:var(--muted);font-size:13px;}
    .actions{display:flex;gap:8px;}
    .btn{padding:8px 10px;border-radius:8px;border:0;cursor:pointer;font-size:13px;}
    .btn.edit{background:#f3f4f6;color:var(--accent-2);}
    .btn.delete{background:#fff5f5;color:var(--danger);border:1px solid rgba(239,68,68,0.08);}
    @media (max-width:640px){#student-form .row{flex-direction:column}.actions{gap:6px}}
    .hidden{display:none}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Student Manager</h1>
      <p class="subtitle">Add, edit, or remove students</p>
    </header>

    <section class="card">
      <form id="student-form">
        <div class="row">
          <input type="text" id="name" placeholder="Name" required />
          <input type="number" id="grade" placeholder="Grade" min="1" max="12" required />
          <input type="text" id="section" placeholder="Section" required />
          <button type="submit" id="submit-btn">Add Student</button>
          <button type="button" id="cancel-edit" class="hidden">Cancel Edit</button>
        </div>
      </form>
    </section>

    <section class="card">
      <h2>Students</h2>
      <div id="students-list" class="students-list"></div>
    </section>
  </div>

  <script>
    const studentsList = document.getElementById('students-list');
    const form = document.getElementById('student-form');
    const nameInput = document.getElementById('name');
    const gradeInput = document.getElementById('grade');
    const sectionInput = document.getElementById('section');
    const submitBtn = document.getElementById('submit-btn');
    const cancelEditBtn = document.getElementById('cancel-edit');

    let editingName = null;

    async function fetchStudents() {
      const res = await fetch('/students');
      const data = await res.json();
      renderStudents(data);
    }

    function renderStudents(list) {
      studentsList.innerHTML = '';
      if (!list || list.length === 0) {
        studentsList.innerHTML = '<div class="student"><div class="meta"><div class="info"><div class="name">No students yet.</div></div></div></div>';
        return;
      }
      list.forEach(s => {
        const el = document.createElement('div');
        el.className = 'student';
        el.innerHTML = `
          <div class="meta">
            <div class="avatar">${(s.name || '?').split(' ').map(p => p[0]).slice(0,2).join('').toUpperCase()}</div>
            <div class="info">
              <div class="name">${escapeHtml(s.name)}</div>
              <div class="sub">Grade ${escapeHtml(String(s.grade))} • Section ${escapeHtml(s.section)}</div>
            </div>
          </div>
          <div class="actions">
            <button class="btn edit">Edit</button>
            <button class="btn delete">Delete</button>
          </div>
        `;
        el.querySelector('.edit').addEventListener('click', () => startEdit(s));
        el.querySelector('.delete').addEventListener('click', () => removeStudent(s.name));
        studentsList.appendChild(el);
      });
    }

    function escapeHtml(unsafe) {
      return unsafe.replace(/[&<"'>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
    }

    async function addStudent(student) {
      const res = await fetch('/students', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(student)
      });
      if (res.ok) {
        await fetchStudents();
        form.reset();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to add student');
      }
    }

    async function updateStudent(originalName, student) {
      const res = await fetch('/students/' + encodeURIComponent(originalName), {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(student)
      });
      if (res.ok) {
        await fetchStudents();
        cancelEditingState();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to update student');
      }
    }

    async function removeStudent(name) {
      if (!confirm('Delete ' + name + '?')) return;
      const res = await fetch('/students/' + encodeURIComponent(name), { method: 'DELETE' });
      if (res.ok) await fetchStudents();
      else alert('Failed to delete');
    }

    function startEdit(s) {
      editingName = s.name;
      nameInput.value = s.name;
      gradeInput.value = s.grade;
      sectionInput.value = s.section;
      submitBtn.textContent = 'Save Changes';
      cancelEditBtn.classList.remove('hidden');
    }

    function cancelEditingState() {
      editingName = null;
      form.reset();
      submitBtn.textContent = 'Add Student';
      cancelEditBtn.classList.add('hidden');
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const student = {
        name: nameInput.value.trim(),
        grade: Number(gradeInput.value),
        section: sectionInput.value.trim()
      };
      if (!student.name || !student.section || !student.grade) {
        alert('Please fill all fields');
        return;
      }
      if (editingName) await updateStudent(editingName, student);
      else await addStudent(student);
    });

    cancelEditBtn.addEventListener('click', (e) => {
      e.preventDefault();
      cancelEditingState();
    });

    fetchStudents();
  </script>
</body>
</html>
    '''

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
            new_name = data.get('name')
            if new_name:
                student['name'] = new_name
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
