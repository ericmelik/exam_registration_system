from flask import Flask, render_template, redirect, url_for, request, session, flash
from mysql.connector import connect
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db():
    return connect(
        host="localhost",
        port=3306,
        user="root",
        password="rootroot",
        database="flask_db_2"
    )

#---------- HELPER FUNCTIONS ----------

def get_student_reservation_count(student_id):
    """Get count of different exams student is registered for"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT exam_id) 
        FROM ExamRegistration 
        WHERE student_id = %s
    """, (student_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return count

def check_duplicate_registration(student_id, exam_id):
    """Check if student already registered for this exam"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT registration_id 
        FROM ExamRegistration 
        WHERE student_id = %s AND exam_id = %s
    """, (student_id, exam_id))
    exists = cursor.fetchone() is not None
    cursor.close()
    db.close()
    return exists

def update_seats_filled(exam_id):
    """Update seats_filled count for an exam"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE Exam 
        SET seats_filled = (
            SELECT COUNT(*) 
            FROM ExamRegistration 
            WHERE exam_id = %s
        )
        WHERE exam_id = %s
    """, (exam_id, exam_id))
    db.commit()
    cursor.close()
    db.close()

#---------- ROUTES ----------

@app.route('/')
def home():
    if 'student_id' in session:
        return render_template('home.html', 
                             email=session.get('email'),
                             first_name=session.get('first_name'),
                             role='student')
    elif 'faculty_id' in session:
        return render_template('home.html',
                             email=session.get('email'),
                             first_name=session.get('first_name'),
                             role='faculty')
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Account creation - detects student vs faculty by email"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Student registration
            if '@student.csn.edu' in email:
                student_id = request.form.get('student_id')
                
                if not student_id:
                    flash("NSHE number is required for student registration.", "error")
                    return render_template('register.html')
                
                cursor.execute("""
                    INSERT INTO Student (student_id, email, password, first_name, last_name) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, email, password, first_name, last_name))
                db.commit()
                flash("Student registration successful! Please log in.", "success")
            
            # Faculty registration
            elif '@csn.edu' in email:
                cursor.execute("""
                    INSERT INTO Faculty (email, password, first_name, last_name) 
                    VALUES (%s, %s, %s, %s)
                """, (email, password, first_name, last_name))
                db.commit()
                flash("Faculty registration successful! Please log in.", "success")
            
            else:
                flash("Email must be a valid CSN email address.", "error")
                return render_template('register.html')
            
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "error")
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Universal login for both students and faculty"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Try student login first
        if '@student.csn.edu' in email:
            cursor.execute("""
                SELECT * FROM Student 
                WHERE email = %s AND password = %s
            """, (email, password))
            user = cursor.fetchone()
            
            if user:
                session['student_id'] = user['student_id']
                session['email'] = user['email']
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                session['role'] = 'student'
                flash("Login successful!", "success")
                cursor.close()
                db.close()
                return redirect(url_for('home'))
        
        # Try faculty login
        else:
            cursor.execute("""
                SELECT * FROM Faculty 
                WHERE email = %s AND password = %s
            """, (email, password))
            user = cursor.fetchone()
            
            if user:
                session['faculty_id'] = user['faculty_id']
                session['email'] = user['email']
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                session['role'] = 'faculty'
                flash("Faculty login successful!", "success")
                cursor.close()
                db.close()
                return redirect(url_for('faculty_dashboard'))
        
        cursor.close()
        db.close()
        flash("Invalid email or password.", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

#---------- STUDENT ROUTES ----------

@app.route('/exam_menu')
def exam_menu():
    """Display available exams for registration"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get exams with available seats (not full)
    cursor.execute("""
        SELECT 
            e.exam_id,
            e.exam_name,
            e.exam_date,
            e.exam_time,
            e.capacity,
            e.seats_filled,
            (e.capacity - e.seats_filled) as available_seats,
            l.room_number,
            l.building_number,
            l.campus_name,
            CONCAT(f.first_name, ' ', f.last_name) as faculty_name
        FROM Exam e
        JOIN Location l ON e.location_id = l.location_id
        JOIN Faculty f ON e.faculty_id = f.faculty_id
        WHERE e.seats_filled < e.capacity
        AND e.exam_date >= CURDATE()
        ORDER BY e.exam_date, e.exam_time
    """)
    
    available_exams = cursor.fetchall()
    
    # Get student's current registrations
    cursor.execute("""
        SELECT exam_id 
        FROM ExamRegistration 
        WHERE student_id = %s
    """, (session['student_id'],))
    
    registered_exam_ids = [row['exam_id'] for row in cursor.fetchall()]
    
    cursor.close()
    db.close()
    
    # Check if student has reached max registrations
    registration_count = get_student_reservation_count(session['student_id'])
    at_max = registration_count >= 3
    
    return render_template('exam_menu.html', 
                         exams=available_exams,
                         registered_exam_ids=registered_exam_ids,
                         at_max=at_max,
                         registration_count=registration_count)

@app.route('/register_exam/<int:exam_id>', methods=['POST'])
def register_exam(exam_id):
    """Register student for an exam"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    # Check if student already has 3 registrations
    if get_student_reservation_count(student_id) >= 3:
        flash("You have already registered for 3 exams. Cancel one to register for another.", "error")
        return redirect(url_for('exam_menu'))
    
    # Check for duplicate registration
    if check_duplicate_registration(student_id, exam_id):
        flash("You are already registered for this exam.", "error")
        return redirect(url_for('exam_menu'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Check if exam is full
    cursor.execute("""
        SELECT capacity, seats_filled 
        FROM Exam 
        WHERE exam_id = %s
    """, (exam_id,))
    
    exam = cursor.fetchone()
    
    if exam and exam['seats_filled'] >= exam['capacity']:
        flash("This exam session is full.", "error")
        cursor.close()
        db.close()
        return redirect(url_for('exam_menu'))
    
    # Register student
    try:
        cursor.execute("""
            INSERT INTO ExamRegistration (student_id, exam_id, registration_date) 
            VALUES (%s, %s, %s)
        """, (student_id, exam_id, datetime.now()))
        db.commit()
        
        # Update seats_filled
        update_seats_filled(exam_id)
        
        flash("Successfully registered for exam!", "success")
        cursor.close()
        db.close()
        return redirect(url_for('confirmation'))
    
    except Exception as e:
        flash(f"Registration failed: {str(e)}", "error")
        cursor.close()
        db.close()
        return redirect(url_for('exam_menu'))

@app.route('/confirmation')
def confirmation():
    """Show registration confirmation"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    return render_template('confirmation.html')

@app.route('/history')
def history():
    """Show student's reservation history"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            er.registration_id,
            er.registration_date,
            e.exam_id,
            e.exam_name,
            e.exam_date,
            e.exam_time,
            l.room_number,
            l.building_number,
            l.campus_name,
            CONCAT(f.first_name, ' ', f.last_name) as faculty_name
        FROM ExamRegistration er
        JOIN Exam e ON er.exam_id = e.exam_id
        JOIN Location l ON e.location_id = l.location_id
        JOIN Faculty f ON e.faculty_id = f.faculty_id
        WHERE er.student_id = %s
        ORDER BY e.exam_date DESC, e.exam_time DESC
    """, (session['student_id'],))
    
    reservations = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('history.html', reservations=reservations)

