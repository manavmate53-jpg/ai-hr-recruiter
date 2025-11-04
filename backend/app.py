from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
import base64
import json
import PyPDF2
import io
import re
import random
import string

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# CORS configuration for development
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
DATABASE = 'candidates.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            dob TEXT,
            location TEXT NOT NULL,
            skills TEXT,
            experience TEXT,
            code TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'New',
            interview_date TEXT,
            interview_time TEXT,
            interview_location TEXT,
            message_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Job settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            job_description TEXT,
            requirements TEXT,
            location TEXT,
            salary_range TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, full_name)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@example.com', 'Administrator'))
    
    # Create default job settings if not exists
    cursor.execute('SELECT COUNT(*) FROM job_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO job_settings (job_title, company_name, job_description, requirements, location, salary_range)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'Software Engineer',
            'Tech Corp',
            'We are looking for talented software engineers',
            'Python, JavaScript, React',
            'Mumbai, India',
            '₹8-12 LPA'
        ))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Initialize database on startup
init_db()

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============= AUTHENTICATION ROUTES =============

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username')
            }
        })
    return jsonify({'authenticated': False}), 401

# ============= CANDIDATE ROUTES =============

def generate_candidate_code():
    """Generate unique candidate code"""
    year = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"HR{year}-{random_num}"

def extract_text_from_image(image_data):
    """Extract text from image using OCR (basic implementation)"""
    # In production, use Tesseract OCR or Google Vision API
    # For demo, return placeholder
    return "Sample extracted text from image"

def extract_candidate_info(text):
    """Extract candidate information from text using regex"""
    info = {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'skills': '',
        'experience': ''
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        info['email'] = emails[0]
    
    # Extract phone
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)
    if phones:
        info['phone'] = phones[0].strip()
    
    # Extract location (common Indian cities)
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
    for city in cities:
        if city.lower() in text.lower():
            info['location'] = city
            break
    
    return info

@app.route('/api/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    """Upload and process resume"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, PDF allowed'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
        else:
            # For images, use basic extraction (in production, use OCR)
            text = extract_text_from_image(file_content)
        
        # Extract candidate information
        candidate_info = extract_candidate_info(text)
        candidate_info['code'] = generate_candidate_code()
        candidate_info['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'candidate': candidate_info
        })
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({'error': str(e)}), 500

