"""
Sarhad College of Arts, Commerce & Science - Student Admission Portal
=======================================================================

DATABASE MODELS:
----------------
1. Student
   - Stores student registration details
   - Fields: id, student_id, name, email, mobile, dob, gender, category,
     address, father_name, mother_name, guardian_phone, course_pref_1/2/3,
     academic_details (10th/12th marks), status, merit_rank, payment_status,
     payment_id, payment_date, created_at, updated_at

2. Application
   - Stores application form data and document uploads
   - Fields: id, appid, studentid, personal_info, family_info, academic_info,
     course_pref_1/2/3, doc_1 to doc_10 (document filenames), status,
     remarks, payment_date, receipt_no, created_at

3. Admin
   - Stores admin user credentials
   - Fields: id, username, password, name, role, created_at

4. Notification
   - Stores system notifications for students
   - Fields: id, student_id, title, message, is_read, created_at

5. Payment
   - Stores payment transaction records
   - Fields: id, student_id, amount, payment_mode, transaction_id,
     receipt_no, payment_date, status

Note: Uses SQLAlchemy ORM with SQLite database (config.py)
"""

import os
import csv
import io
import random
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login as admin to continue', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

COURSES = {
    'Computer Science': {
        'fees': 75000, 'seats': 120, 'duration': '4 Years',
        'eligibility': '10+2 with Physics, Chemistry, Mathematics',
        'description': 'Covers programming, AI, ML, Data Science, Web Development'
    },
    'Information Technology': {
        'fees': 65000, 'seats': 100, 'duration': '4 Years',
        'eligibility': '10+2 with Physics, Chemistry, Mathematics',
        'description': 'Software development, Networking, Cloud Computing'
    },
    'Electronics Engineering': {
        'fees': 60000, 'seats': 80, 'duration': '4 Years',
        'eligibility': '10+2 with Physics, Chemistry, Mathematics',
        'description': 'Circuit design, Embedded systems, VLSI'
    },
    'Mechanical Engineering': {
        'fees': 55000, 'seats': 90, 'duration': '4 Years',
        'eligibility': '10+2 with Physics, Chemistry, Mathematics',
        'description': 'Automobiles, Robotics, Thermal Engineering'
    },
    'Civil Engineering': {
        'fees': 50000, 'seats': 70, 'duration': '4 Years',
        'eligibility': '10+2 with Physics, Chemistry, Mathematics',
        'description': 'Construction, Structural Engineering, Surveying'
    },
    'Business Administration': {
        'fees': 45000, 'seats': 60, 'duration': '3 Years',
        'eligibility': '10+2 in any stream',
        'description': 'Management, Marketing, Finance, HR'
    },
    'Data Science': {
        'fees': 80000, 'seats': 50, 'duration': '4 Years',
        'eligibility': '10+2 with Mathematics',
        'description': 'Big Data, Analytics, Machine Learning, AI'
    },
    'Artificial Intelligence': {
        'fees': 85000, 'seats': 40, 'duration': '4 Years',
        'eligibility': '10+2 with Mathematics',
        'description': 'Deep Learning, Neural Networks, NLP, Robotics'
    }
}

DOCUMENT_CHECKLIST = [
    'Passport Size Photographs',
    '10th Mark Sheet & Certificate',
    '12th Mark Sheet & Certificate',
    'Transfer Certificate (TC)',
    'Income Certificate',
    'Caste Certificate (if applicable)',
    'Domicile Certificate',
    'Aadhar Card'
]

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Personal Info
    father_name = db.Column(db.String(100), nullable=True)
    mother_name = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(20), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    religion = db.Column(db.String(50), nullable=True)
    caste = db.Column(db.String(50), nullable=True)
    domicile_state = db.Column(db.String(50), nullable=True)
    aadhaar = db.Column(db.String(20), nullable=True)
    differently_abled = db.Column(db.String(10), nullable=True)
    disability_type = db.Column(db.String(100), nullable=True)
    
    # Address
    address = db.Column(db.Text, nullable=True)
    perm_address = db.Column(db.Text, nullable=True)
    corr_address = db.Column(db.Text, nullable=True)
    emergency_name = db.Column(db.String(100), nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    parent_mobile = db.Column(db.String(20), nullable=True)
    parent_name = db.Column(db.String(100), nullable=True)
    parent_contact = db.Column(db.String(20), nullable=True)
    
    # SSC (10th)
    ssc_school = db.Column(db.String(200), nullable=True)
    ssc_board = db.Column(db.String(50), nullable=True)
    ssc_year = db.Column(db.String(10), nullable=True)
    ssc_marks = db.Column(db.String(20), nullable=True)
    ssc_seat_no = db.Column(db.String(50), nullable=True)
    
    # HSC (12th)
    hsc_college = db.Column(db.String(200), nullable=True)
    hsc_board = db.Column(db.String(50), nullable=True)
    hsc_year = db.Column(db.String(10), nullable=True)
    hsc_marks = db.Column(db.String(20), nullable=True)
    hsc_stream = db.Column(db.String(50), nullable=True)
    
    # Additional
    entrance_score = db.Column(db.String(20), nullable=True)
    gap_year = db.Column(db.String(10), nullable=True)
    gap_reason = db.Column(db.Text, nullable=True)
    previous_admission = db.Column(db.String(10), nullable=True)
    
    # Course preferences
    course_pref_1 = db.Column(db.String(50), nullable=True)
    course_pref_2 = db.Column(db.String(50), nullable=True)
    course_pref_3 = db.Column(db.String(50), nullable=True)
    medium = db.Column(db.String(50), nullable=True)
    hostel = db.Column(db.String(10), nullable=True)
    
    # Payment
    payment_status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(50), nullable=True)
    payment_amount = db.Column(db.Integer, default=500)
    payment_date = db.Column(db.DateTime, nullable=True)
    merit_rank = db.Column(db.Integer, nullable=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.String(20), unique=True, nullable=False)
    studentid = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)
    academic_details = db.Column(db.Text, nullable=False)
    documents = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text, nullable=True)
    student = db.relationship('Student', backref='application')
    
    # Document fields
    doc_photo = db.Column(db.String(100), nullable=True)
    doc_signature = db.Column(db.String(100), nullable=True)
    doc_ssc_marksheet = db.Column(db.String(100), nullable=True)
    doc_hsc_marksheet = db.Column(db.String(100), nullable=True)
    doc_hsc_tc = db.Column(db.String(100), nullable=True)
    doc_aadhaar = db.Column(db.String(100), nullable=True)
    doc_caste_cert = db.Column(db.String(100), nullable=True)
    doc_income_cert = db.Column(db.String(100), nullable=True)
    doc_domicile = db.Column(db.String(100), nullable=True)
    doc_migration = db.Column(db.String(100), nullable=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied = db.Column(db.Boolean, default=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_app_id():
    return 'SCAS-2025-' + str(random.randint(10000, 99999))

def generate_student_id():
    return 'SCAS-2025-' + str(random.randint(10000, 99999))

def generate_payment_id():
    return 'PAY' + datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))

