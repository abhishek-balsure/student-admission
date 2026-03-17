# Sarhad College Admission Portal

A comprehensive student admission management system for Sarhad College of Arts, Commerce & Science, Katraj, Pune (Affiliated to Savitribai Phule Pune University).

## Features

### Student Portal
- **Registration** - Student registration with captcha verification
- **Login** - Secure login for students and admins
- **Application Form** - Multi-step application form with course preferences
- **Document Upload** - Upload required documents (photo, signature, marksheets, etc.)
- **Dashboard** - Track application status, view notifications
- **Fee Payment** - Simulated payment gateway with receipt generation
- **Track Application** - Public tracker using Application ID or Mobile + OTP

### Admin Panel
- **Dashboard** - View statistics, charts, recent applications
- **Applications Management** - Filter, search, view, and update application status
- **Merit List Generation** - Generate and publish merit lists by course
- **Messages** - View contact form submissions
- **Settings** - Configure admission dates and announcements

### Public Pages
- **Home** - Landing page with important dates and announcements
- **Courses** - Course information and eligibility
- **Merit List** - Public merit list display (after published)
- **Seat Matrix** - Available seats by category
- **Admission Process** - Step-by-step admission timeline
- **Contact** - Contact form for inquiries

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Icons**: Font Awesome 6
- **Fonts**: Inter, Playfair Display

## Installation

1. Clone the repository:
```bash
git clone https://github.com/abhishek-balsure/student-admission.git
cd student-admission
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-sqlalchemy flask-login werkzeug reportlab
```

4. Run the application:
```bash
python app.py
```

5. Open browser at `http://localhost:5000`

## Default Credentials

### Admin
- Username: `admin`
- Password: `admin123`

### Test Student
Register a new account through the registration form.

## Courses Offered

| Course | Duration | Fees | Seats |
|--------|----------|------|-------|
| BCA (Bachelor of Computer Applications) | 3 Years | ₹21,500 | 60 |
| BSc CS (Bachelor of Science in Computer Science) | 3 Years | ₹21,500 | 60 |
| BCom (Bachelor of Commerce) | 3 Years | ₹13,300 | 120 |
| BCom (BM) (Bachelor of Commerce - Business Management) | 3 Years | ₹13,300 | 60 |
| BCom (CA) (Bachelor of Commerce - Computer Application) | 3 Years | ₹13,300 | 60 |
| BA (Bachelor of Arts) | 3 Years | ₹10,700 | 120 |

## Fee Structure

### BCA / BSc CS
- Tuition Fee: ₹18,000
- Development Fee: ₹2,000
- Library Fee: ₹500
- Exam Fee: ₹800
- Student Welfare Fund: ₹200
- **Total: ₹21,500**

### BCom / BCom (BM) / BCom (CA)
- Tuition Fee: ₹10,000
- Development Fee: ₹2,000
- Library Fee: ₹500
- Exam Fee: ₹600
- Student Welfare Fund: ₹200
- **Total: ₹13,300**

### BA
- Tuition Fee: ₹8,000
- Development Fee: ₹1,500
- Library Fee: ₹500
- Exam Fee: ₹500
- Student Welfare Fund: ₹200
- **Total: ₹10,700**

## Project Structure

```
student-admission/
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── static/
│   ├── css/
│   │   └── design-system.css
│   ├── style.css
│   └── uploads/           # Uploaded documents
├── templates/
│   ├── base.html         # Main base template
│   ├── admin/
│   │   ├── admin_base.html
│   │   ├── dashboard.html
│   │   ├── applications.html
│   │   ├── application_detail.html
│   │   ├── merit_list.html
│   │   ├── settings.html
│   │   └── messages.html
│   ├── index.html
│   ├── courses.html
│   ├── merit_list.html
│   ├── seat_matrix.html
│   ├── admission_process.html
│   ├── register.html
│   ├── login.html
│   ├── apply.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── payment.html
│   └── track.html
└── admission_portal.db   # SQLite database
```

## License

This project is for educational purposes.

## Contact

**Sarhad College of Arts, Commerce & Science**
Katraj, Pune - 411046

Email: sarhadcollege@gmail.com
Phone: (020) 24368621
