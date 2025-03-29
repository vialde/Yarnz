from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import os
from functools import wraps
from datetime import timedelta
import re
import base64
from werkzeug.utils import secure_filename

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
        "username": "Admin",
        "join_date": "2025-02-28",
        "bio": "System administrator and storyteller extraordinaire.",
        "profile_pic": None,
        "location": "Narrative City",
        "favorite_genre": "Science Fiction",
        "games_created": ["fantasy-123", "scifi-456"],
        "games_joined": ["fantasy-123", "scifi-456"]
    }
}

# Store games in memory (in a real app, this would be a database)
games_db = {
    "fantasy-123": {
        "id": "fantasy-123",
        "title": "The Forgotten Realms: Adventure Awaits",
        "host": "DungeonMaster42",
        "host_email": "admin@narrativechaos.com",
        "description": "A fantasy adventure set in a world of magic and mystery. Join forces with other players to explore dungeons, battle mythical creatures, and uncover ancient treasures.",
        "theme": "fantasy",
        "difficulty": "Moderate",
        "max_players": 6,
        "players": ["admin@narrativechaos.com"],  # List of player emails
        "started_date": "2025-02-25",
        "current_content": """The ancient castle loomed ahead, its crumbling towers silhouetted against the stormy sky. Lightning flashed, illuminating the jagged battlements for a brief, terrifying moment.

"I don't like this," whispered Elara, clutching her staff tighter. "The legends say no one who enters the Castle of Shadows ever returns."

Thorne, the battle-scarred warrior, unsheathed his broadsword. "Legends are often exaggerated," he replied, though his voice betrayed a hint of uncertainty.

The party stood at the edge of the drawbridge, the murky waters of the moat churning below. Something large moved beneath the surface, sending ripples across the water.

"We have no choice," said Garrick, the scholarly mage. "The artifact we seek lies within, and without it, the kingdom will fall to darkness within a fortnight."

As they took their first steps onto the ancient drawbridge, a bone-chilling howl echoed from within the castle walls..."""
    },
    "scifi-456": {
        "id": "scifi-456",
        "title": "Space Odyssey: The Final Frontier",
        "host": "CaptainKirk",
        "host_email": "admin@narrativechaos.com",
        "description": "Set in the distant future, this sci-fi narrative puts you in command of a starship exploring uncharted territories. Face alien civilizations, navigate interstellar politics, and make decisions that will shape the fate of the galaxy.",
        "theme": "scifi",
        "difficulty": "Hard",
        "max_players": 4,
        "players": ["admin@narrativechaos.com"],
        "started_date": "2025-02-28",
        "current_content": """The command deck of the Starship Horizon fell silent as the unknown vessel appeared on the viewscreen. It had emerged from the darkness of space without warning, its hull gleaming with a metallic sheen unlike any alloy known to Earth science.

"Sensors report no life signs, Captain," First Officer Vega said, her voice steady despite the tension. "But there's an energy signature I've never seen before."

Captain Reyes leaned forward in his chair, studying the enigmatic craft. "How did it get past our detection grid?"

"Unknown, sir," replied the young lieutenant at tactical. "It's as if it... folded space somehow."

The communications officer turned, her expression puzzled. "Captain, we're receiving a transmission. But it's not on any standard frequency."

"Let's hear it," Reyes ordered.

The bridge speakers crackled to life, filling the room with a series of rhythmic pulses and harmonic tones that seemed to resonate with the very metal of the ship itself...

"""
    }
}