def calculate_merit_rank():
    students = Student.query.filter(Student.entrance_score != None).order_by(Student.entrance_score.desc()).all()
    for rank, student in enumerate(students, 1):
        student.merit_rank = rank
    db.session.commit()

def generate_invoice_pdf(student, application):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.3*inch, bottomMargin=0.3*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#667eea'), spaceAfter=15, alignment=1)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2c3e50'), spaceBefore=15, spaceAfter=8)
    
    elements.append(Paragraph("ADMISSION PORTAL", title_style))
    elements.append(Paragraph("Application Invoice / Receipt", ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.gray, alignment=1, spaceBottom=20)))
    
    invoice_data = [
        ['Invoice No:', f'INV-{application.appid}', 'Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Student ID:', student.student_id, 'Email:', student.email[:25]],
        ['Payment ID:', student.payment_id or 'N/A', 'Amount:', f'Rs.{student.payment_amount}'],
    ]
    
    table = Table(invoice_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray), ('TEXTCOLOR', (1, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Personal Details", heading_style))
    personal_data = [
        ['Full Name:', student.name], ['Contact:', student.contact], ['DOB:', student.dob or 'N/A'],
        ['Gender:', student.gender or 'N/A'], ['Address:', (student.address or 'N/A')[:40]],
        ['Parent Name:', student.parent_name or 'N/A'], ['Parent Contact:', student.parent_contact or 'N/A'],
    ]
    table = Table(personal_data, colWidths=[1.8*inch, 4.2*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9), ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))
    
    course_info = COURSES.get(student.course, {})
    elements.append(Paragraph("Academic & Application Details", heading_style))
    academic_data = [
        ['Applied Course:', student.course], ['Duration:', course_info.get('duration', 'N/A')],
        ['Annual Fees:', f"Rs.{course_info.get('fees', 0):,}"],
        ['10th:', f"{student.tenth_school} - {student.tenth_marks}% ({student.tenth_year})"],
        ['12th:', f"{student.twelfth_school} - {student.twelfth_marks}% ({student.twelfth_year})"],
        ['Entrance Score:', student.entrance_score or 'N/A'], ['Application ID:', application.appid],
        ['Status:', application.status.upper()],
    ]
    table = Table(academic_data, colWidths=[1.8*inch, 4.2*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9), ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (1, 6), (1, 7), colors.HexColor('#27ae60') if application.status == 'approved' else colors.HexColor('#f39c12')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("Thank you for applying!", ParagraphStyle('Normal', fontSize=11, textColor=colors.HexColor('#667eea'), alignment=1)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html', courses=COURSES)

@app.route('/courses')
def courses_page():
    return render_template('courses.html', courses=COURSES)

@app.route('/course/<course_name>')
def course_detail(course_name):
    course = COURSES.get(course_name)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('courses_page'))
    return render_template('course_detail.html', course=course, course_name=course_name, courses=COURSES)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        new_contact = Contact(name=request.form.get('name'), email=request.form.get('email'), subject=request.form.get('subject'), message=request.form.get('message'))
        db.session.add(new_contact)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        captcha = request.form.get('captcha')
        if captcha != '7':
            flash('Incorrect captcha answer!', 'error')
            return redirect(url_for('register'))
        
        if request.form.get('password') != request.form.get('confirm_password'):
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(request.form.get('password')) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))
        
        if Student.query.filter_by(email=request.form.get('email')).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        existing_student = Student.query.filter_by(student_id=request.form.get('student_id')).first()
        if existing_student:
            flash('Application number already registered!', 'error')
            return redirect(url_for('register'))
        
        student_id = generate_student_id()
        app_ref = 'SCAS-2025-' + str(random.randint(10000, 99999))
        
        new_student = Student(
            student_id=student_id,
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=generate_password_hash(request.form.get('password')),
            contact=request.form.get('contact'),
            dob=request.form.get('dob'),
            gender=request.form.get('gender'),
            category=request.form.get('category'),
            course=request.form.get('course') if request.form.get('course') else 'Not Selected'
        )
        db.session.add(new_student)
        db.session.commit()
        
        flash(f'Registration successful! Your Application No: {student_id}. Please login to continue.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', courses=COURSES)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'register_student_id' not in session and 'student_id' not in session:
        return redirect(url_for('login'))
    student_id = session.get('register_student_id') or session.get('student_id')
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return redirect(url_for('login'))
    if student.payment_status == 'paid':
        flash('Payment already completed!', 'success')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        student.payment_status = 'paid'
        student.payment_id = generate_payment_id()
        student.payment_date = datetime.utcnow()
        db.session.commit()
        session['student_id'] = student.student_id
        session['student_name'] = student.name
        session['user_type'] = 'student'
        session.pop('register_student_id', None)
        flash('Payment successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('payment.html', student=student, course_info=COURSES.get(student.course, {}))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type')
        
        if login_type == 'admin':
            admin = Admin.query.filter_by(username=request.form.get('username')).first()
            if admin and check_password_hash(admin.password, request.form.get('password')):
                session['admin_id'] = admin.admin_id
                session['user_type'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials!', 'error')
            return redirect(url_for('login'))
        
        email_or_id = request.form.get('email')
        student = None
        
        if '@' in email_or_id:
            student = Student.query.filter_by(email=email_or_id).first()
        else:
            student = Student.query.filter_by(student_id=email_or_id).first()
        
        if student and check_password_hash(student.password, request.form.get('password')):
            session['student_id'] = student.student_id
            session['student_name'] = student.name
            session['user_type'] = 'student'
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid application number/email or password!', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    return redirect(url_for('dashboard'))

@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    existing_application = Application.query.filter_by(studentid=student.student_id).first()
    if existing_application and existing_application.status != 'draft':
        return redirect(url_for('dashboard'))
    
    saved_progress = session.get('application_progress', {})
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if data.get('save_progress'):
                session['application_progress'] = data
                return jsonify({'status': 'saved'})
        
        if existing_application:
            existing_application.status = 'submitted'
            app_number = existing_application.appid
        else:
            app_id = generate_app_id()
            new_application = Application(
                appid=app_id,
                studentid=student.student_id,
                academic_details=f"Course: {request.form.get('course_pref_1')}, SSC: {request.form.get('ssc_marks')}, HSC: {request.form.get('hsc_marks')}",
                status='submitted'
            )
            db.session.add(new_application)
            app_number = app_id
        
        student.name = request.form.get('full_name', student.name)
        student.father_name = request.form.get('father_name')
        student.mother_name = request.form.get('mother_name')
        student.dob = request.form.get('dob')
        student.gender = request.form.get('gender')
        student.category = request.form.get('category')
        student.nationality = request.form.get('nationality')
        student.religion = request.form.get('religion')
        student.caste = request.form.get('caste')
        student.domicile_state = request.form.get('domicile_state')
        student.aadhaar = request.form.get('aadhaar')
        student.differently_abled = request.form.get('differently_abled')
        student.disability_type = request.form.get('disability_type')
        student.ssc_school = request.form.get('ssc_school')
        student.ssc_board = request.form.get('ssc_board')
        student.ssc_year = request.form.get('ssc_year')
        student.ssc_marks = request.form.get('ssc_marks')
        student.ssc_seat_no = request.form.get('ssc_seat_no')
        student.hsc_college = request.form.get('hsc_college')
        student.hsc_board = request.form.get('hsc_board')
        student.hsc_year = request.form.get('hsc_year')
        student.hsc_marks = request.form.get('hsc_marks')
        student.hsc_stream = request.form.get('hsc_stream')
        student.gap_year = request.form.get('gap_year')
        student.gap_reason = request.form.get('gap_reason')
        student.previous_admission = request.form.get('previous_admission')
        student.course_pref_1 = request.form.get('course_pref_1')
        student.course_pref_2 = request.form.get('course_pref_2')
        student.course_pref_3 = request.form.get('course_pref_3')
        student.medium = request.form.get('medium')
        student.hostel = request.form.get('hostel')
        student.perm_address = f"{request.form.get('perm_house_no')}, {request.form.get('perm_street')}, {request.form.get('perm_city')}, {request.form.get('perm_district')}, {request.form.get('perm_state')} - {request.form.get('perm_pin')}"
        student.corr_address = f"{request.form.get('corr_house_no')}, {request.form.get('corr_street')}, {request.form.get('corr_city')}, {request.form.get('corr_district')}, {request.form.get('corr_state')} - {request.form.get('corr_pin')}"
        student.emergency_name = request.form.get('emergency_name')
        student.emergency_contact = request.form.get('emergency_contact')
        student.parent_mobile = request.form.get('parent_mobile')
        
        db.session.commit()
        session.pop('application_progress', None)
        
        flash(f'Application submitted successfully! Application No: {app_number}', 'success')
        return render_template('apply.html', application_submitted=True, application_number=app_number)
    
    return render_template('apply.html', saved=saved_progress, courses=COURSES)

NOTIFICATION_LIST = [
    {'id': 1, 'title': 'Application Submitted', 'message': 'Your application has been submitted successfully.', 'created_at': datetime(2025, 7, 1, 10, 30), 'read': True},
    {'id': 2, 'title': 'Documents Verified', 'message': 'Your uploaded documents have been verified by the administration.', 'created_at': datetime(2025, 7, 5, 14, 20), 'read': False},
    {'id': 3, 'title': 'Merit List Published', 'message': 'Merit list for all courses has been published.', 'created_at': datetime(2025, 8, 15, 9, 0), 'read': False},
]

@app.route('/dashboard')
@login_required
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    application = Application.query.filter_by(studentid=student.student_id).first()
    
    doc_fields = ['doc_photo', 'doc_signature', 'doc_ssc_marksheet', 'doc_hsc_marksheet', 
                  'doc_hsc_tc', 'doc_aadhaar', 'doc_caste_cert', 'doc_income_cert', 
                  'doc_domicile', 'doc_migration']
    doc_names = ['Passport Photo', 'Signature', 'SSC Marksheet', 'HSC Marksheet', 
                 'HSC Leaving Cert', 'Aadhaar Card', 'Category Cert', 'Income Cert', 
                 'Domicile Cert', 'Migration Cert']
    
    uploaded_count = 0
    document_status = []
    for i, field in enumerate(doc_fields):
        is_uploaded = bool(getattr(application, field, None)) if application else False
        if is_uploaded:
            uploaded_count += 1
        document_status.append({
            'name': doc_names[i],
            'status': 'uploaded' if is_uploaded else 'pending',
            'uploaded_date': 'Uploaded' if is_uploaded else None
        })
    
    return render_template('dashboard.html', student=student, application=application, 
                          uploaded_count=uploaded_count, document_status=document_status,
                          notifications=NOTIFICATION_LIST, application_notes='')

@app.route('/download-application-pdf')
def download_application_pdf():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        return redirect(url_for('login'))
    
    application = Application.query.filter_by(studentid=student.student_id).first()
    if not application:
        flash('No application found', 'error')
        return redirect(url_for('dashboard'))
    
    pdf_buffer = generate_application_summary_pdf(student, application)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, 
                   download_name=f'Application_{application.appid}.pdf')

