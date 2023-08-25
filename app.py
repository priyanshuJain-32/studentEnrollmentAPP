import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
db = SQLAlchemy(app)

class Student(db.Model):
	__tablename__ = 'student'
	student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	roll_number = db.Column(db.String, unique = True, nullable = False)
	first_name = db.Column(db.String, nullable = False)
	last_name = db.Column(db.String)
	
class Course(db.Model):
	__tablename__ = 'course'
	course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	course_code = db.Column(db.String, unique = True, nullable = False)
	course_name = db.Column(db.String, nullable = False)
	course_description = db.Column(db.String)

class Enrollments(db.Model):
	__tablename__ = 'enrollments'
	enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), primary_key = True, nullable = False)
	ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), primary_key = True, nullable = False)

# Part 1 The home page
@app.route('/', methods=["GET"])	
def index():
	data = Student.query.all()
	return render_template("index.html", data=data) #Tested Ok

# Part 2 when we click on Add Student
@app.route("/student/create", methods=["GET","POST"])
def create_form():
	if request.method =='GET':
		return render_template("create-form.html")
	else:
		while True:
			try:
	# Adding the student data into student database
				_student = Student(student_id = None, roll_number=int(request.form["roll"]), first_name = request.form["f_name"], last_name=request.form["l_name"])
				db.session.add(_student)
				db.session.commit()
				break
	# Adding the student id and course id into the database	
			except: # Exception was handled with some mumbo jumbo
				return render_template("id_exists.html")
		D = {"course_1":1,"course_2":2,"course_3":3,"course_4":4}
		for course in request.form.getlist("courses"):
			_enrollments = Enrollments(enrollment_id=None, estudent_id = _student.student_id, ecourse_id = D[course])
			db.session.add(_enrollments)
		db.session.commit()
		return redirect("/") #Tested Ok


# Part 3 when we click on Update button
@app.route("/student/<int:student_id>/update", methods=["GET","POST"])
def update_details(student_id):
	_student = Student.query.filter_by(student_id=student_id).first()
	if request.method == 'GET':
		return render_template("update-form.html", Data=_student)
	else:
		_student.first_name = request.form["f_name"]
		_student.last_name = request.form["l_name"]
		db.session.add(_student)
		db.session.commit()
		_clear = Enrollments.query.filter_by(estudent_id=student_id).all()
		for i in _clear:
			db.session.delete(i)
			db.session.commit()
		D = {"course_1":1,"course_2":2,"course_3":3,"course_4":4}
		for course in request.form.getlist("courses"):
			_enrollments = Enrollments(enrollment_id=None, estudent_id = student_id, ecourse_id = D[course])
			db.session.add(_enrollments)
		db.session.commit()
		return redirect("/") #Tested Ok


# Part 4 When we click on delete button from the homepage
@app.route("/student/<int:student_id>/delete", methods=["GET"])
def delete_details(student_id):
	_student = Student.query.get(student_id)
	db.session.delete(_student)
	db.session.commit()
	
	_clear = Enrollments.query.filter_by(estudent_id=student_id).all()
	for i in _clear:
			db.session.delete(i)
			db.session.commit()
	return redirect("/") #Tested Ok
	


# Part 5 When we click on roll number to open the details of students
@app.route("/student/<int:student_id>", methods=["GET"])
def display_details(student_id):
	_student = Student.query.get(student_id)
	_enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
	data2 = []
	for i in range(len(_enrollments)):
		data = Course.query.get(_enrollments[i].ecourse_id)
		data2.append(data)
	return render_template("personal_details.html", data1=_student, data2=data2)
	
if __name__=='__main__':
	app.run()