# Store games in memory (in a real app, this would be a database)
games_db = {
    "fantasy-123": {
        "id": "fantasy-123",
        "title": "The Forgotten Realms: Adventure Awaits",
        "host": "DungeonMaster42",
        "host_email": "admin@narrativechaos.com",
        "description": "A fantasy adventure set in a world of magic and mystery. Join forces with other players to explore dungeons, battle mythical creatures, and uncover ancient treasures.",
        "theme": "fantasy",
        "difficulty": "Moderate",
        "max_players": 6,
        "players": ["admin@narrativechaos.com"],  # List of player emails
        "started_date": "2025-02-25",
        "current_content": """The ancient castle loomed ahead, its crumbling towers silhouetted against the stormy sky. Lightning flashed, illuminating the jagged battlements for a brief, terrifying moment.

"I don't like this," whispered Elara, clutching her staff tighter. "The legends say no one who enters the Castle of Shadows ever returns."

Thorne, the battle-scarred warrior, unsheathed his broadsword. "Legends are often exaggerated," he replied, though his voice betrayed a hint of uncertainty.

The party stood at the edge of the drawbridge, the murky waters of the moat churning below. Something large moved beneath the surface, sending ripples across the water.

"We have no choice," said Garrick, the scholarly mage. "The artifact we seek lies within, and without it, the kingdom will fall to darkness within a fortnight."

As they took their first steps onto the ancient drawbridge, a bone-chilling howl echoed from within the castle walls..."""
    },
    "scifi-456": {
        "id": "scifi-456",
        "title": "Space Odyssey: The Final Frontier",
        "host": "CaptainKirk",
        "host_email": "admin@narrativechaos.com",
        "description": "Set in the distant future, this sci-fi narrative puts you in command of a starship exploring uncharted territories. Face alien civilizations, navigate interstellar politics, and make decisions that will shape the fate of the galaxy.",
        "theme": "scifi",
        "difficulty": "Hard",
        "max_players": 4,
        "players": ["admin@narrativechaos.com"],
        "started_date": "2025-02-28",
        "current_content": """The command deck of the Starship Horizon fell silent as the unknown vessel appeared on the viewscreen. It had emerged from the darkness of space without warning, its hull gleaming with a metallic sheen unlike any alloy known to Earth science.

"Sensors report no life signs, Captain," First Officer Vega said, her voice steady despite the tension. "But there's an energy signature I've never seen before."

Captain Reyes leaned forward in his chair, studying the enigmatic craft. "How did it get past our detection grid?"

"Unknown, sir," replied the young lieutenant at tactical. "It's as if it... folded space somehow."

The communications officer turned, her expression puzzled. "Captain, we're receiving a transmission. But it's not on any standard frequency."

"Let's hear it," Reyes ordered.

The bridge speakers crackled to life, filling the room with a series of rhythmic pulses and harmonic tones that seemed to resonate with the very metal of the ship itself...

"""
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
    # Get current user data
    user_email = session.get('user_id')
    user_data = users_db.get(user_email, {})
    
    return render_template('dashboard.html', 
                          username=session.get('username'),
                          join_date=user_data.get('join_date', ''),
                          user_count=len(users_db))

# Enhanced registration with validation
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        username = request.form['username']
        
        # Validate inputs
        if email in users_db:
            error = 'Email already registered. Please use a different email.'
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = 'Please enter a valid email address.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(username) < 3:
            error = 'Username must be at least 3 characters long.'
        else:
            # All validation passed, create the new user
            from datetime import datetime
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users_db[email] = {
                "password": hashed_password, 
                "username": username,
                "join_date": datetime.now().strftime('%Y-%m-%d'),
                "bio": "",
                "profile_pic": None,
                "location": "",
                "favorite_genre": "",
                "games_created": [],
                "games_joined": []
            }
            flash('Registration successful! Please log in with your new account.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)

# Join Game (AJAX endpoint)
@app.route('/join-game/<game_id>', methods=['POST'])
@login_required
def join_game_action(game_id):
    user_email = session.get('user_id')
    
    # Check if game exists
    if game_id not in games_db:
        return {"success": False, "message": "Game not found"}, 404
    
    game = games_db[game_id]
    
    # Check if user is already in the game
    if user_email in game['players']:
        return {"success": True, "message": "You are already in this game"}, 200
    
    # Check if game is full
    if len(game['players']) >= game['max_players']:
        return {"success": False, "message": "Game is full"}, 400
    
    # Add user to game
    game['players'].append(user_email)
    
    # Add game to user's joined games
    if 'games_joined' not in users_db[user_email]:
        users_db[user_email]['games_joined'] = []
    
    if game_id not in users_db[user_email]['games_joined']:
        users_db[user_email]['games_joined'].append(game_id)
    
    return {"success": True, "message": "Successfully joined the game"}, 200

# Game Page (for a specific game)
@app.route('/game/<game_id>')
@login_required
def game_page(game_id):
    user_email = session.get('user_id')
    username = session.get('username')
    
    # Check if game exists
    if game_id not in games_db:
        flash('Game not found', 'error')
        return redirect(url_for('join_game'))
    
    # Get game data
    game_data = games_db[game_id]
    
    # Check if user has joined this game
    user_has_joined = user_email in game_data['players']
    
    # Get list of players
    players_data = []
    for player_email in game_data['players']:
        player_data = users_db.get(player_email, {})
        player_username = player_data.get('username', 'Unknown')
        
        players_data.append({
            "username": player_username,
            "status": "host" if player_email == game_data['host_email'] else "player",
            "avatar": player_data.get('profile_pic'),
            "last_active": "Just now" if player_email == user_email else "Online"
        })
    
    # Add some fake players to simulate a fuller game
    if len(players_data) < 3 and game_id == "fantasy-123":
        players_data.extend([
            {"username": "ElvenRanger", "status": "player", "avatar": None, "last_active": "5 minutes ago"},
            {"username": "WizardOfTheCoast", "status": "player", "avatar": None, "last_active": "2 minutes ago"}
        ])
    
    # Sample chat messages
    chat_messages = [
        {"username": game_data['host'], "message": f"Welcome to {game_data['title']}!", "timestamp": "10 minutes ago"},
    ]
    
    # Add some fake chat messages
    if game_id == "fantasy-123":
        chat_messages.extend([
            {"username": "ElvenRanger", "message": "My character is ready with bow drawn!", "timestamp": "8 minutes ago"},
            {"username": "WizardOfTheCoast", "message": "I've prepared my spells. Let's hope we don't need them all.", "timestamp": "5 minutes ago"},
        ])
    
    # Add a message from the current user if they just joined
    if user_has_joined:
        user_already_in_chat = any(msg['username'] == username for msg in chat_messages)
        if not user_already_in_chat:
            chat_messages.append({
                "username": username, 
                "message": "Just joined! Excited to play.", 
                "timestamp": "Just now"
            })
    
    return render_template('game.html', 
                          game=game_data, 
                          players=players_data, 
                          chat_messages=chat_messages,
                          username=username,
                          user_has_joined=user_has_joined)

# User Profile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_email = session.get('user_id')
    user_data = users_db.get(user_email, {})
    
    if request.method == 'POST':
        # Update user profile information
        username = request.form.get('username')
        bio = request.form.get('bio')
        location = request.form.get('location')
        favorite_genre = request.form.get('favorite_genre')
        
        # Validate username
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('profile.html', user=user_data)
        
        # Check if username is taken by another user
        if username != user_data['username']:
            for email, data in users_db.items():
                if email != user_email and data['username'] == username:
                    flash('Username already taken', 'error')
                    return render_template('profile.html', user=user_data)
        
        # Handle profile picture upload
        if 'profile_pic' in request.files and request.files['profile_pic'].filename:
            file = request.files['profile_pic']
            # In a real application, you would save this to a file system or cloud storage
            # For this demo, we'll encode it to base64 and store it in memory
            file_data = file.read()
            file_type = file.content_type
            encoded_pic = base64.b64encode(file_data).decode('utf-8')
            users_db[user_email]['profile_pic'] = f"data:{file_type};base64,{encoded_pic}"
        
        # Update user data
        users_db[user_email]['username'] = username
        users_db[user_email]['bio'] = bio
        users_db[user_email]['location'] = location
        users_db[user_email]['favorite_genre'] = favorite_genre
        
        # Update session with new username
        session['username'] = username
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user_data)

# Create Game page with form processing
@app.route('/create-game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        # In a real application, you would save the game data to a database
        # For this demo, we'll just redirect to a sample game page
        
        # Generate a unique game ID based on the title and theme
        game_title = request.form.get('game_title', 'New Game')
        game_theme = request.form.get('theme', 'fantasy')
        game_id = f"{game_theme}-{hash(game_title) % 1000}"
        
        flash('Game created successfully!', 'success')
        return redirect(url_for('game_page', game_id=game_id))
        
    return render_template('create_game.html', username=session.get('username'))

# Join Game page
@app.route('/join-game')
@login_required
def join_game():
    return render_template('join_game.html', username=session.get('username'))

# List all users (admin feature)
@app.route('/users')
@login_required
def list_users():
    # Check if current user is admin
    if session.get('user_id') != "admin@narrativechaos.com":
        flash('Access denied: Admin privileges required', 'error')
        return redirect(url_for('dashboard'))
    
    user_list = []
    for email, data in users_db.items():
        user_list.append({
            'email': email,
            'username': data['username'],
            'join_date': data.get('join_date', 'Unknown')
        })
    
    return render_template('users.html', users=user_list)

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
        .card {
            background-color: #16213e;
            border: none;
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #7b2cbf;
        }
        .stat-label {
            color: #9d4edd;
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
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card stat-card">
                        <div class="stat-number">{{ user_count }}</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card stat-card">
                        <div class="stat-number">0</div>
                        <div class="stat-label">Your Stories</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card stat-card">
                        <div class="stat-number">{{ join_date }}</div>
                        <div class="stat-label">Member Since</div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">Your Storytelling Journey</div>
                        <div class="card-body">
                            <h3>Welcome to Narrative Chaos</h3>
                            <p>This is where your creative journey begins. You can create new stories, continue working on drafts, or explore the community's shared narratives.</p>
                            <p>Start by clicking on "Create New Story" below to begin your first narrative adventure.</p>
                            <button class="btn btn-primary">Create New Story</button>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">Quick Actions</div>
                        <div class="card-body">
                            <div class="list-group">
                                <a href="{{ url_for('create_game') }}" class="list-group-item list-group-item-action bg-dark text-white border-secondary">Create Game</a>
                                <a href="{{ url_for('join_game') }}" class="list-group-item list-group-item-action bg-purple text-white border-secondary" style="background-color: #7b2cbf;">Join Game</a>
                                <a href="{{ url_for('profile') }}" class="list-group-item list-group-item-action bg-dark text-white border-secondary">Edit Profile</a>
                                {% if session.get('user_id') == 'admin@narrativechaos.com' %}
                                <a href="{{ url_for('list_users') }}" class="list-group-item list-group-item-action bg-danger text-white">Admin: User Management</a>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ENHANCED Template for register.html with improved validation
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
            margin-bottom: 50px;
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
        .form-text {
            color: #9d4edd;
            font-size: 0.8rem;
        }
        .password-requirements {
            background-color: #0f3460;
            border-radius: 5px;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            font-size: 0.85rem;
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
                            <input type="text" class="form-control" id="username" name="username" required minlength="3">
                            <div class="form-text">Choose a unique username (minimum 3 characters)</div>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                            <div class="form-text">We'll never share your email with anyone else</div>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required minlength="8">
                            <div class="password-requirements">
                                <div class="fw-bold mb-1">Password requirements:</div>
                                <ul class="mb-0 ps-3">
                                    <li>Minimum 8 characters long</li>
                                    <li>Recommended: Mix of letters, numbers, and symbols</li>
                                </ul>
                            </div>
                        </div>
                        <div class="mb-4">
                            <label for="confirm_password" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
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

# Template for game.html
@app.route('/template/game')
def game_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - {{ game.title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #1a1a2e;
            color: #ffffff;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .game-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 1rem;
        }
        .header {
            background-color: #16213e;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .navbar-brand {
            color: #7b2cbf;
            font-weight: bold;
        }
        .welcome-message {
            color: #9d4edd;
        }
        .main-content {
            display: flex;
            flex: 1;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .story-area {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .sidebar {
            width: 300px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .card {
            background-color: #16213e;
            border: none;
            border-radius: 10px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        .story-display {
            flex: 1;
            padding: 1rem;
            background-color: #16213e;
            border-radius: 10px;
            overflow-y: auto;
            min-height: 300px;
            line-height: 1.6;
            white-space: pre-wrap;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        .fantasy-theme {
            background-color: #182848;
            background-image: linear-gradient(135deg, #182848 0%, #4b6cb7 100%);
        }
        .scifi-theme {
            background-color: #000428;
            background-image: linear-gradient(135deg, #000428 0%, #004e92 100%);
        }
        .mystery-theme {
            background-color: #200122;
            background-image: linear-gradient(135deg, #200122 0%, #6f0000 100%);
        }
        .horror-theme {
            background-color: #16222A;
            background-image: linear-gradient(135deg, #16222A 0%, #3A6073 100%);
        }
        .editor-container {
            position: relative;
            min-height: 150px;
        }
        .story-editor {
            width: 100%;
            min-height: 150px;
            padding: 1rem;
            background-color: #0f3460;
            color: white;
            border: 1px solid #1f4287;
            border-radius: 10px;
            resize: vertical;
            font-family: inherit;
            line-height: 1.6;
        }
        .story-editor:focus {
            outline: none;
            border-color: #7b2cbf;
            box-shadow: 0 0 0 0.25rem rgba(123, 44, 191, 0.25);
        }
        .editor-controls {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
        }
        .editor-status {
            font-size: 0.9rem;
            color: #9d4edd;
        }
        .btn-purple {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
            color: white;
        }
        .btn-purple:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
            color: white;
        }
        .btn-outline-purple {
            color: #7b2cbf;
            border-color: #7b2cbf;
        }
        .btn-outline-purple:hover {
            background-color: #7b2cbf;
            color: white;
        }
        .typing-indicator {
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: #9d4edd;
            font-style: italic;
            font-size: 0.9rem;
            display: none;
        }
        .player-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .player-item {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #1f4287;
        }
        .player-item:last-child {
            border-bottom: none;
        }
        .player-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 0.75rem;
            background-color: #0f3460;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9d4edd;
            font-size: 1.2rem;
        }
        .player-info {
            flex: 1;
        }
        .player-name {
            font-weight: bold;
            color: white;
            margin: 0;
        }
        .player-status {
            font-size: 0.8rem;
            color: #9d4edd;
            margin: 0;
        }
        .host-badge {
            background-color: #7b2cbf;
            color: white;
            font-size: 0.7rem;
            padding: 0.1rem 0.4rem;
            border-radius: 10px;
            margin-left: 0.5rem;
        }
        .current-user {
            color: #7b2cbf;
        }
        .chat-messages {
            height: 250px;
            overflow-y: auto;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .chat-message {
            margin-bottom: 0.75rem;
        }
        .chat-sender {
            font-weight: bold;
        }
        .chat-timestamp {
            font-size: 0.7rem;
            color: #9d4edd;
            margin-left: 0.5rem;
        }
        .chat-input {
            display: flex;
            gap: 0.5rem;
        }
        .chat-input input {
            flex: 1;
            background-color: #0f3460;
            border: 1px solid #1f4287;
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
        }
        .chat-input input:focus {
            outline: none;
            border-color: #7b2cbf;
        }
        .tooltip-icon {
            color: #9d4edd;
            cursor: pointer;
        }
        /* Collaborative editing indicators */
        .editor-cursor {
            position: absolute;
            width: 2px;
            height: 20px;
            background-color: #ff0000;
            animation: blink 1s infinite;
        }
        .editor-cursor::after {
            content: attr(data-user);
            position: absolute;
            top: -18px;
            left: 0;
            white-space: nowrap;
            font-size: 10px;
            background-color: #ff0000;
            color: white;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .cursor-elven {
            background-color: #00ff00;
        }
        .cursor-elven::after {
            background-color: #00ff00;
            color: black;
        }
        .cursor-wizard {
            background-color: #0000ff;
        }
        .cursor-wizard::after {
            background-color: #0000ff;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="header d-flex justify-content-between align-items-center">
            <div>
                <span class="navbar-brand">Narrative Chaos</span>
                <span class="ms-3 text-light">{{ game.title }}</span>
            </div>
            <div>
                <span class="welcome-message me-3">{{ username }}</span>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        {% if not user_has_joined %}
        <div class="join-game-banner mb-3 p-4 text-center rounded" style="background-color: #0f3460;">
            <h4>You haven't joined this game yet</h4>
            <p>Join this game to participate in the collaborative storytelling experience.</p>
            <button id="join-game-btn" class="btn btn-purple btn-lg" data-game-id="{{ game.id }}">Join Game</button>
        </div>
        {% endif %}
        
        <div class="main-content">
            <div class="story-area">
                <div class="card mb-3">
                    <div class="card-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>Story</div>
                            <div>
                                <span class="badge bg-purple me-2">{{ game.difficulty }}</span>
                                <span class="badge bg-info">{{ game.players|length }}/{{ game.max_players }} Players</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div class="story-display {{ game.theme }}-theme" id="story-display">{{ game.current_content }}</div>
                    </div>
                </div>
                
                <div class="editor-container">
                    <textarea class="story-editor" id="story-editor" placeholder="Continue the story..."></textarea>
                    <div class="typing-indicator" id="typing-indicator">Someone is typing...</div>
                    
                    <!-- Simulated collaborative editing cursors -->
                    <div class="editor-cursor" id="cursor-elven" data-user="ElvenRanger" style="display: none; top: 40px; left: 120px;"></div>
                    <div class="editor-cursor cursor-elven" id="cursor-wizard" data-user="WizardOfTheCoast" style="display: none; top: 60px; left: 80px;"></div>
                    
                    <div class="editor-controls">
                        <div class="editor-status">
                            <i class="fas fa-info-circle tooltip-icon me-1" title="Your additions will be appended to the story"></i>
                            <span id="character-count">0 characters</span>
                        </div>
                        <div>
                            <button class="btn btn-outline-secondary me-2" id="discard-btn">Discard</button>
                            <button class="btn btn-purple" id="submit-btn">Add to Story</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="card">
                    <div class="card-header">Players ({{ players|length }})</div>
                    <div class="card-body p-0">
                        <div class="player-list">
                            {% for player in players %}
                            <div class="player-item">
                                {% if player.avatar %}
                                <img src="{{ player.avatar }}" alt="{{ player.username }}" class="player-avatar">
                                {% else %}
                                <div class="player-avatar">
                                    <i class="fas fa-user"></i>
                                </div>
                                {% endif %}
                                <div class="player-info">
                                    <p class="player-name {% if player.username == username %}current-user{% endif %}">
                                        {{ player.username }}
                                        {% if player.status == 'host' %}
                                        <span class="host-badge">Host</span>
                                        {% endif %}
                                    </p>
                                    <p class="player-status">{{ player.last_active }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <div class="card flex-grow-1 d-flex flex-column">
                    <div class="card-header">Chat</div>
                    <div class="card-body p-2 d-flex flex-column flex-grow-1">
                        <div class="chat-messages" id="chat-messages">
                            {% for message in chat_messages %}
                            <div class="chat-message">
                                <span class="chat-sender {% if message.username == username %}current-user{% endif %}">{{ message.username }}:</span>
                                <span class="chat-text">{{ message.message }}</span>
                                <span class="chat-timestamp">{{ message.timestamp }}</span>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="chat-input">
                            <input type="text" id="chat-input" placeholder="Type a message...">
                            <button class="btn btn-purple" id="send-chat-btn">Send</button>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">Game Info</div>
                    <div class="card-body">
                        <p><strong>Host:</strong> {{ game.host }}</p>
                        <p><strong>Started:</strong> {{ game.started_date }}</p>
                        <p class="mb-0">{{ game.description }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Join game functionality
            const joinGameBtn = document.getElementById('join-game-btn');
            if (joinGameBtn) {
                joinGameBtn.addEventListener('click', function() {
                    const gameId = this.getAttribute('data-game-id');
                    joinGame(gameId);
                });
            }
            
            // Story editor functionality
            const storyEditor = document.getElementById('story-editor');
            const storyDisplay = document.getElementById('story-display');
            const characterCount = document.getElementById('character-count');
            const typingIndicator = document.getElementById('typing-indicator');
            const submitBtn = document.getElementById('submit-btn');
            const discardBtn = document.getElementById('discard-btn');
            
            // Chat functionality
            const chatInput = document.getElementById('chat-input');
            const sendChatBtn = document.getElementById('send-chat-btn');
            const chatMessages = document.getElementById('chat-messages');
            
            // Collaborative cursors
            const cursorElven = document.getElementById('cursor-elven');
            const cursorWizard = document.getElementById('cursor-wizard');
            
            // Join game function
            function joinGame(gameId) {
                fetch(`/join-game/${gameId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message and reload the page
                        alert(data.message);
                        window.location.reload();
                    } else {
                        // Show error message
                        alert(data.message || 'An error occurred');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while joining the game');
                });
            }
            
            // Disable the editor if user hasn't joined
            {% if not user_has_joined %}
            if (storyEditor) {
                storyEditor.disabled = true;
                storyEditor.placeholder = "Join the game to contribute to the story...";
                
                if (submitBtn) submitBtn.disabled = true;
                if (discardBtn) discardBtn.disabled = true;
                
                const chatInput = document.getElementById('chat-input');
                const sendChatBtn = document.getElementById('send-chat-btn');
                if (chatInput) chatInput.disabled = true;
                if (sendChatBtn) sendChatBtn.disabled = true;
            }
            {% endif %}
            
            // Update character count
            if (storyEditor) {
                storyEditor.addEventListener('input', function() {
                    const count = storyEditor.value.length;
                    characterCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
                    
                    // Show typing indicator to other users (simulated)
                    if (count > 0) {
                        // In a real app, you would broadcast this to other users
                        simulateOtherUserTyping();
                    }
                });
            }
            
            // Submit story addition
            submitBtn.addEventListener('click', function() {
                if (storyEditor.value.trim() === '') return;
                
                // Add the new content to the story display
                storyDisplay.textContent += '\\n\\n' + storyEditor.value;
                
                // Scroll to the bottom of the story
                storyDisplay.scrollTop = storyDisplay.scrollHeight;
                
                // Clear the editor
                storyEditor.value = '';
                characterCount.textContent = '0 characters';
                
                // In a real app, you would send this to the server and broadcast to other users
                alert('In a real application, your addition would be saved to the database and broadcast to all users in real-time.');
                
                // Simulate other users continuing the story after a delay
                setTimeout(simulateOtherUserContribution, 5000);
            });
            
            // Discard button
            discardBtn.addEventListener('click', function() {
                storyEditor.value = '';
                characterCount.textContent = '0 characters';
            });
            
            // Chat functionality
            sendChatBtn.addEventListener('click', sendChatMessage);
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
            
            function sendChatMessage() {
                if (chatInput.value.trim() === '') return;
                
                // Create new chat message
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message';
                messageDiv.innerHTML = `
                    <span class="chat-sender current-user">${'{{ username }}'}:</span>
                    <span class="chat-text">${chatInput.value}</span>
                    <span class="chat-timestamp">Just now</span>
                `;
                
                // Add to chat and scroll to bottom
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Clear input
                chatInput.value = '';
                
                // Simulate response from another user
                setTimeout(simulateOtherUserChat, 3000);
            }
            
            // Simulate collaborative editing
            storyEditor.addEventListener('click', function(e) {
                // Calculate cursor position relative to the textarea
                const rect = storyEditor.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // In a real-time collaborative editor, you would broadcast your cursor position
                // For simulation, we'll show other users' cursors randomly
                simulateOtherUsersCursors();
            });
            
            // Show tooltips on hover
            document.querySelectorAll('[title]').forEach(el => {
                new bootstrap.Tooltip(el);
            });
            
            // Simulation functions for demonstration purposes
            function simulateOtherUserTyping() {
                // Randomly show/hide the typing indicator
                if (Math.random() > 0.7) {
                    typingIndicator.style.display = 'block';
                    
                    // Hide after a random time
                    setTimeout(() => {
                        typingIndicator.style.display = 'none';
                    }, 2000 + Math.random() * 3000);
                }
            }
            
            function simulateOtherUsersCursors() {
                // Randomly show other users' cursors
                if (Math.random() > 0.5) {
                    cursorElven.style.display = 'block';
                    cursorElven.style.top = (30 + Math.random() * 100) + 'px';
                    cursorElven.style.left = (Math.random() * 300) + 'px';
                    
                    setTimeout(() => {
                        cursorElven.style.display = 'none';
                    }, 3000 + Math.random() * 2000);
                }
                
                if (Math.random() > 0.5) {
                    cursorWizard.style.display = 'block';
                    cursorWizard.style.top = (30 + Math.random() * 100) + 'px';
                    cursorWizard.style.left = (50 + Math.random() * 300) + 'px';
                    
                    setTimeout(() => {
                        cursorWizard.style.display = 'none';
                    }, 3000 + Math.random() * 2000);
                }
            }
            
            function simulateOtherUserChat() {
                // Only respond sometimes
                if (Math.random() < 0.7) return;
                
                const responses = [
                    "I like where this story is going!",
                    "What if we introduced a new character here?",
                    "Maybe we should add a plot twist?",
                    "Great addition to the narrative!",
                    "I'm thinking of adding a mysterious artifact next."
                ];
                
                const users = ["ElvenRanger", "WizardOfTheCoast", "DungeonMaster42"];
                const randomUser = users[Math.floor(Math.random() * users.length)];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message';
                messageDiv.innerHTML = `
                    <span class="chat-sender">${randomUser}:</span>
                    <span class="chat-text">${randomResponse}</span>
                    <span class="chat-timestamp">Just now</span>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function simulateOtherUserContribution() {
                // Only contribute sometimes
                if (Math.random() < 0.5) return;
                
                const contributions = [
                    "The howl was suddenly cut short, replaced by a sound even more unsettling—silence. The party exchanged nervous glances, each member gripping their weapons tighter.",
                    ""We should turn back," whispered Elara, her voice quavering. But even as she spoke, the massive doors of the castle began to creak open, seemingly of their own accord.",
                    "Garrick reached into his pouch and extracted a small, glowing crystal. "This will guide us to the artifact," he explained, watching as the crystal pulsed with an eerie blue light that intensified when pointed towards the castle's tallest tower."
                ];
                
                const randomContribution = contributions[Math.floor(Math.random() * contributions.length)];
                const users = ["ElvenRanger", "WizardOfTheCoast", "DungeonMaster42"];
                const randomUser = users[Math.floor(Math.random() * users.length)];
                
                // Add the contribution to the story
                storyDisplay.textContent += '\\n\\n' + randomContribution;
                storyDisplay.scrollTop = storyDisplay.scrollHeight;
                
                // Add a chat message about it
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message';
                messageDiv.innerHTML = `
                    <span class="chat-sender">${randomUser}:</span>
                    <span class="chat-text">I've added to the story!</span>
                    <span class="chat-timestamp">Just now</span>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
    </script>
</body>
</html>
"""

# Template for profile.html
@app.route('/template/profile')
def profile_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - User Profile</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
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
        .card {
            background-color: #16213e;
            border: none;
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
        }
        .form-control, .form-select {
            background-color: #0f3460;
            border: 1px solid #1f4287;
            color: #ffffff;
        }
        .form-control:focus, .form-select:focus {
            background-color: #0f3460;
            border-color: #7b2cbf;
            box-shadow: 0 0 0 0.25rem rgba(123, 44, 191, 0.25);
            color: #ffffff;
        }
        .form-label {
            color: #c8c8c8;
        }
        .btn-purple {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
            color: white;
        }
        .btn-purple:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
            color: white;
        }
        .profile-picture-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
        }
        .profile-picture {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
            background-color: #0f3460;
            border: 3px solid #7b2cbf;
        }
        .profile-picture-placeholder {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background-color: #0f3460;
            border: 3px solid #7b2cbf;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            color: #9d4edd;
        }
        .profile-picture-edit {
            position: absolute;
            bottom: 0;
            right: 0;
            background-color: #7b2cbf;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border: 3px solid #16213e;
        }
        .profile-picture-edit:hover {
            background-color: #9d4edd;
        }
        .profile-picture-input {
            display: none;
        }
        .stats-card {
            background-color: #0f3460;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            text-align: center;
        }
        .stats-number {
            font-size: 2rem;
            font-weight: bold;
            color: #7b2cbf;
        }
        .stats-label {
            color: #9d4edd;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header d-flex justify-content-between align-items-center">
            <span class="navbar-brand">Narrative Chaos</span>
            <div>
                <span class="welcome-message me-3">Welcome, {{ user.username }}</span>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">Profile Summary</div>
                        <div class="card-body text-center">
                            <div class="profile-picture-container">
                                {% if user.profile_pic %}
                                <img src="{{ user.profile_pic }}" alt="Profile Picture" class="profile-picture">
                                {% else %}
                                <div class="profile-picture-placeholder">
                                    <i class="fas fa-user"></i>
                                </div>
                                {% endif %}
                                <label for="profile-pic-input" class="profile-picture-edit">
                                    <i class="fas fa-camera text-white"></i>
                                </label>
                            </div>
                            
                            <h4 class="mb-1">{{ user.username }}</h4>
                            <p class="text-muted mb-3">{{ session.get('user_id') }}</p>
                            
                            <p class="mb-1"><i class="fas fa-calendar-alt me-2 text-purple"></i> Joined: {{ user.join_date }}</p>
                            {% if user.location %}
                            <p class="mb-1"><i class="fas fa-map-marker-alt me-2 text-purple"></i> {{ user.location }}</p>
                            {% endif %}
                            
                            <div class="row mt-4">
                                <div class="col-6">
                                    <div class="stats-card">
                                        <div class="stats-number">{{ user.games_created }}</div>
                                        <div class="stats-label">Games Created</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="stats-card">
                                        <div class="stats-number">{{ user.games_joined }}</div>
                                        <div class="stats-label">Games Joined</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">Edit Profile</div>
                        <div class="card-body">
                            <form method="post" enctype="multipart/form-data">
                                <input type="file" id="profile-pic-input" name="profile_pic" accept="image/*" class="profile-picture-input">
                                
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" value="{{ user.username }}" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="bio" class="form-label">Bio</label>
                                    <textarea class="form-control" id="bio" name="bio" rows="3" placeholder="Tell us about yourself...">{{ user.bio }}</textarea>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="location" class="form-label">Location</label>
                                            <input type="text" class="form-control" id="location" name="location" value="{{ user.location }}" placeholder="City, Country">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="favorite_genre" class="form-label">Favorite Genre</label>
                                            <select class="form-select" id="favorite_genre" name="favorite_genre">
                                                <option value="" {% if not user.favorite_genre %}selected{% endif %}>Select a genre</option>
                                                <option value="Fantasy" {% if user.favorite_genre == 'Fantasy' %}selected{% endif %}>Fantasy</option>
                                                <option value="Science Fiction" {% if user.favorite_genre == 'Science Fiction' %}selected{% endif %}>Science Fiction</option>
                                                <option value="Mystery" {% if user.favorite_genre == 'Mystery' %}selected{% endif %}>Mystery</option>
                                                <option value="Horror" {% if user.favorite_genre == 'Horror' %}selected{% endif %}>Horror</option>
                                                <option value="Adventure" {% if user.favorite_genre == 'Adventure' %}selected{% endif %}>Adventure</option>
                                                <option value="Romance" {% if user.favorite_genre == 'Romance' %}selected{% endif %}>Romance</option>
                                                <option value="Historical" {% if user.favorite_genre == 'Historical' %}selected{% endif %}>Historical</option>
                                                <option value="Dystopian" {% if user.favorite_genre == 'Dystopian' %}selected{% endif %}>Dystopian</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="d-flex justify-content-between mt-4">
                                    <a href="{{ url_for('dashboard') }}" class="btn btn-outline-secondary">Cancel</a>
                                    <button type="submit" class="btn btn-purple">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">Account Settings</div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h5 class="mb-0">Change Password</h5>
                                    <p class="text-muted mb-0 small">Update your password regularly for security</p>
                                </div>
                                <button class="btn btn-outline-secondary" onclick="alert('Password change functionality would go here')">Change</button>
                            </div>
                            
                            <hr class="my-3" style="border-color: #1f4287;">
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h5 class="mb-0">Privacy Settings</h5>
                                    <p class="text-muted mb-0 small">Manage your profile visibility and data sharing</p>
                                </div>
                                <button class="btn btn-outline-secondary" onclick="alert('Privacy settings would go here')">Manage</button>
                            </div>
                            
                            <hr class="my-3" style="border-color: #1f4287;">
                            
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 class="mb-0 text-danger">Delete Account</h5>
                                    <p class="text-muted mb-0 small">Permanently delete your account and all data</p>
                                </div>
                                <button class="btn btn-outline-danger" onclick="alert('Account deletion functionality would go here')">Delete</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Handle profile picture upload
        document.getElementById('profile-pic-input').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    // If there's an existing profile picture, update it
                    let profilePic = document.querySelector('.profile-picture');
                    if (!profilePic) {
                        // If there's a placeholder, replace it with an image
                        const placeholder = document.querySelector('.profile-picture-placeholder');
                        if (placeholder) {
                            placeholder.parentNode.innerHTML = '<img src="' + event.target.result + '" alt="Profile Picture" class="profile-picture">';
                        }
                    } else {
                        // Update existing image
                        profilePic.src = event.target.result;
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    </script>
</body>
</html>
"""

# Template for create_game.html
@app.route('/template/create_game')
def create_game_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - Create Game</title>
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
        .card {
            background-color: #16213e;
            border: none;
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
        }
        .form-section {
            margin-bottom: 30px;
        }
        .form-control, .form-select {
            background-color: #0f3460;
            border: 1px solid #1f4287;
            color: #ffffff;
        }
        .form-control:focus, .form-select:focus {
            background-color: #0f3460;
            border-color: #7b2cbf;
            box-shadow: 0 0 0 0.25rem rgba(123, 44, 191, 0.25);
            color: #ffffff;
        }
        .form-label {
            color: #c8c8c8;
        }
        .form-text {
            color: #9d4edd;
        }
        .form-check-input:checked {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
        }
        .btn-purple {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
            color: white;
        }
        .btn-purple:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
            color: white;
        }
        .theme-preview {
            width: 100%;
            height: 100px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .theme-preview:hover {
            transform: scale(1.05);
        }
        .fantasy {
            background: linear-gradient(135deg, #4b6cb7, #182848);
        }
        .scifi {
            background: linear-gradient(135deg, #000428, #004e92);
        }
        .mystery {
            background: linear-gradient(135deg, #200122, #6f0000);
        }
        .horror {
            background: linear-gradient(135deg, #16222A, #3A6073);
        }
        .custom-file-upload {
            border: 1px dashed #7b2cbf;
            border-radius: 5px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            margin-top: 10px;
        }
        .custom-file-upload:hover {
            background-color: rgba(123, 44, 191, 0.1);
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header d-flex justify-content-between align-items-center">
            <span class="navbar-brand">Narrative Chaos</span>
            <div>
                <span class="welcome-message me-3">Welcome, {{ username }}</span>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">Create a New Game</div>
                        <div class="card-body">
                            <form action="{{ url_for('create_game') }}" method="post">
                                <div class="form-section">
                                    <h4 class="mb-3">Game Details</h4>
                                    <div class="mb-3">
                                        <label for="game-title" class="form-label">Game Title</label>
                                        <input type="text" class="form-control" id="game-title" name="game_title" placeholder="Enter a captivating title" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="game-description" class="form-label">Game Description</label>
                                        <textarea class="form-control" id="game-description" name="game_description" rows="4" placeholder="Describe your game's setting, theme, and what players can expect..." required></textarea>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <h4 class="mb-3">Game Settings</h4>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="game-type" class="form-label">Game Type</label>
                                                <select class="form-select" id="game-type" name="game_type" required>
                                                    <option value="" selected disabled>Select a game type</option>
                                                    <option value="collaborative">Collaborative Story</option>
                                                    <option value="branching">Branching Narrative</option>
                                                    <option value="roleplay">Character Roleplay</option>
                                                    <option value="adventure">Interactive Adventure</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="difficulty" class="form-label">Difficulty Level</label>
                                                <select class="form-select" id="difficulty" name="difficulty" required>
                                                    <option value="" selected disabled>Select difficulty</option>
                                                    <option value="easy">Easy - Beginner Friendly</option>
                                                    <option value="moderate">Moderate - Some Experience Needed</option>
                                                    <option value="hard">Hard - Challenging Experience</option>
                                                    <option value="expert">Expert - For Veterans Only</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="max-players" class="form-label">Maximum Players</label>
                                                <select class="form-select" id="max-players" name="max_players" required>
                                                    <option value="2">2 Players</option>
                                                    <option value="4" selected>4 Players</option>
                                                    <option value="6">6 Players</option>
                                                    <option value="8">8 Players</option>
                                                    <option value="10">10 Players</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="visibility" class="form-label">Game Visibility</label>
                                                <select class="form-select" id="visibility" name="visibility" required>
                                                    <option value="public" selected>Public - Anyone can join</option>
                                                    <option value="private">Private - Invite only (with code)</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <h4 class="mb-3">Theme & Visuals</h4>
                                    <p class="text-muted">Choose a theme for your game or upload custom artwork</p>
                                    
                                    <div class="row mb-4">
                                        <div class="col-md-3">
                                            <div class="form-check">
                                                <input class="form-check-input visually-hidden" type="radio" name="theme" id="fantasy-theme" value="fantasy" checked>
                                                <label class="form-check-label w-100" for="fantasy-theme">
                                                    <div class="theme-preview fantasy">Fantasy</div>
                                                </label>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="form-check">
                                                <input class="form-check-input visually-hidden" type="radio" name="theme" id="scifi-theme" value="scifi">
                                                <label class="form-check-label w-100" for="scifi-theme">
                                                    <div class="theme-preview scifi">Sci-Fi</div>
                                                </label>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="form-check">
                                                <input class="form-check-input visually-hidden" type="radio" name="theme" id="mystery-theme" value="mystery">
                                                <label class="form-check-label w-100" for="mystery-theme">
                                                    <div class="theme-preview mystery">Mystery</div>
                                                </label>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="form-check">
                                                <input class="form-check-input visually-hidden" type="radio" name="theme" id="horror-theme" value="horror">
                                                <label class="form-check-label w-100" for="horror-theme">
                                                    <div class="theme-preview horror">Horror</div>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="custom-artwork" name="custom_artwork">
                                            <label class="form-check-label" for="custom-artwork">
                                                Use custom artwork
                                            </label>
                                        </div>
                                        
                                        <div class="custom-file-upload">
                                            <input type="file" id="artwork-upload" name="artwork" class="d-none">
                                            <label for="artwork-upload">
                                                <i class="fa fa-cloud-upload"></i> Click to upload game artwork
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <h4 class="mb-3">Advanced Options</h4>
                                    <div class="mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="auto-moderate" name="auto_moderate" checked>
                                            <label class="form-check-label" for="auto-moderate">
                                                Enable content moderation
                                            </label>
                                            <div class="form-text">Automatically filter inappropriate content</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="ai-npcs" name="ai_npcs">
                                            <label class="form-check-label" for="ai-npcs">
                                                Include AI NPCs
                                            </label>
                                            <div class="form-text">Add AI-controlled non-player characters to your story</div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="mature-content" name="mature_content">
                                            <label class="form-check-label" for="mature-content">
                                                Allow mature themes
                                            </label>
                                            <div class="form-text">Game will be marked as suitable for adults only</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="d-flex justify-content-between mt-4">
                                    <a href="{{ url_for('dashboard') }}" class="btn btn-outline-secondary">Cancel</a>
                                    <button type="submit" class="btn btn-purple">Create Game</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Template for join_game.html
@app.route('/template/join_game')
def join_game_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - Join Game</title>
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
        .card {
            background-color: #16213e;
            border: none;
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
        }
        .game-card {
            background-color: #1f4287;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .game-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        }
        .game-title {
            color: #7b2cbf;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .game-host {
            color: #9d4edd;
            font-style: italic;
        }
        .game-description {
            margin: 15px 0;
        }
        .game-stats {
            display: flex;
            justify-content: space-between;
            color: #9d4edd;
            font-size: 0.9rem;
        }
        .btn-purple {
            background-color: #7b2cbf;
            border-color: #7b2cbf;
            color: white;
        }
        .btn-purple:hover {
            background-color: #9d4edd;
            border-color: #9d4edd;
            color: white;
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
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header d-flex justify-content-between align-items-center">
            <span class="navbar-brand">Narrative Chaos</span>
            <div>
                <span class="welcome-message me-3">Welcome, {{ username }}</span>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">Join a Narrative Game</div>
                        <div class="card-body">
                            <p>Enter a game code to join a private game, or browse available public games below.</p>
                            
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <form action="#" method="post">
                                        <div class="input-group">
                                            <input type="text" class="form-control" placeholder="Enter game code" aria-label="Game code">
                                            <button class="btn btn-purple" type="submit">Join Private Game</button>
                                        </div>
                                    </form>
                                </div>
                                <div class="col-md-6 text-md-end mt-3 mt-md-0">
                                    <button class="btn btn-outline-secondary me-2">Refresh List</button>
                                    <a href="{{ url_for('create_game') }}" class="btn btn-outline-purple" style="border-color: #7b2cbf; color: #7b2cbf;">Create New Game</a>
                                </div>
                            </div>
                            
                            <h4 class="mb-3">Public Games</h4>
                            
                            <!-- Example game cards -->
                            <div class="game-card">
                                <div class="game-title">The Forgotten Realms: Adventure Awaits</div>
                                <div class="game-host">Hosted by: DungeonMaster42</div>
                                <div class="game-description">
                                    A fantasy adventure set in a world of magic and mystery. Join forces with other players to explore dungeons, battle mythical creatures, and uncover ancient treasures.
                                </div>
                                <div class="game-stats mb-3">
                                    <span>Players: 3/6</span>
                                    <span>Difficulty: Moderate</span>
                                    <span>Started: 2 days ago</span>
                                </div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-success">Accepting Players</span>
                                    <a href="{{ url_for('game_page', game_id='fantasy-123') }}" class="btn btn-purple">Join Game</a>
                                </div>
                            </div>
                            
                            <div class="game-card">
                                <div class="game-title">Space Odyssey: The Final Frontier</div>
                                <div class="game-host">Hosted by: CaptainKirk</div>
                                <div class="game-description">
                                    Set in the distant future, this sci-fi narrative puts you in command of a starship exploring uncharted territories. Face alien civilizations, navigate interstellar politics, and make decisions that will shape the fate of the galaxy.
                                </div>
                                <div class="game-stats mb-3">
                                    <span>Players: 2/4</span>
                                    <span>Difficulty: Hard</span>
                                    <span>Started: Just now</span>
                                </div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-success">Accepting Players</span>
                                    <a href="{{ url_for('game_page', game_id='scifi-456') }}" class="btn btn-purple">Join Game</a>
                                </div>
                            </div>
                            
                            <div class="game-card">
                                <div class="game-title">Detective Chronicles: The Missing Heir</div>
                                <div class="game-host">Hosted by: SherlockHolmes</div>
                                <div class="game-description">
                                    A murder mystery set in 1920s London. As private investigators, players must solve the case of a missing heir to a fortune. Interview suspects, find clues, and piece together the truth before it's too late.
                                </div>
                                <div class="game-stats mb-3">
                                    <span>Players: 5/5</span>
                                    <span>Difficulty: Moderate</span>
                                    <span>Started: 1 week ago</span>
                                </div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-danger">Full</span>
                                    <button class="btn btn-secondary" disabled>Game Full</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Template for users.html (admin page)
@app.route('/template/users')
def users_template():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Narrative Chaos - User Management</title>
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
        .card {
            background-color: #16213e;
            border: none;
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #0f3460;
            color: #9d4edd;
            font-weight: bold;
        }
        .table {
            color: white;
        }
        .table th {
            color: #9d4edd;
        }
        .admin-badge {
            background-color: #7b2cbf;
            color: white;
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            border-radius: 10px;
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header d-flex justify-content-between align-items-center">
            <span class="navbar-brand">Narrative Chaos</span>
            <div>
                <span class="welcome-message me-3">Welcome, {{ session.get('username') }}</span>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
        
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <span>User Management</span>
                                <span class="badge bg-danger">Admin Only</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-dark table-hover">
                                    <thead>
                                        <tr>
                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Join Date</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for user in users %}
                                        <tr>
                                            <td>
                                                {{ user.username }}
                                                {% if user.email == 'admin@narrativechaos.com' %}
                                                <span class="admin-badge">Admin</span>
                                                {% endif %}
                                            </td>
                                            <td>{{ user.email }}</td>
                                            <td>{{ user.join_date }}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-info">View</button>
                                                {% if user.email != 'admin@narrativechaos.com' %}
                                                <button class="btn btn-sm btn-outline-warning">Edit</button>
                                                <button class="btn btn-sm btn-outline-danger">Delete</button>
                                                {% endif %}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
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
        
    with open(templates_dir / 'users.html', 'w') as f:
        f.write(users_template())
        
    with open(templates_dir / 'join_game.html', 'w') as f:
        f.write(join_game_template())
        
    with open(templates_dir / 'create_game.html', 'w') as f:
        f.write(create_game_template())
        
    with open(templates_dir / 'profile.html', 'w') as f:
        f.write(profile_template())
        
    with open(templates_dir / 'game.html', 'w') as f:
        f.write(game_template())
    
    # Run the app
    app.run(debug=True)