def generate_application_summary_pdf(student, application):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.3*inch, bottomMargin=0.3*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, 
                                 textColor=colors.HexColor('#1a237e'), spaceAfter=15, alignment=1)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, 
                                   textColor=colors.HexColor('#1a237e'), spaceBefore=15, spaceAfter=8)
    
    elements.append(Paragraph("SARHAD COLLEGE OF ARTS, COMMERCE & SCIENCE", title_style))
    elements.append(Paragraph("Application Form Summary", ParagraphStyle('Subtitle', parent=styles['Normal'], 
                fontSize=12, textColor=colors.gray, alignment=1, spaceBottom=20)))
    elements.append(Paragraph(f"Application No: {application.appid}", ParagraphStyle('Normal', 
                fontSize=11, textColor=colors.HexColor('#1a237e'), alignment=1, spaceBottom=20)))
    
    personal_data = [
        ['Full Name:', student.name or 'N/A'],
        ['Date of Birth:', student.dob or 'N/A'],
        ['Gender:', student.gender or 'N/A'],
        ['Category:', student.category or 'N/A'],
        ['Father Name:', student.father_name or 'N/A'],
        ['Mother Name:', student.mother_name or 'N/A'],
        ['Mobile:', student.contact or 'N/A'],
        ['Email:', student.email or 'N/A'],
    ]
    table = Table(personal_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("Personal Information", heading_style))
    elements.append(table)
    
    academic_data = [
        ['SSC Board:', student.ssc_board or 'N/A'],
        ['SSC School:', student.ssc_school or 'N/A'],
        ['SSC Year:', student.ssc_year or 'N/A'],
        ['SSC Marks:', student.ssc_marks or 'N/A'],
        ['HSC Board:', student.hsc_board or 'N/A'],
        ['HSC College:', student.hsc_college or 'N/A'],
        ['HSC Year:', student.hsc_year or 'N/A'],
        ['HSC Marks:', student.hsc_marks or 'N/A'],
    ]
    table = Table(academic_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("Academic Information", heading_style))
    elements.append(table)
    
    course_data = [
        ['Course Preference 1:', student.course_pref_1 or 'N/A'],
        ['Course Preference 2:', student.course_pref_2 or 'N/A'],
        ['Course Preference 3:', student.course_pref_3 or 'N/A'],
        ['Medium:', student.medium or 'N/A'],
        ['Hostel Required:', student.hostel or 'N/A'],
    ]
    table = Table(course_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("Course Preference", heading_style))
    elements.append(table)
    
    elements.append(Paragraph(f"Application Status: {application.status.upper()}", 
                ParagraphStyle('Normal', fontSize=11, textColor=colors.HexColor('#2e7d32'), alignment=1, spaceBefore=20)))
    elements.append(Paragraph("Generated on: " + datetime.now().strftime('%d %B %Y %H:%M'), 
                ParagraphStyle('Normal', fontSize=9, textColor=colors.gray, alignment=1)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/student/application', methods=['GET', 'POST'])
def submit_application():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if student.payment_status != 'paid':
        flash('Please complete payment first!', 'error')
        return redirect(url_for('payment'))
    if Application.query.filter_by(studentid=student.student_id).first():
        flash('Application already submitted!', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        student.dob = request.form.get('dob')
        student.gender = request.form.get('gender')
        student.address = request.form.get('address')
        student.parent_name = request.form.get('parent_name')
        student.parent_contact = request.form.get('parent_contact')
        student.tenth_school = request.form.get('tenth_school')
        student.tenth_marks = request.form.get('tenth_marks')
        student.tenth_year = request.form.get('tenth_year')
        student.twelfth_school = request.form.get('twelfth_school')
        student.twelfth_marks = request.form.get('twelfth_marks')
        student.twelfth_year = request.form.get('twelfth_year')
        student.entrance_score = request.form.get('entrance_score')
        
        document_filename = None
        if 'documents' in request.files:
            file = request.files['documents']
            if file and allowed_file(file.filename):
                document_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))
        
        new_application = Application(appid=generate_app_id(), studentid=student.student_id,
            academic_details=f"10th: {student.tenth_marks}%, 12th: {student.twelfth_marks}%, Entrance: {student.entrance_score}",
            documents=document_filename)
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('application_form.html', student=student, courses=COURSES)

@app.route('/student/download-invoice/<appid>')
def download_invoice(appid):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    application = Application.query.filter_by(appid=appid).first()
    if not application or application.studentid != session['student_id']:
        flash('Application not found!', 'error')
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(student_id=session['student_id']).first()
    pdf_buffer = generate_invoice_pdf(student, application)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f'Invoice_{appid}.pdf')