@app.route('/cancel_registration/<int:registration_id>', methods=['POST'])
def cancel_registration(registration_id):
    """Cancel a registration"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get exam_id before deleting
    cursor.execute("""
        SELECT exam_id 
        FROM ExamRegistration 
        WHERE registration_id = %s AND student_id = %s
    """, (registration_id, session['student_id']))
    
    result = cursor.fetchone()
    
    if result:
        exam_id = result['exam_id']
        
        # Delete registration
        cursor.execute("""
            DELETE FROM ExamRegistration 
            WHERE registration_id = %s AND student_id = %s
        """, (registration_id, session['student_id']))
        
        db.commit()
        
        # Update seats_filled
        update_seats_filled(exam_id)
        
        flash("Registration cancelled successfully.", "success")
    else:
        flash("Registration not found.", "error")
    
    cursor.close()
    db.close()
    return redirect(url_for('history'))

#---------- ADMIN ROUTES ----------

@app.route('/admin/locations', methods=['GET', 'POST'])
def manage_locations():
    """Admin page to manage exam locations"""
    if 'faculty_id' not in session:
        flash("Please login as faculty to access this page.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            room_number = request.form['room_number']
            building_number = request.form['building_number']
            campus_name = request.form['campus_name']
            
            db = get_db()
            cursor = db.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO Location (room_number, building_number, campus_name)
                    VALUES (%s, %s, %s)
                """, (room_number, building_number, campus_name))
                db.commit()
                flash(f"Location added: Room {room_number}, Building {building_number}", "success")
            except Exception as e:
                flash(f"Failed to add location: {str(e)}", "error")
            finally:
                cursor.close()
                db.close()
        
        elif action == 'delete':
            location_id = request.form['location_id']
            
            db = get_db()
            cursor = db.cursor()
            
            try:
                # Check if location is being used by any exam
                cursor.execute("SELECT COUNT(*) FROM Exam WHERE location_id = %s", (location_id,))
                exam_count = cursor.fetchone()[0]
                
                if exam_count > 0:
                    flash(f"Cannot delete location - it's being used by {exam_count} exam(s).", "error")
                else:
                    cursor.execute("DELETE FROM Location WHERE location_id = %s", (location_id,))
                    db.commit()
                    flash("Location deleted successfully.", "success")
            except Exception as e:
                flash(f"Failed to delete location: {str(e)}", "error")
            finally:
                cursor.close()
                db.close()
    
    # Get all locations
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT l.*, 
               COUNT(e.exam_id) as exam_count
        FROM Location l
        LEFT JOIN Exam e ON l.location_id = e.location_id
        GROUP BY l.location_id
        ORDER BY l.campus_name, l.building_number, l.room_number
    """)
    
    locations = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('manage_locations.html', locations=locations)

#---------- FACULTY ROUTES ----------

@app.route('/create_exam', methods=['GET', 'POST'])
def create_exam():
    """Faculty can create new exam sessions"""
    if 'faculty_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        location_id = request.form['location_id']
        exam_date = request.form['exam_date']
        exam_time = request.form['exam_time']
        capacity = request.form.get('capacity', 20)
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Exam (exam_name, faculty_id, location_id, exam_date, exam_time, capacity, seats_filled)
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            """, (exam_name, session['faculty_id'], location_id, exam_date, exam_time, capacity))
            db.commit()
            flash("Exam session created successfully!", "success")
            return redirect(url_for('faculty_dashboard'))
        except Exception as e:
            flash(f"Failed to create exam: {str(e)}", "error")
        finally:
            cursor.close()
            db.close()
    
    # GET request - show form with available locations
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Location ORDER BY campus_name, building_number, room_number")
    locations = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('create_exam.html', locations=locations)

