import os
import csv
import io
import random
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
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
    
    dob = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    parent_name = db.Column(db.String(100), nullable=True)
    parent_contact = db.Column(db.String(20), nullable=True)
    
    tenth_school = db.Column(db.String(200), nullable=True)
    tenth_marks = db.Column(db.String(20), nullable=True)
    tenth_year = db.Column(db.String(10), nullable=True)
    twelfth_school = db.Column(db.String(200), nullable=True)
    twelfth_marks = db.Column(db.String(20), nullable=True)
    twelfth_year = db.Column(db.String(10), nullable=True)
    entrance_score = db.Column(db.String(20), nullable=True)
    
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
    student = db.relationship('Student', backref='application')

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
    return 'APP' + datetime.now().strftime('%Y%m%d%H%M%S')

def generate_student_id():
    return 'STU' + datetime.now().strftime('%Y%m%d%H%M%S')

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
        if request.form.get('password') != request.form.get('confirm_password'):
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        if Student.query.filter_by(email=request.form.get('email')).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        student_id = generate_student_id()
        new_student = Student(student_id=student_id, name=request.form.get('name'), email=request.form.get('email'),
            password=generate_password_hash(request.form.get('password')), contact=request.form.get('contact'), course=request.form.get('course'))
        db.session.add(new_student)
        db.session.commit()
        session['register_student_id'] = student_id
        flash('Registration successful! Please complete payment.', 'success')
        return redirect(url_for('payment'))
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
        return redirect(url_for('student_dashboard'))
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
        return redirect(url_for('student_dashboard'))
    return render_template('payment.html', student=student, course_info=COURSES.get(student.course, {}))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student = Student.query.filter_by(email=request.form.get('email')).first()
        if student and check_password_hash(student.password, request.form.get('password')):
            session['student_id'] = student.student_id
            session['student_name'] = student.name
            session['user_type'] = 'student'
            return redirect(url_for('student_dashboard'))
        flash('Invalid email or password!', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    application = Application.query.filter_by(studentid=student.student_id).first()
    return render_template('student_dashboard.html', student=student, application=application, courses=COURSES, checklist=DOCUMENT_CHECKLIST)

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
        return redirect(url_for('student_dashboard'))
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
        return redirect(url_for('student_dashboard'))
    return render_template('application_form.html', student=student, courses=COURSES)

@app.route('/student/download-invoice/<appid>')
def download_invoice(appid):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    application = Application.query.filter_by(appid=appid).first()
    if not application or application.studentid != session['student_id']:
        flash('Application not found!', 'error')
        return redirect(url_for('student_dashboard'))
    student = Student.query.filter_by(student_id=session['student_id']).first()
    pdf_buffer = generate_invoice_pdf(student, application)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f'Invoice_{appid}.pdf')

@app.route('/merit-list')
def merit_list():
    students = Student.query.filter(Student.entrance_score != None).order_by(Student.entrance_score.desc()).all()
    return render_template('merit_list.html', students=students, courses=COURSES)

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
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    status_filter = request.args.get('status', '')
    course_filter = request.args.get('course', '')
    search_query = request.args.get('search', '')
    
    query = db.session.query(Student, Application).outerjoin(Application, Student.student_id == Application.studentid)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if course_filter:
        query = query.filter(Student.course == course_filter)
    if search_query:
        query = query.filter((Student.name.contains(search_query)) | (Student.student_id.contains(search_query)) | (Student.email.contains(search_query)))
    
    stats = {'total': Student.query.count(), 'pending': Application.query.filter_by(status='pending').count(),
        'approved': Application.query.filter_by(status='approved').count(), 'rejected': Application.query.filter_by(status='rejected').count(),
        'paid': Student.query.filter_by(payment_status='paid').count()}
    
    return render_template('admin_dashboard.html', applications=query.all(), courses=list(COURSES.keys()), stats=stats,
        status_filter=status_filter, course_filter=course_filter, search_query=search_query, all_courses=COURSES)

@app.route('/admin/update-status/<appid>/<status>')
def update_status(appid, status):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    application = Application.query.filter_by(appid=appid).first()
    if application:
        application.status = status
        student = Student.query.filter_by(student_id=application.studentid).first()
        if student:
            student.status = status
            if status == 'approved':
                calculate_merit_rank()
        db.session.commit()
        flash(f'Application {status}!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/<format>')
def export_data(format):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
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

@app.route('/admin/messages')
def admin_messages():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    messages = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/student/<student_id>')
def admin_student_detail(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    application = Application.query.filter_by(studentid=student_id).first()
    return render_template('admin_student_detail.html', student=student, application=application, courses=COURSES)

@app.route('/admin/delete-student/<student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
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
def approve_all():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
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

@app.route('/logout')
def logout():
    session.clear()
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