def save_to_database(candidate_data):
    """Save candidate data to SQLite database"""
    try:
        # Validate mandatory fields
        email = candidate_data.get('email', '').strip()
        phone = candidate_data.get('phone', '').strip()
        location = candidate_data.get('location', '').strip()
        
        missing_fields = []
        if not email:
            missing_fields.append('Email')
        if not phone:
            missing_fields.append('Phone')
        if not location:
            missing_fields.append('Location')
        
        if missing_fields:
            return {
                'success': False,
                'error': f'Missing mandatory fields: {", ".join(missing_fields)}'
            }
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if candidate already exists
        cursor.execute('SELECT id FROM candidates WHERE email = ?', (email,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return {
                'success': False,
                'error': f'Candidate with email {email} is already registered'
            }
        
        # Generate unique code
        code = generate_candidate_code()
        while True:
            cursor.execute('SELECT id FROM candidates WHERE code = ?', (code,))
            if not cursor.fetchone():
                break
            code = generate_candidate_code()
        
        # Insert candidate
        cursor.execute('''
            INSERT INTO candidates (date, name, phone, email, dob, location, skills, experience, code, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            candidate_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            candidate_data.get('name', ''),
            phone,
            email,
            candidate_data.get('dob', ''),
            location,
            candidate_data.get('skills', ''),
            candidate_data.get('experience', ''),
            code,
            'New'
        ))
        
        conn.commit()
        candidate_id = cursor.lastrowid
        conn.close()
        
        return {
            'success': True,
            'candidate_id': candidate_id,
            'code': code
        }
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/api/save-candidate', methods=['POST'])
@login_required
def save_candidate():
    """Save candidate to database"""
    data = request.json
    candidate_data = data.get('candidate', {})
    
    result = save_to_database(candidate_data)
    
    return jsonify(result)

def get_all_candidates():
    """Retrieve all candidates from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, date, name, phone, email, dob, location, skills, experience, code, status, 
                   interview_date, interview_time, interview_location, message_sent
            FROM candidates
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        candidates = []
        for row in rows:
            candidate = {
                'id': row['id'],
                'date': row['date'],
                'name': row['name'] or '',
                'phone': row['phone'] or '',
                'email': row['email'] or '',
                'dob': row['dob'] or '',
                'location': row['location'] or '',
                'skills': row['skills'] or '',
                'experience': row['experience'] or '',
                'code': row['code'],
                'status': row['status'] or 'New',
                'interview_date': row['interview_date'] or '',
                'interview_time': row['interview_time'] or '',
                'interview_location': row['interview_location'] or '',
                'message_sent': row['message_sent'] or 0
            }
            candidates.append(candidate)
        
        return candidates
    except Exception as e:
        print(f"Error retrieving candidates: {e}")
        return []

@app.route('/api/candidates', methods=['GET'])
@login_required
def get_candidates():
    """Get all candidates from database"""
    candidates = get_all_candidates()
    return jsonify({
        'success': True,
        'candidates': candidates
    })

def update_candidate_in_database(candidate_id, field, value):
    """Update a specific field for a candidate in database"""
    try:
        allowed_fields = ['status', 'interview_slot', 'interview_date', 'interview_time', 'interview_location', 'name', 'phone', 'email', 'dob', 'location', 'skills', 'experience', 'message_sent']
        if field not in allowed_fields:
            return {'success': False, 'error': 'Invalid field'}
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        query = f'UPDATE candidates SET {field} = ? WHERE id = ?'
        cursor.execute(query, (value, candidate_id))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        if affected_rows == 0:
            return {'success': False, 'error': 'Candidate not found'}
        
        return {'success': True}
    except Exception as e:
        print(f"Error updating candidate: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/api/update-candidate', methods=['POST'])
@login_required
def update_candidate():
    """Update candidate status or interview slot"""
    data = request.json
    candidate_id = data.get('id')
    field = data.get('field')
    value = data.get('value')
    
    if not candidate_id or not field or value is None:
        return jsonify({'error': 'id, field, and value are required'}), 400
    
    result = update_candidate_in_database(candidate_id, field, value)
    return jsonify(result)

# ============= MESSAGING ROUTES =============

def send_gmail(to_email, subject, message):
    """Simulated email sending - DEMO MODE"""
    try:
        import time
        time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"📧 SIMULATED EMAIL SENT")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Message:\n{message}")
        print(f"{'='*60}\n")
        
        try:
            with open('sent_messages.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"EMAIL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Message:\n{message}\n")
                f.write(f"{'='*60}\n")
        except:
            pass
        
        return {
            'success': True,
            'demo_mode': True,
            'message': 'Email simulated successfully'
        }
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return {'success': False, 'error': str(e)}

def send_sms(to_phone, message):
    """Simulated SMS sending - DEMO MODE"""
    try:
        import time
        time.sleep(0.3)
        
        print(f"\n{'='*60}")
        print(f"📱 SIMULATED SMS SENT")
        print(f"{'='*60}")
        print(f"To: {to_phone}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        
        try:
            with open('sent_messages.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"SMS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"To: {to_phone}\n")
                f.write(f"Message: {message}\n")
                f.write(f"{'='*60}\n")
        except:
            pass
        
        return {
            'success': True,
            'demo_mode': True,
            'message': 'SMS simulated successfully',
            'sid': f'DEMO_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        }
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    """Send email and/or SMS to candidate"""
    try:
        data = request.json
        candidate_id = data.get('candidate_id')
        email = data.get('email')
        phone = data.get('phone')
        subject = data.get('subject', 'Job Opportunity')
        message = data.get('message')
        send_email_flag = data.get('send_email', True)
        send_sms_flag = data.get('send_sms', True)
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        results = {'email': None, 'sms': None}
        
        if send_email_flag and email:
            email_result = send_gmail(email, subject, message)
            results['email'] = email_result
        
        if send_sms_flag and phone:
            sms_result = send_sms(phone, message)
            results['sms'] = sms_result
        
        if candidate_id:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('UPDATE candidates SET message_sent = 1 WHERE id = ?', (candidate_id,))
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'message': 'Message sent successfully (Demo Mode)',
            'email_sent': bool(results['email']),
            'sms_sent': bool(results['sms'])
        })
            
    except Exception as e:
        print(f"❌ Send message error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/message-log', methods=['GET'])
@login_required
def get_message_log():
    """Get simulated message log"""
    try:
        messages = []
        log_file = 'sent_messages.log'
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            blocks = content.split('='*60)
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                    
                lines = block.split('\n')
                msg = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('EMAIL -') or line.startswith('SMS -'):
                        msg['type'] = 'email' if 'EMAIL' in line else 'sms'
                        msg['timestamp'] = line.split(' - ')[1] if ' - ' in line else ''
                    elif line.startswith('To:'):
                        msg['to'] = line.replace('To:', '').strip()
                    elif line.startswith('Subject:'):
                        msg['subject'] = line.replace('Subject:', '').strip()
                    elif line.startswith('Message:'):
                        msg_index = lines.index(line)
                        msg['message'] = '\n'.join(lines[msg_index+1:]).strip()
                        break
                
                if msg.get('to'):
                    messages.append(msg)
        
        messages.reverse()
        
        return jsonify({
            'success': True,
            'messages': messages[:50]
        })
        
    except Exception as e:
        print(f"❌ Error reading message log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= JOB SETTINGS ROUTES =============

@app.route('/api/job-settings', methods=['GET'])
@login_required
def get_job_settings():
    """Get job settings"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_settings ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            settings = {
                'job_title': row['job_title'],
                'company_name': row['company_name'],
                'job_description': row['job_description'],
                'requirements': row['requirements'],
                'location': row['location'],
                'salary_range': row['salary_range']
            }
            return jsonify({'success': True, 'settings': settings})
        else:
            return jsonify({'success': True, 'settings': {}})
            
    except Exception as e:
        print(f"❌ Error getting job settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/job-settings', methods=['POST'])
@login_required
def update_job_settings():
    """Update job settings"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM job_settings')
        
        cursor.execute('''
            INSERT INTO job_settings (job_title, company_name, job_description, requirements, location, salary_range)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('job_title', ''),
            data.get('company_name', ''),
            data.get('job_description', ''),
            data.get('requirements', ''),
            data.get('location', ''),
            data.get('salary_range', '')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Job settings updated'})
        
    except Exception as e:
        print(f"❌ Error updating job settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