@app.route('/faculty_dashboard')
def faculty_dashboard():
    """Faculty dashboard"""
    if 'faculty_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get exams created by this faculty
    cursor.execute("""
        SELECT 
            e.exam_id,
            e.exam_name,
            e.exam_date,
            e.exam_time,
            e.capacity,
            e.seats_filled,
            l.room_number,
            l.building_number,
            l.campus_name
        FROM Exam e
        JOIN Location l ON e.location_id = l.location_id
        WHERE e.faculty_id = %s
        ORDER BY e.exam_date DESC, e.exam_time DESC
    """, (session['faculty_id'],))
    
    exams = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('faculty_dashboard.html', exams=exams)

@app.route('/view_registrations/<int:exam_id>')
def view_registrations(exam_id):
    """View all registrations for an exam (faculty only)"""
    if 'faculty_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get exam details
    cursor.execute("""
        SELECT e.exam_name, e.exam_date, e.exam_time, e.capacity, e.seats_filled
        FROM Exam e
        WHERE e.exam_id = %s AND e.faculty_id = %s
    """, (exam_id, session['faculty_id']))
    
    exam = cursor.fetchone()
    
    if not exam:
        flash("Exam not found or access denied.", "error")
        cursor.close()
        db.close()
        return redirect(url_for('faculty_dashboard'))
    
    # Get registrations
    cursor.execute("""
        SELECT 
            s.student_id,
            s.first_name,
            s.last_name,
            s.email,
            er.registration_date
        FROM ExamRegistration er
        JOIN Student s ON er.student_id = s.student_id
        WHERE er.exam_id = %s
        ORDER BY er.registration_date
    """, (exam_id,))
    
    registrations = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('view_registrations.html', 
                         exam=exam, 
                         exam_id=exam_id,
                         registrations=registrations)

