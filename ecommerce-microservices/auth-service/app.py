from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os
from dataclasses import dataclass
from typing import Dict, Optional

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# In-memory user storage (replace with database in production)
users: Dict[str, dict] = {}

@dataclass
class User:
    username: str
    password_hash: str
    email: str

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# HTML Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Auth Service</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <h2>{{ title }}</h2>
    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}
    {% if success %}
        <div class="success">{{ success }}</div>
    {% endif %}
    
    <form method="POST">
        {% if register %}
        <div class="form-group">
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>
        {% endif %}
        <div class="form-group">
            <label>Username:</label>
            <input type="text" name="username" required>
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit">{{ button_text }}</button>
    </form>
    
    <div class="nav">
        {% if register %}
            <a href="/login">Already have an account? Login</a>
        {% else %}
            <a href="/register">Don't have an account? Register</a>
        {% endif %}
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; }
        .token-box { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .token { word-break: break-all; font-family: monospace; font-size: 12px; }
        button { padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #c82333; }
        .api-info { background: #e9ecef; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Welcome, {{ username }}!</h2>
        <form method="POST" action="/logout" style="margin: 0;">
            <button type="submit">Logout</button>
        </form>
    </div>
    
    <div class="token-box">
        <h3>Your JWT Token:</h3>
        <div class="token">{{ token }}</div>
    </div>
    
    <div class="api-info">
        <h3>API Usage:</h3>
        <p><strong>Protected Endpoint:</strong> GET /api/protected</p>
        <p><strong>Header:</strong> Authorization: Bearer YOUR_TOKEN</p>
        <p><strong>User Info:</strong> GET /api/user</p>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    logger.info("Home route accessed")
    try:
        if 'username' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return f"Error: {e}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f"Login route accessed with method: {request.method}")
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username in users and check_password_hash(users[username]['password'], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template_string(LOGIN_TEMPLATE, 
                                            title="Login", 
                                            button_text="Login",
                                            error="Invalid credentials")
        
        return render_template_string(LOGIN_TEMPLATE, 
                                    title="Login", 
                                    button_text="Login")
    except Exception as e:
        logger.error(f"Error in login route: {e}")
        return f"Error: {e}", 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if username in users:
            return render_template_string(LOGIN_TEMPLATE, 
                                        title="Register", 
                                        button_text="Register",
                                        register=True,
                                        error="Username already exists")
        
        users[username] = {
            'password': generate_password_hash(password),
            'email': email
        }
        
        return render_template_string(LOGIN_TEMPLATE, 
                                    title="Login", 
                                    button_text="Login",
                                    success="Account created! Please login.")
    
    return render_template_string(LOGIN_TEMPLATE, 
                                title="Register", 
                                button_text="Register",
                                register=True)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.secret_key, algorithm='HS256')
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                username=username, 
                                token=token)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    if username in users and check_password_hash(users[username]['password'], password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.secret_key, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'username': username
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({'message': 'Username, password, and email required'}), 400
    
    if username in users:
        return jsonify({'message': 'Username already exists'}), 409
    
    users[username] = {
        'password': generate_password_hash(password),
        'email': email
    }
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/protected')
@token_required
def protected(current_user):
    return jsonify({
        'message': f'Hello {current_user}! This is a protected endpoint.',
        'user': current_user
    })

@app.route('/api/user')
@token_required
def user_info(current_user):
    user_data = users.get(current_user)
    if user_data:
        return jsonify({
            'username': current_user,
            'email': user_data['email']
        })
    return jsonify({'message': 'User not found'}), 404

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create a default admin user for testing
    if 'admin' not in users:
        users['admin'] = {
            'password': generate_password_hash('admin123'),
            'email': 'admin@example.com'
        }
    
    logger.info("Starting Flask application...")
    logger.info(f"Available routes: {[rule.rule for rule in app.url_map.iter_rules()]}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