@app.route('/merit-list')
def merit_list():
    selected_course = request.args.get('course', 'BCA')
    search = request.args.get('search', '')
    
    merit_published = True
    
    students = Student.query.filter(
        Student.course_pref_1 == selected_course,
        Student.merit_rank != None
    ).order_by(Student.merit_rank).all()
    
    seats = COURSES.get(selected_course, {}).get('seats', 60)
    
    search_result = None
    if search:
        found_student = Student.query.filter_by(student_id=search).first()
        if found_student and found_student.merit_rank:
            search_result = {
                'found': True,
                'student_id': found_student.student_id,
                'name': found_student.name,
                'course': found_student.course_pref_1 or found_student.course,
                'rank': found_student.merit_rank
            }
        else:
            search_result = {'found': False}
    
    return render_template('merit_list.html', 
                         merit_list=students, 
                         courses=list(COURSES.keys()),
                         selected_course=selected_course,
                         seats=seats,
                         merit_published=merit_published,
                         search=search,
                         search_result=search_result)

@app.route('/seats')
def seat_matrix():
    seat_data = {
        'BCA': {'total': 60, 'open': 31, 'sc': 6, 'st': 3, 'obc': 12, 'nt': 4, 'ews': 4, 'filled': 0, 'available': 60},
        'BSc CS': {'total': 60, 'open': 31, 'sc': 6, 'st': 3, 'obc': 12, 'nt': 4, 'ews': 4, 'filled': 0, 'available': 60},
        'BCom': {'total': 120, 'open': 62, 'sc': 12, 'st': 6, 'obc': 24, 'nt': 8, 'ews': 8, 'filled': 0, 'available': 120},
        'BCom (BM)': {'total': 60, 'open': 31, 'sc': 6, 'st': 3, 'obc': 12, 'nt': 4, 'ews': 4, 'filled': 0, 'available': 60},
        'BCom (CA)': {'total': 60, 'open': 31, 'sc': 6, 'st': 3, 'obc': 12, 'nt': 4, 'ews': 4, 'filled': 0, 'available': 60},
        'BA': {'total': 120, 'open': 62, 'sc': 12, 'st': 6, 'obc': 24, 'nt': 8, 'ews': 8, 'filled': 0, 'available': 120},
    }
    
    for course in seat_data:
        filled = Student.query.filter_by(course_pref_1=course).count()
        seat_data[course]['filled'] = filled
        seat_data[course]['available'] = seat_data[course]['total'] - filled
    
    total_seats = sum(d['total'] for d in seat_data.values())
    filled_seats = sum(d['filled'] for d in seat_data.values())
    available_seats = sum(d['available'] for d in seat_data.values())
    
    return render_template('seat_matrix.html', 
                         seat_matrix=seat_data,
                         total_seats=total_seats,
                         filled_seats=filled_seats,
                         available_seats=available_seats,
                         last_updated='15 August 2025')