@app.route('/delete_exam/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    """Delete an exam (faculty only, with restrictions)"""
    if 'faculty_id' not in session:
        flash("Please login as faculty to delete exams.", "error")
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Verify faculty owns this exam
        cursor.execute("""
            SELECT exam_name, seats_filled 
            FROM Exam 
            WHERE exam_id = %s AND faculty_id = %s
        """, (exam_id, session['faculty_id']))
        
        exam = cursor.fetchone()
        
        if not exam:
            flash("Exam not found or you don't have permission to delete it.", "error")
            return redirect(url_for('faculty_dashboard'))
        
        # Check if exam has registrations
        if exam['seats_filled'] > 0:
            flash(f"Cannot delete exam with {exam['seats_filled']} registered student(s). Please contact students to cancel their registrations first.", "error")
            return redirect(url_for('faculty_dashboard'))
        
        # Delete the exam (registrations will cascade delete if any exist)
        cursor.execute("DELETE FROM Exam WHERE exam_id = %s", (exam_id,))
        db.commit()
        
        flash(f"Exam '{exam['exam_name']}' deleted successfully.", "success")
        
    except Exception as e:
        flash(f"Failed to delete exam: {str(e)}", "error")
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for('faculty_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


















# from flask import Flask, render_template, redirect, url_for, request, session, flash
# from mysql.connector import connect
# from datetime import datetime

# app = Flask(__name__)

# # Database connection
# db = connect(
#     host="localhost",
#     port=3306,
#     user="root",
#     password="rootroot",
#     database="flask_db_2"
# )

# # get cursor
# cursor = db.cursor(dictionary=True)

#         # cursor.execute('SELECT * FROM users')
#         # users = cursor.fetchall()
#         # print(users)


# app.secret_key = 'your_secret_key'


# #---------- ROUTES ----------

# @app.route('/')
# def home():
#     user_email = session.get('email')
#     first_name = session.get('first_name')  # ← Get from session
    
#     if not user_email:
#         return redirect(url_for('login'))
    
#     return render_template('home.html', email=user_email, first_name=first_name) 


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
        
#         # Generate or get student_id (NSHE number)
#         # You'll need to add an input field for this in register.html
#         student_id = request.form.get('student_id')  # Add this field to your form!

#         cursor.execute(
#             "INSERT INTO Student (student_id, email, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s)", 
#             (student_id, email, password, first_name, last_name)
#         )
#         db.commit()
        
#         flash("Registration successful! Please log in.", "success")
#         return redirect(url_for('login'))

#     return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM Student WHERE email = %s AND password = %s", (email, password))
#         Student = cursor.fetchone()
#         cursor.close()

#         if Student:
#             session['email'] = Student['email']
#             session['password'] = Student['password']
#             session['first_name'] = Student['first_name']
#             session['last_name'] = Student['last_name']

#             flash("Login successful!", "success")  # Success flash message
#             return redirect(url_for('home'))
#         else:
#             flash("Invalid email or NSHE number.", "error")  # Error flash message


#     return render_template('login.html')


# @app.route('/logout')
# def logout():
#     session.clear() 
#     return redirect(url_for('home'))


# @app.route('/exam_menu')
# def exam_menu():
#     print("Rendering exam_menu.html")
#     return render_template('exam_menu.html')


# @app.route('/confirmation')
# def confirmation():
#     return render_template('confirmation.html')


# @app.route('/history')
# def history():
#     if 'email' not in session:
#         return redirect(url_for('login'))
#     return render_template('history.html')


# if __name__ == '__main__':
#      app.run(host = '0.0.0.0', port = 5001, debug=True)
#      print("Server is running on http://localhost:5001") 

