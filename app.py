import os
from flask import Flask, render_template, request,redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_number = db.Column(db.String(30), unique=True, nullable=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        course = request.form.get("course")
        department = request.form.get("department")

        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
             return render_template("email_exists.html", email=email)

        new_student = Student(fullname=fullname, email=email, course=course, department=department)
        try:
            db.session.add(new_student)
            db.session.flush()
            
            year = 2026
            new_student.reg_number = f"AE-FUNAI/{department}/{year}/{new_student.id:03d}"
            db.session.commit()
            
            return render_template("success.html", fullname=fullname)          
        except IntegrityError:
            db.session.rollback()
            return render_template("email_exists.html", email=email)

    return render_template('sign_up.html')

@app.route('/students')
def students():
    all_students = Student.query.all()
    return render_template('students.html', students=all_students)

@app.route('/students/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash (f"Student {student.fullname} has been deleted.", "success")
    return redirect(url_for('students'))

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        print(request.form)
        
        student.fullname = request.form.get("fullname")
        student.email = request.form.get("email")
        student.course = request.form.get("course")
        student.department = request.form.get("department")
        db.session.commit()
        flash (f"Student {student.fullname} has been updated.", "success")
        return redirect(url_for('students'))
    return render_template('edit_students.html', student=student)

if __name__ == "__main__":
    app.run(debug=True)