@app.route('/track', methods=['GET', 'POST'])
@app.route('/track-application', methods=['GET', 'POST'])
def track_application():
    if request.method == 'POST':
        track_type = request.form.get('track_type', 'app')
        application_no = request.form.get('application_no', '').strip()
        dob = request.form.get('dob', '').strip()
        mobile = request.form.get('mobile', '').strip()
        otp = request.form.get('otp', '').strip()
        
        student = None
        
        if track_type == 'app':
            if not application_no:
                return render_template('track.html', error='Please enter your Application Number.', result_found=False)
            student = Student.query.filter_by(student_id=application_no).first()
            if not student and dob:
                student = Student.query.filter_by(student_id=application_no, dob=dob).first()
        else:
            if not mobile:
                return render_template('track.html', error='Please enter your Mobile Number.', result_found=False)
            if otp != '123456':
                return render_template('track.html', error='Invalid OTP. For demo, use 123456', result_found=False)
            student = Student.query.filter_by(contact=mobile).first()
        
        if student:
            current_status = student.status or 'registered'
            
            result = {
                'status': current_status,
                'name': student.name,
                'student_id': student.student_id,
                'course': student.course_pref_1 or student.course or 'N/A',
                'applied_date': student.created_at.strftime('%d-%m-%Y') if student.created_at else 'N/A',
                'remarks': student.remarks if hasattr(student, 'remarks') else None
            }
            
            return render_template('track.html', result=result, result_found=True)
        
        return render_template('track.html', error='No application found with this Application Number. Please check and try again.', result_found=False)
    
    return render_template('track.html', result_found=False)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form.get('username')).first()
        if admin and check_password_hash(admin.password, request.form.get('password')):
            session['admin_id'] = admin.admin_id
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials!', 'error')
        return redirect(url_for('admin_login'))
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    applications = Application.query.all()
    stats = {
        'total': len(applications),
        'submitted': len([a for a in applications if a.status == 'submitted']),
        'under_review': len([a for a in applications if a.status == 'under_review']),
        'verified': len([a for a in applications if a.status == 'verified']),
        'admitted': len([a for a in applications if a.status == 'admitted']),
        'rejected': len([a for a in applications if a.status == 'rejected']),
    }
    
    course_labels = list(COURSES.keys())
    course_data = [Student.query.filter_by(course_pref_1=c).count() for c in course_labels]
    
    categories = ['General', 'OBC', 'SC', 'ST', 'NT', 'SBC']
    category_data = [Student.query.filter_by(category=c).count() for c in categories]
    
    recent = Application.query.order_by(Application.submitted_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_applications=recent,
                         course_labels=course_labels, course_data=course_data,
                         category_labels=categories, category_data=category_data)

