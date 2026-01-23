# Exam Registration System

A comprehensive web-based exam registration platform built for the College of Southern Nevada (CSN), enabling students to register for placement exams and faculty to manage exam sessions efficiently.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Security Features](#-security-features)
- [API Endpoints](#-api-endpoints)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### For Students
- 🔐 **Secure Registration & Authentication** - Bcrypt password hashing with email validation
- 📅 **Exam Registration** - Browse and register for available placement exams
- ⏱️ **Real-time Availability** - See live seat availability and capacity
- 📊 **Registration Management** - View registration history and cancel bookings
- 🎯 **Smart Limitations** - Maximum 3 exam registrations per student
- ✅ **Duplicate Prevention** - Cannot register for the same exam twice
- 📧 **Email Integration** - Confirmation messages and notifications

### For Faculty
- 🎓 **Exam Session Creation** - Schedule multiple exam sessions with custom parameters
- 📍 **Location Management** - Add and manage exam room locations
- 👥 **Student Registration Tracking** - View complete lists of registered students
- 📈 **Dashboard Analytics** - Monitor registration status and capacity
- 🗑️ **Exam Management** - Delete empty exam sessions
- 🔒 **Access Control** - Faculty-only administrative features

### System-Wide
- 🌐 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- 🔍 **Input Validation** - Client-side and server-side validation
- ⚡ **Flash Messaging** - Real-time user feedback and notifications
- 🎨 **Modern UI/UX** - Clean, gradient-based design with intuitive navigation
- 🔄 **Session Management** - Secure session handling with Flask

## 🎥 Demo

### Student Workflow
1. Register with CSN student email and NSHE number
2. Login and browse available exams
3. Register for up to 3 exams
4. View and manage registrations
5. Receive confirmation messages

### Faculty Workflow
1. Register with CSN faculty email
2. Create exam locations
3. Schedule exam sessions
4. Monitor registrations in real-time
5. View registered student lists
6. Delete unused exam sessions

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **Flask 3.0+** - Web framework
- **MySQL 8.0+** - Relational database
- **mysql-connector-python** - Database connectivity
- **bcrypt** - Password hashing and authentication

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom styling with gradients and animations
- **JavaScript (Vanilla)** - Client-side interactivity
- **Jinja2** - Template engine

### Security
- **Bcrypt** - Password hashing with salt
- **Flask Sessions** - Secure session management
- **SQL Parameterization** - SQL injection prevention
- **Flask-WTF** - CSRF protection for all forms

## 🏗️ System Architecture

```
┌─────────────────┐
│   Client        │
│  (Browser)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Server   │
│  - Routes       │
│  - Auth Logic   │
│  - Business     │
│    Logic        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MySQL DB       │
│  - Students     │
│  - Faculty      │
│  - Exams        │
│  - Registrations│
│  - Locations    │
└─────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/csn-exam-registration.git
cd csn-exam-registration
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install flask mysql-connector-python bcrypt flask-wtf
```

Or use the requirements.txt file:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Connection
Edit the database configuration in `app.py`:
```python
def get_db():
    return connect(
        host="localhost",
        port=3306,
        user="your_username",      # Change this
        password="your_password",  # Change this
        database="flask_db"        # Change this
    )
```

### Step 5: Update Secret Key
In `app.py`, change the secret key:
```python
app.secret_key = 'your-super-secret-key-here'  # Change this!
```

## 💾 Database Setup

### Create Database
```sql
CREATE DATABASE flask_db;
USE flask_db;
```

### Create Tables

#### Student Table
```sql
CREATE TABLE Student (
    student_id VARCHAR(10) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Faculty Table
```sql
CREATE TABLE Faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Location Table
```sql
CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL,
    building_number VARCHAR(20) NOT NULL,
    campus_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Exam Table
```sql
CREATE TABLE Exam (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    faculty_id INT NOT NULL,
    location_id INT NOT NULL,
    exam_date DATE NOT NULL,
    exam_time TIME NOT NULL,
    capacity INT DEFAULT 20,
    seats_filled INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES Location(location_id) ON DELETE RESTRICT
);
```

#### ExamRegistration Table
```sql
CREATE TABLE ExamRegistration (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    exam_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE,
    UNIQUE KEY unique_registration (student_id, exam_id)
);
```

### Insert Sample Data (Optional)

#### Sample Locations
```sql
INSERT INTO Location (room_number, building_number, campus_name) VALUES
('101', 'A', 'Charleston Campus'),
('202', 'B', 'Charleston Campus'),
('Lab-A', 'Science', 'North Las Vegas Campus'),
('305', 'C', 'Henderson Campus');
```

## 📖 Usage

### Running the Application

#### Development Mode
```bash
python app.py
```
The application will run on `http://localhost:5001`

#### Production Mode
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Default User Accounts

#### Creating a Student Account
1. Navigate to `/register`
2. Email format: `1234567890@student.csn.edu`
3. Enter your 10-digit NSHE number
4. Password: Use your NSHE number (will be hashed)
5. Fill in first and last name

#### Creating a Faculty Account
1. Navigate to `/register`
2. Email format: `professor@csn.edu`
3. Choose a secure password
4. Fill in first and last name

### Testing the Application

#### Student Flow
```
1. Register → Login → Browse Exams → Register for Exam → View History
```

#### Faculty Flow
```
1. Register → Login → Create Location → Create Exam → View Registrations
```

## 📁 Project Structure

```
csn-exam-registration/
│
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html               # Base template with navigation
│   ├── home.html               # Home page for both roles
│   ├── login.html              # Login page
│   ├── register.html           # User registration
│   ├── exam_menu.html          # Student: Browse exams
│   ├── history.html            # Student: Registration history
│   ├── confirmation.html       # Student: Registration confirmation
│   ├── faculty_dashboard.html  # Faculty: Dashboard
│   ├── create_exam.html        # Faculty: Create exam session
│   ├── manage_locations.html   # Faculty: Manage locations
│   └── view_registrations.html # Faculty: View registrations
│
├── static/                     # Static files (if needed)
│   ├── css/                    # Additional CSS
│   ├── js/                     # Additional JavaScript
│   └── images/                 # Images and assets
│
└── venv/                       # Virtual environment (not in git)
```

## 🔒 Security Features

### Password Security
- **Bcrypt Hashing**: All passwords are hashed using bcrypt with auto-generated salts
- **Cost Factor**: Default cost factor of 12 (4096 iterations)
- **One-way Encryption**: Passwords cannot be decrypted, only verified

### SQL Injection Prevention
- **Parameterized Queries**: All database queries use parameterization
- **Input Validation**: Server-side and client-side validation
- **Type Checking**: Proper data type enforcement

### Session Security
- **Secure Sessions**: Flask's built-in session management
- **Session Clearing**: Proper logout with session.clear()
- **CSRF Protection**: Flask-WTF protects all POST requests with CSRF tokens
- **Token Validation**: All forms automatically include and validate CSRF tokens

### Access Control
- **Role-based Access**: Separate student and faculty routes
- **Authentication Checks**: `@app.route` decorators verify login status
- **Authorization**: Faculty can only manage their own exams

### Input Validation Examples
```python
# Email validation
if '@student.csn.edu' in email:
    # Student registration logic
elif '@csn.edu' in email:
    # Faculty registration logic

# Duplicate registration prevention
if check_duplicate_registration(student_id, exam_id):
    flash("You are already registered for this exam.", "error")

# Capacity checks
if exam['seats_filled'] >= exam['capacity']:
    flash("This exam session is full.", "error")
```

## 🔗 API Endpoints

### Public Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page (redirects based on role) |
| GET/POST | `/login` | User login |
| GET/POST | `/register` | User registration |
| GET | `/logout` | User logout |

### Student Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exam_menu` | View available exams |
| POST | `/register_exam/<exam_id>` | Register for an exam |
| GET | `/confirmation` | Registration confirmation |
| GET | `/history` | View registration history |
| POST | `/cancel_registration/<registration_id>` | Cancel registration |

### Faculty Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/faculty_dashboard` | Faculty dashboard |
| GET/POST | `/create_exam` | Create exam session |
| GET | `/view_registrations/<exam_id>` | View exam registrations |
| POST | `/delete_exam/<exam_id>` | Delete exam session |
| GET/POST | `/admin/locations` | Manage locations |

### Potential Additional Features
- [ ] Email confirmation system (SMTP integration)
- [ ] PDF exam ticket generation
- [ ] Calendar integration (iCal/Google Calendar)
- [ ] Advanced search and filtering
- [ ] Export registration lists to CSV/Excel
- [ ] QR code check-in system
- [ ] Push notifications
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Exam reminder system (24hr before)
- [ ] Waitlist functionality
- [ ] Admin panel for system-wide management
- [ ] Analytics and reporting dashboard
- [ ] API for mobile app integration

### Potential Technical Improvements
- [ ] Migrate to SQLAlchemy ORM
- [ ] Add comprehensive unit tests
- [ ] Implement Redis caching
- [ ] Add API rate limiting
- [ ] Implement password reset functionality
- [ ] Add two-factor authentication (2FA)
- [ ] Containerize with Docker
- [ ] CI/CD pipeline setup
- [ ] Automated database backups

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide for Python
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions
- Test thoroughly before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- College of Southern Nevada for project inspiration
- Flask documentation and community
- MySQL documentation
- All contributors and testers

---

**⭐ If you find this project useful, please consider giving it a star!**

---

### Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/csn-exam-registration.git
cd csn-exam-registration
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure database in app.py, then run
python app.py

# Access at http://localhost:5001
```

### Common Issues

**Issue**: Database connection error
**Solution**: Verify MySQL is running and credentials are correct in `app.py`

**Issue**: Import error for bcrypt
**Solution**: `pip install bcrypt`

**Issue**: Port 5001 already in use
**Solution**: Change port in `app.py`: `app.run(port=5002)`

### Project Statistics

- **Lines of Code**: ~800+
- **Number of Routes**: 15+
- **Database Tables**: 5
- **HTML Templates**: 10
- **Development Time**: Varies based on features

---