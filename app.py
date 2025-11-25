from flask import Flask, render_template, redirect, url_for, request, session, flash
from mysql.connector import connect
# from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Database connection
db = connect(
    host="localhost",
    port=3306,
    user="root",
    password="TalitaEva2005",
    database="flask_db"
)

# get cursor
cursor = db.cursor(dictionary=True)

        # cursor.execute('SELECT * FROM users')
        # users = cursor.fetchall()
        # print(users)


app.secret_key = 'your_secret_key'


#---------- ROUTES ----------

@app.route('/')
def home():
    # Use .get() method to avoid KeyError
    user_email = session.get('email')
    
    if not user_email:  # If email doesn't exist in session
        return redirect(url_for('login'))
    
    return render_template('home.html', email=user_email)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        nshe = request.form['nshe']

        cursor.execute("INSERT INTO users (email, nshe) VALUES (%s, %s)", (email, nshe))
        db.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        nshe = request.form['nshe']

        cursor.execute("SELECT * FROM users WHERE email = %s AND nshe = %s", (email, nshe))
        user = cursor.fetchone()

        if user:
            session['email'] = user['email']
            session['nshe'] = user['nshe']
            flash("Login successful!", "success")  # Success flash message
            return redirect(url_for('home'))
        else:
            flash("Invalid email or NSHE number.", "error")  # Error flash message

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('home'))


@app.route('/exam_menu')
def exam_menu():
    print("Rendering exam_menu.html")
    return render_template('exam_menu.html')


@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')


@app.route('/history')
def history():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('history.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     return render_template('login.html')

if __name__ == '__main__':
     app.run(host = '0.0.0.0', port = 5001, debug=True)
     print("Server is running on http://localhost:5001") 
















# from flask import Flask, render_template, request, session, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# # -----------------------------------
# # FLASK SETUP
# # -----------------------------------
# app = Flask(__name__)
# app.secret_key = "SECRET_KEY_CHANGE_ME"

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam_system.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)


# # -----------------------------------
# # DATABASE MODELS
# # -----------------------------------

# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True)
#     nshe = db.Column(db.String(20))  # password
#     role = db.Column(db.String(10), default="student")  # future faculty support


# class Exam(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))


# class ExamSession(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
#     date = db.Column(db.String(50))
#     time = db.Column(db.String(50))
#     capacity = db.Column(db.Integer, default=20)

#     exam = db.relationship("Exam")


# class Reservation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
#     session_id = db.Column(db.Integer, db.ForeignKey('exam_session.id'))

#     exam = db.relationship("Exam")
#     session = db.relationship("ExamSession")


# # -----------------------------------
# # HELPER FUNCTIONS
# # -----------------------------------

# def authenticate(email, password):
#     """Return student if email+NSHE matches."""
#     user = Student.query.filter_by(email=email, nshe=password).first()
#     return user


# def get_exam_data():
#     """Return list of exams and available sessions."""
#     exams = Exam.query.all()
#     sessions = ExamSession.query.all()

#     # Filter out full sessions
#     session_status = {}
#     for s in sessions:
#         count = Reservation.query.filter_by(session_id=s.id).count()
#         if count < s.capacity:
#             session_status[s.id] = count
#         else:
#             session_status[s.id] = "full"

#     return exams, sessions, session_status


# def register_student(student_id, exam_id, session_id):
#     """Check rules and register student."""
    
#     # 1. Prevent duplicate for same exam
#     existing = Reservation.query.filter_by(student_id=student_id, exam_id=exam_id).first()
#     if existing:
#         return False, "You already booked this exam."

#     # 2. Max 3 different exams
#     total = Reservation.query.filter_by(student_id=student_id).count()
#     if total >= 3:
#         return False, "You have already registered for 3 exams."

#     # 3. Check capacity
#     count = Reservation.query.filter_by(session_id=session_id).count()
#     session_obj = ExamSession.query.get(session_id)

#     if count >= session_obj.capacity:
#         return False, "This session is already full."

#     # 4. Register
#     reservation = Reservation(
#         student_id=student_id,
#         exam_id=exam_id,
#         session_id=session_id
#     )

#     db.session.add(reservation)
#     db.session.commit()

#     return True, "Registration successful."


# def get_reservations_by_student(student_id):
#     return Reservation.query.filter_by(student_id=student_id).all()


# def cancel_reservation_db(reservation_id, student_id):
#     r = Reservation.query.filter_by(id=reservation_id, student_id=student_id).first()
#     if r:
#         db.session.delete(r)
#         db.session.commit()


# # -----------------------------------
# # ROUTES
# # -----------------------------------

# # HOME = LOGIN
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == "POST":
#         email = request.form['email']
#         password = request.form['password']

#         user = authenticate(email, password)

#         if user:
#             session['user_id'] = user.id
#             session['email'] = user.email
#             return redirect("/dashboard")

#         return render_template("login.html", error="Invalid email or NSHE number.")

#     return render_template("login.html")


# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect('/')
#     return render_template("dashboard.html", email=session['email'])


# @app.route('/register', methods=['GET', 'POST'])
# def register_exam():
#     if 'user_id' not in session:
#         return redirect('/')

#     exams, sessions, session_status = get_exam_data()

#     if request.method == "POST":
#         exam_id = request.form['exam_id']
#         session_id = request.form['session_id']

#         success, message = register_student(session['user_id'], exam_id, session_id)

#         if success:
#             return redirect('/confirmation')

#         return render_template(
#             "register.html",
#             error=message,
#             exams=exams,
#             sessions=sessions,
#             session_status=session_status
#         )

#     return render_template(
#         "register.html",
#         exams=exams,
#         sessions=sessions,
#         session_status=session_status
#     )


# @app.route('/confirmation')
# def confirmation():
#     if 'user_id' not in session:
#         return redirect('/')
#     return render_template("confirmation.html")


# @app.route('/history')
# def reservation_history():
#     if 'user_id' not in session:
#         return redirect('/')
    
#     reservations = get_reservations_by_student(session['user_id'])

#     return render_template("history.html", reservations=reservations)


# @app.route('/cancel/<int:reservation_id>')
# def cancel_reservation(reservation_id):
#     if 'user_id' not in session:
#         return redirect('/')
    
#     cancel_reservation_db(reservation_id, session['user_id'])
#     return redirect('/history')


# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/')


# # -----------------------------------
# # INITIALIZE DB
# # -----------------------------------
# @app.cli.command("initdb")
# def initdb():
#     """Run: flask initdb"""
#     db.drop_all()
#     db.create_all()

#     # Sample exams
#     math = Exam(name="Math Placement Exam")
#     english = Exam(name="English Placement Exam")
#     rtc = Exam(name="Reading Skills Exam")

#     db.session.add_all([math, english, rtc])
#     db.session.commit()

#     # Sample sessions
#     sessions = [
#         ExamSession(exam_id=1, date="2025-12-05", time="9:00 AM"),
#         ExamSession(exam_id=1, date="2025-12-05", time="1:00 PM"),
#         ExamSession(exam_id=2, date="2025-12-06", time="10:00 AM"),
#         ExamSession(exam_id=3, date="2025-12-07", time="2:00 PM"),
#     ]

#     db.session.add_all(sessions)
#     db.session.commit()

#     # Example student
#     demo = Student(
#         email="12345678@student.csn.edu",
#         nshe="12345678"
#     )
#     db.session.add(demo)
#     db.session.commit()

#     print("Database initialized.")


# # -----------------------------------
# # RUN
# # -----------------------------------
# if __name__ == "__main__":
#     app.run(debug=True)
#     print("Server is running on http://localhost:5001")