@app.route('/admin/applications')
@admin_required
def admin_applications():
    search = request.args.get('search', '')
    course_filter = request.args.get('course', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    
    query = Application.query.join(Student)
    
    if search:
        query = query.filter((Student.name.contains(search)) | (Student.student_id.contains(search)) | (Student.contact.contains(search)))
    if course_filter:
        query = query.filter(Student.course_pref_1 == course_filter)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if category_filter:
        query = query.filter(Student.category == category_filter)
    
    applications = query.order_by(Application.submitted_at.desc()).all()
    
    return render_template('admin/applications.html', applications=applications,
                         search=search, course_filter=course_filter, 
                         status_filter=status_filter, category_filter=category_filter)

@app.route('/admin/application/<appid>')
@admin_required
def admin_application_detail(appid):
    application = Application.query.filter_by(appid=appid).first_or_404()
    student = Student.query.filter_by(student_id=application.studentid).first()
    
    return render_template('admin/application_detail.html', application=application, student=student)

@app.route('/admin/update-status/<appid>', methods=['POST'])
@admin_required
def admin_update_status(appid):
    application = Application.query.filter_by(appid=appid).first()
    if application:
        application.status = request.form.get('status', application.status)
        application.remarks = request.form.get('remarks', '')
        
        student = Student.query.filter_by(student_id=application.studentid).first()
        if student:
            student.status = application.status
        
        db.session.commit()
        flash('Status updated!', 'success')
    
    return redirect(url_for('admin_application_detail', appid=appid))

@app.route('/admin/merit-list')
@admin_required
def admin_merit_list():
    course = request.args.get('course', 'BCA')
    
    course_map = {
        'BCA': ['BCA', 'Computer Science'],
        'BSc CS': ['BSc CS', 'Computer Science'],
        'BCom': ['BCom', 'Commerce'],
        'BCom (BM)': ['BCom (BM)', 'Commerce'],
        'BCom (CA)': ['BCom (CA)', 'Commerce'],
        'BA': ['BA', 'Arts']
    }
    
    course_values = course_map.get(course, [course])
    
    merit_list = Student.query.filter(
        (Student.course_pref_1.in_(course_values)) | (Student.course.in_(course_values)),
        Student.hsc_marks != None
    ).order_by(Student.hsc_marks.desc()).all()
    
    return render_template('admin/merit_list.html', merit_list=merit_list, selected_course=course, courses=COURSES)

@app.route('/admin/generate-merit', methods=['POST'])
@admin_required
def admin_generate_merit():
    course = request.form.get('course')
    cutoff = float(request.form.get('cutoff', 0))
    seats = int(request.form.get('seats', 60))
    
    course_map = {
        'BCA': ['BCA', 'Computer Science'],
        'BSc CS': ['BSc CS', 'Computer Science'],
        'BCom': ['BCom', 'Commerce'],
        'BCom (BM)': ['BCom (BM)', 'Commerce'],
        'BCom (CA)': ['BCom (CA)', 'Commerce'],
        'BA': ['BA', 'Arts']
    }
    
    course_values = course_map.get(course, [course])
    
    students = Student.query.filter(
        (Student.course_pref_1.in_(course_values)) | (Student.course.in_(course_values)),
        Student.hsc_marks != None,
        Student.hsc_marks >= str(cutoff)
    ).order_by(Student.hsc_marks.desc()).limit(seats).all()
    
    for i, student in enumerate(students, 1):
        student.merit_rank = i
    
    db.session.commit()
    flash(f'Merit list generated for {course} - {len(students)} students listed', 'success')
    return redirect(url_for('admin_merit_list', course=course))

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html', courses=COURSES, settings={
        'reg_start': '2025-06-01',
        'reg_end': '2025-07-31',
        'doc_verify': '2025-08-01',
        'merit_date': '2025-08-15',
        'announcement': 'Admissions Open for 2025-26'
    })

