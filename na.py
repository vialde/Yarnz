from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import os
from functools import wraps
from datetime import timedelta

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management (use a fixed secret in production)
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout
bcrypt = Bcrypt(app)

# In a real application, you would use a database
# This is a simple mock database for demonstration
users_db = {
    "admin@narrativechaos.com": {
        "password": bcrypt.generate_password_hash("admin123").decode('utf-8'),
        "username": "Admin"
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        
        if email in users_db and bcrypt.check_password_hash(users_db[email]['password'], password):
            session.permanent = remember
            session['user_id'] = email
            session['username'] = users_db[email]['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid email or password. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

# Create a new user (simplified registration)
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        
        if email in users_db:
            error = 'Email already registered. Please use a different email.'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users_db[email] = {"password": hashed_password, "username": username}
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)

# Template for login.html
@app.route('/template/login')
def login_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #1a1a2e;
            color: #ffffff;
            height: 100vh;
        }
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            margin-top: 50px;
        }
        .brand-title {
            color: #7b2cbf;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .brand-tagline {
            color: #9d4edd;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-control {
            background-color: #0f3460;
            border: 1px solid #1f4287;
            color: #ffffff;
        }
        .form-control:focus {
            background-color: #0f3460;
            border-color: #7b2cbf;
            box-shadow: 0 0 0 0.25rem rgba(123, 44, 191, 0.25);
            color: #ffffff;
        }
        .btn-primary {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
        }
        .btn-primary:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
        }
        .alert {
            margin-bottom: 20px;
        }
        .form-check-input:checked {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
        }
        .form-label {
            color: #c8c8c8;
        }
        .signup-link, .forgot-link {
            color: #9d4edd;
            text-decoration: none;
        }
        .signup-link:hover, .forgot-link:hover {
            color: #7b2cbf;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="login-container">
                    <h1 class="brand-title">Narrative Chaos</h1>
                    <p class="brand-tagline">Where your stories come to life</p>
                    
                    {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="post" action="{{ url_for('login') }}">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="mb-3 d-flex justify-content-between align-items-center">
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                <label class="form-check-label" for="remember">Remember me</label>
                            </div>
                            <a href="#" class="forgot-link">Forgot password?</a>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">Sign In</button>
                        </div>
                        <div class="text-center mt-3">
                            <span class="text-muted">Don't have an account?</span>
                            <a href="{{ url_for('register') }}" class="signup-link ms-1">Sign up</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Template for dashboard.html
@app.route('/template/dashboard')
def dashboard_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #1a1a2e;
            color: #ffffff;
        }
        .dashboard-container {
            padding: 2rem;
        }
        .header {
            background-color: #16213e;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .navbar-brand {
            color: #7b2cbf;
            font-weight: bold;
        }
        .welcome-message {
            color: #9d4edd;
        }
        .btn-outline-light:hover {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header d-flex justify-content-between align-items-center">
            <span class="navbar-brand">Narrative Chaos</span>
            <div>
                <span class="welcome-message me-3">Welcome, {{ username }}</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <h2>Dashboard</h2>
                    <p>Your storytelling journey begins here. This is where you'll create, manage, and explore your narratives.</p>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <div class="alert alert-info">
                        This is a placeholder dashboard for the Narrative Chaos application. In a real application, this would contain your stories, writing tools, and other features.
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Template for register.html
@app.route('/template/register')
def register_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - Register</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #1a1a2e;
            color: #ffffff;
            height: 100vh;
        }
        .register-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            margin-top: 50px;
        }
        .brand-title {
            color: #7b2cbf;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .brand-tagline {
            color: #9d4edd;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-control {
            background-color: #0f3460;
            border: 1px solid #1f4287;
            color: #ffffff;
        }
        .form-control:focus {
            background-color: #0f3460;
            border-color: #7b2cbf;
            box-shadow: 0 0 0 0.25rem rgba(123, 44, 191, 0.25);
            color: #ffffff;
        }
        .btn-primary {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
        }
        .btn-primary:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
        }
        .alert {
            margin-bottom: 20px;
        }
        .form-label {
            color: #c8c8c8;
        }
        .login-link {
            color: #9d4edd;
            text-decoration: none;
        }
        .login-link:hover {
            color: #7b2cbf;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="register-container">
                    <h1 class="brand-title">Narrative Chaos</h1>
                    <p class="brand-tagline">Create your storyteller account</p>
                    
                    {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="post" action="{{ url_for('register') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">Create Account</button>
                        </div>
                        <div class="text-center mt-3">
                            <span class="text-muted">Already have an account?</span>
                            <a href="{{ url_for('login') }}" class="login-link ms-1">Sign in</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

if __name__ == '__main__':
    # Create project structure
    from pathlib import Path
    
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    with open(templates_dir / 'login.html', 'w') as f:
        f.write(login_template())
    
    with open(templates_dir / 'dashboard.html', 'w') as f:
        f.write(dashboard_template())
    
    with open(templates_dir / 'register.html', 'w') as f:
        f.write(register_template())
    
    # Run the app
    app.run(debug=True)