@app.route('/admin/save-settings', methods=['POST'])
@admin_required
def admin_save_settings():
    flash('Settings saved successfully!', 'success')
    return redirect(url_for('admin_settings'))

@app.route('/admin/messages')
@admin_required
def admin_messages():
    messages = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/export/<format>')
@admin_required
def admin_export_csv(format):
    applications = db.session.query(Student, Application).outerjoin(Application, Student.student_id == Application.studentid).all()
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Name', 'Email', 'Contact', 'Course', 'Payment Status', 'App ID', 'Status', 'Merit Rank'])
        for student, app in applications:
            writer.writerow([student.student_id, student.name, student.email, student.contact, student.course,
                student.payment_status, app.appid if app else 'N/A', app.status if app else 'N/A', student.merit_rank or 'N/A'])
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='students.csv')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export-merit-pdf')
@admin_required
def admin_export_merit_pdf():
    flash('PDF export coming soon!', 'info')
    return redirect(url_for('admin_merit_list'))

@app.route('/admin/student/<student_id>')
@admin_required
def admin_student_detail(student_id):
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    application = Application.query.filter_by(studentid=student_id).first()
    return render_template('admin/student_detail.html', student=student, application=application, courses=COURSES)

@app.route('/admin/delete-student/<student_id>')
@admin_required
def delete_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        application = Application.query.filter_by(studentid=student_id).first()
        if application:
            db.session.delete(application)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve-all')
@admin_required
def approve_all():
    applications = Application.query.filter_by(status='pending').all()
    for app in applications:
        app.status = 'approved'
        student = Student.query.filter_by(student_id=app.studentid).first()
        if student:
            student.status = 'approved'
    db.session.commit()
    calculate_merit_rank()
    flash('All applications approved!', 'success')
    return redirect(url_for('admin_dashboard'))

DOCUMENT_LIST = [
    {'id': 'photo', 'name': 'Passport Size Photograph', 'required': True, 'formats': 'JPG, PNG', 'max_size': '200KB', 'max_bytes': 200*1024, 'accept': '.jpg,.jpeg,.png'},
    {'id': 'signature', 'name': 'Student Signature', 'required': True, 'formats': 'JPG, PNG', 'max_size': '100KB', 'max_bytes': 100*1024, 'accept': '.jpg,.jpeg,.png'},
    {'id': 'ssc_marksheet', 'name': 'SSC (10th) Marksheet', 'required': True, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'hsc_marksheet', 'name': 'HSC (12th) / Diploma Marksheet', 'required': True, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'hsc_tc', 'name': 'HSC (12th) Leaving Certificate', 'required': True, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'aadhaar', 'name': 'Aadhaar Card', 'required': True, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'caste_cert', 'name': 'Category/Caste Certificate', 'required': False, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'income_cert', 'name': 'Income Certificate', 'required': False, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'domicile', 'name': 'Domicile Certificate', 'required': False, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
    {'id': 'migration', 'name': 'Migration Certificate', 'required': False, 'formats': 'PDF, JPG', 'max_size': '2MB', 'max_bytes': 2*1024*1024, 'accept': '.pdf,.jpg,.jpeg,.png'},
]

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    application = Application.query.filter_by(studentid=student.student_id).first()
    
    if not application or application.status != 'submitted':
        return render_template('upload.html', student=student, application=application, documents=DOCUMENT_LIST, uploaded_count=0)
    
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'applications', application.appid)
    os.makedirs(upload_folder, exist_ok=True)
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if data.get('remove'):
                doc_id = data.get('document_id')
                doc_field = f'doc_{doc_id}'
                if hasattr(application, doc_field):
                    existing_file = getattr(application, doc_field)
                    if existing_file:
                        try:
                            os.remove(os.path.join(upload_folder, existing_file))
                        except:
                            pass
                    setattr(application, doc_field, None)
                    db.session.commit()
                return jsonify({'success': True})
        
        doc_id = request.form.get('document_id')
        file = request.files.get('file')
        
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        doc_config = next((d for d in DOCUMENT_LIST if d['id'] == doc_id), None)
        if not doc_config:
            return jsonify({'success': False, 'message': 'Invalid document type'})
        
        if file.size > doc_config['max_bytes']:
            return jsonify({'success': False, 'message': f'File size exceeds {doc_config["max_size"]} limit'})
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in doc_config['accept'].replace('.', ',').split(','):
            return jsonify({'success': False, 'message': 'Invalid file format'})
        
        filename = f"{doc_id}_{application.appid}{ext}"
        file.save(os.path.join(upload_folder, filename))
        
        doc_field = f'doc_{doc_id}'
        if hasattr(application, doc_field):
            old_file = getattr(application, doc_field)
            if old_file and old_file != filename:
                try:
                    os.remove(os.path.join(upload_folder, old_file))
                except:
                    pass
            setattr(application, doc_field, filename)
            db.session.commit()
        
        return jsonify({'success': True})
    
    uploaded_docs = []
    for doc in DOCUMENT_LIST:
        doc_field = f'doc_{doc["id"]}'
        filename = getattr(application, doc_field, None) if application else None
        file_size = ''
        if filename:
            try:
                size = os.path.getsize(os.path.join(upload_folder, filename))
                if size < 1024:
                    file_size = f'{size} B'
                elif size < 1024*1024:
                    file_size = f'{size/1024:.1f} KB'
                else:
                    file_size = f'{size/(1024*1024):.1f} MB'
            except:
                file_size = 'Unknown'
        
        uploaded_docs.append({
            **doc,
            'uploaded': bool(filename),
            'filename': filename or '',
            'file_size': file_size
        })
    
    uploaded_count = sum(1 for d in uploaded_docs if d['uploaded'])
    
    return render_template('upload.html', student=student, application=application, documents=uploaded_docs, uploaded_count=uploaded_count)

@app.route('/pay-fee')
@login_required
def pay_fee():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    application = Application.query.filter_by(studentid=student.student_id).first()
    
    if application and application.status in ['admitted', 'fee_paid']:
        flash('Fee already paid!', 'info')
        return redirect(url_for('dashboard'))
    
    course = student.course_pref_1 or student.course or 'BCA'
    
    fee_structure = {
        'BCA': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BSc CS': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BCom': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (BM)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (CA)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BA': {'tuition': 8000, 'development': 1500, 'library': 500, 'exam': 500, 'swf': 200}
    }
    
    fee_breakdown = fee_structure.get(course, fee_structure['BCA'])
    fee_breakdown['total'] = sum(fee_breakdown.values())
    
    return render_template('payment.html', student=student, course=course, fee_breakdown=fee_breakdown)

@app.route('/pay-fee/process', methods=['POST'])
def process_payment():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    import time
    import random
    
    time.sleep(2)
    
    course = student.course_pref_1 or student.course or 'BCA'
    
    fee_structure = {
        'BCA': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BSc CS': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BCom': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (BM)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (CA)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BA': {'tuition': 8000, 'development': 1500, 'library': 500, 'exam': 500, 'swf': 200}
    }
    
    fee_breakdown = fee_structure.get(course, fee_structure['BCA'])
    total_amount = sum(fee_breakdown.values())
    
    receipt_no = f"SCA-{int(time.time())}-{random.randint(1000, 9999)}"
    from datetime import datetime
    payment_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    
    application = Application.query.filter_by(studentid=student.student_id).first()
    if application:
        application.status = 'fee_paid'
        if hasattr(application, 'payment_date'):
            application.payment_date = datetime.now()
        if hasattr(application, 'receipt_no'):
            application.receipt_no = receipt_no
        db.session.commit()
    
    session['payment_completed'] = True
    
    payment_mode_map = {
        'online': 'Online Payment',
        'dd': 'DD/Challan',
        'bank': 'Bank Transfer'
    }
    payment_mode = payment_mode_map.get(request.form.get('payment_mode', 'online'), 'Online Payment')
    
    receipt = {
        'receipt_no': receipt_no,
        'date': payment_date,
        'student_name': student.name,
        'application_no': student.student_id,
        'course': course,
        'payment_mode': payment_mode,
        'amount': total_amount
    }
    
    return render_template('payment_success.html', receipt=receipt)

@app.route('/pay-fee/receipt/<receipt_no>')
def fee_receipt(receipt_no):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    
    course = student.course_pref_1 or student.course or 'BCA'
    
    fee_structure = {
        'BCA': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BSc CS': {'tuition': 18000, 'development': 2000, 'library': 500, 'exam': 800, 'swf': 200},
        'BCom': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (BM)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BCom (CA)': {'tuition': 10000, 'development': 2000, 'library': 500, 'exam': 600, 'swf': 200},
        'BA': {'tuition': 8000, 'development': 1500, 'library': 500, 'exam': 500, 'swf': 200}
    }
    
    fee_breakdown = fee_structure.get(course, fee_structure['BCA'])
    total_amount = sum(fee_breakdown.values())
    
    from datetime import datetime
    payment_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    
    def number_to_words(n):
        if n == 0: return 'Zero'
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 
                'Eighteen', 'Nineteen', 'Twenty']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        if n < 20: return ones[n]
        if n < 100: return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
        if n < 1000: return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' and ' + number_to_words(n % 100))
        if n < 100000: return number_to_words(n // 1000) + ' Thousand' + ('' if n % 1000 == 0 else ' ' + number_to_words(n % 1000))
        if n < 10000000: return number_to_words(n // 100000) + ' Lakh' + ('' if n % 100000 == 0 else ' ' + number_to_words(n % 100000))
        return number_to_words(n // 10000000) + ' Crore' + ('' if n % 10000000 == 0 else ' ' + number_to_words(n % 10000000))
    
    amount_in_words = number_to_words(total_amount) + ' Rupees Only'
    
    return render_template('receipt.html', 
                         receipt_no=receipt_no,
                         date=payment_date,
                         student_name=student.name,
                         application_no=student.student_id,
                         course=course,
                         amount=total_amount,
                         fee_breakdown=fee_breakdown,
                         amount_in_words=amount_in_words)

@app.route('/logout')
def logout():
    user_type = session.get('user_type', 'user')
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('index'))

def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(admin_id='ADM001', username='admin', password=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
