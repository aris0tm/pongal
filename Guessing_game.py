from flask import Flask, render_template_string, request, session, redirect, url_for
from akinator import Client
from akinator.exceptions import CantGoBackAnyFurther
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# File to store user information
USER_DATA_FILE = 'user_data.json'

def save_user_info(user_info):
    """Save user information to a JSON file"""
    try:
        # Load existing data
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Add timestamp
        user_info['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Append new user
        data.append(user_info)
        
        # Save back to file
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving user data: {e}")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mind Reader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        body.fullscreen {
            display: flex;
            align-items: stretch;
            padding: 0;
        }
        
        body.centered {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideIn 0.5s ease;
        }
        
        .container.fullscreen {
            width: 100%;
            height: 100vh;
            border-radius: 0;
            display: flex;
            flex-direction: column;
        }
        
        .container.centered {
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .info-container {
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .brain-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            margin-bottom: 15px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #555;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        
        input[type="text"],
        input[type="tel"],
        input[type="hidden"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        input[type="text"]:focus,
        input[type="tel"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            display: inline-block;
            padding: 15px 30px;
            border: none;
            border-radius: 15px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 20px;
            margin-bottom: 30px;
        }

        .welcome-card h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .welcome-card p {
            font-size: 1.2em;
            opacity: 0.95;
        }

        .welcome-icon {
            font-size: 60px;
            margin-bottom: 20px;
        }
        
        .how-to-play {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .how-to-play h2 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .how-to-play p {
            color: #666;
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .theme-selector {
            margin-bottom: 30px;
        }
        
        .theme-selector h3 {
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .theme-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        
        .btn-theme {
            padding: 20px;
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .btn-theme:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .btn-theme.active {
            border-color: #667eea;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        
        .theme-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .theme-name {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        
        .child-mode-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            border-radius: 15px;
            margin-bottom: 25px;
            cursor: pointer;
        }
        
        .toggle-switch {
            position: relative;
            width: 60px;
            height: 30px;
            background: #ccc;
            border-radius: 15px;
            transition: background 0.3s;
        }
        
        .toggle-switch.active {
            background: #4caf50;
        }
        
        .toggle-slider {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s;
        }
        
        .toggle-switch.active .toggle-slider {
            transform: translateX(30px);
        }
        
        .toggle-label {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        
        .game-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 30px;
            overflow: hidden;
        }
        
        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            border-radius: 20px;
        }
        
        .user-info-display {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .user-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .user-details {
            text-align: left;
        }
        
        .user-name {
            font-weight: 700;
            color: #333;
            font-size: 1.1em;
        }
        
        .institution {
            color: #666;
            font-size: 0.9em;
        }
        
        .game-stats {
            text-align: right;
        }
        
        .step-counter {
            font-size: 1.5em;
            font-weight: 700;
            color: #667eea;
        }
        
        .step-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .game-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
        }
        
        .question-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 50px 40px;
            border-radius: 25px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .question-text {
            font-size: 2em;
            color: white;
            font-weight: 600;
            line-height: 1.4;
        }
        
        .progress-section {
            margin-bottom: 30px;
        }
        
        .progress-bar {
            width: 100%;
            height: 12px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
        }
        
        .progress-text {
            text-align: center;
            color: #666;
            font-size: 1em;
            font-weight: 600;
        }
        
        .answer-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        
        .answer-grid.two-col {
            grid-template-columns: repeat(2, 1fr);
            max-width: 500px;
            margin: 0 auto;
        }
        
        .btn-answer {
            padding: 25px 20px;
            border: none;
            border-radius: 20px;
            font-size: 1.15em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        
        .btn-yes {
            background: #4caf50;
        }
        
        .btn-yes:hover {
            background: #45a049;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
        }
        
        .btn-no {
            background: #f44336;
        }
        
        .btn-no:hover {
            background: #da190b;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(244, 67, 54, 0.4);
        }
        
        .btn-idk {
            background: #9e9e9e;
        }
        
        .btn-idk:hover {
            background: #757575;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(158, 158, 158, 0.4);
        }
        
        .btn-probably {
            background: #2196f3;
        }
        
        .btn-probably:hover {
            background: #0b7dda;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(33, 150, 243, 0.4);
        }
        
        .btn-probably-not {
            background: #ff9800;
        }
        
        .btn-probably-not:hover {
            background: #e68900;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255, 152, 0, 0.4);
        }
        
        .btn-back {
            background: #9c27b0;
        }
        
        .btn-back:hover {
            background: #7b1fa2;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(156, 39, 176, 0.4);
        }
        
        .btn-back:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .result-card {
            text-align: center;
        }
        
        .result-image {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            object-fit: cover;
            border: 5px solid #667eea;
            margin: 20px auto;
            display: block;
        }
        
        .result-name {
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .result-description {
            color: #666;
            font-size: 1.2em;
            margin-bottom: 20px;
        }
        
        .result-message {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            white-space: pre-line;
            line-height: 1.6;
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #c62828;
        }
        
        .sparkle {
            font-size: 60px;
            margin-bottom: 20px;
        }

        .guess-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }

        .guess-content {
            max-width: 700px;
            width: 100%;
        }
    </style>
</head>
<body class="{% if stage == 'game' or stage == 'guess' %}fullscreen{% else %}centered{% endif %}">
    <div class="container {% if stage == 'game' or stage == 'guess' %}fullscreen{% else %}centered{% endif %}">
        {% if stage == 'info' %}
        <div class="info-container">
            <div class="header">
                <div class="brain-icon">🧠</div>
                <h1>Mind Reader</h1>
                <p class="subtitle">Think of a Anything, I'll read your mind!</p>
            </div>
            
            <form method="POST" action="{{ url_for('start_game') }}">
                <div class="form-group">
                    <label for="name">👤 Name</label>
                    <input type="text" id="name" name="name" placeholder="Your name" required>
                </div>
                
                <div class="form-group">
                    <label for="phone">📱 Phone Number</label>
                    <input type="tel" id="phone" name="phone" placeholder="Phone number" required>
                </div>
                
                <div class="form-group">
                    <label for="institution">🏫 Institution</label>
                    <input type="text" id="institution" name="institution" placeholder="School/College name" required>
                </div>
                
                <button type="submit" class="btn btn-primary">Continue</button>
            </form>
        </div>

        {% elif stage == 'welcome' %}
        <div class="info-container">
            <div class="welcome-card">
                <div class="welcome-icon">👋</div>
                <h2>Welcome, {{ user_info.name }}!</h2>
                <p>Get ready for an amazing experience</p>
            </div>
            
            <div class="how-to-play">
                <h2>How to Play</h2>
                <p>
                    Think of any character, animal, or object in your mind.<br>
                    Answer my questions honestly.<br>
                    I will try to guess what you're thinking!
                </p>
            </div>

            <form method="POST" action="{{ url_for('begin_game') }}" id="welcomeForm">
                <div class="theme-selector">
                    <h3>Choose a Theme</h3>
                    <div class="theme-buttons">
                        <div class="btn-theme active" onclick="selectTheme('c', event)">
                            <div class="theme-icon">🧑</div>
                            <div class="theme-name">Characters</div>
                        </div>
                        <div class="btn-theme" onclick="selectTheme('a', event)">
                            <div class="theme-icon">🦁</div>
                            <div class="theme-name">Animals</div>
                        </div>
                        <div class="btn-theme" onclick="selectTheme('o', event)">
                            <div class="theme-icon">🎨</div>
                            <div class="theme-name">Objects</div>
                        </div>
                    </div>
                </div>
                
                <div class="child-mode-toggle" onclick="toggleChildMode()">
                    <span class="toggle-label">Child-Safe Mode</span>
                    <div class="toggle-switch" id="childModeToggle">
                        <div class="toggle-slider"></div>
                    </div>
                </div>
                
                <input type="hidden" name="theme" id="themeInput" value="c">
                <input type="hidden" name="child_mode" id="childModeInput" value="false">
                
                <button type="submit" class="btn btn-primary">Start Playing 🎮</button>
            </form>
        </div>
        
        <script>
            function selectTheme(theme, event) {
                event.preventDefault();
                document.querySelectorAll('.btn-theme').forEach(btn => {
                    btn.classList.remove('active');
                });
                event.currentTarget.classList.add('active');
                document.getElementById('themeInput').value = theme;
            }
            
            function toggleChildMode() {
                const toggle = document.getElementById('childModeToggle');
                const input = document.getElementById('childModeInput');
                const isActive = toggle.classList.contains('active');
                
                if (isActive) {
                    toggle.classList.remove('active');
                    input.value = 'false';
                } else {
                    toggle.classList.add('active');
                    input.value = 'true';
                }
            }
        </script>
        
        {% elif stage == 'game' %}
        <div class="game-container">
            <div class="game-header">
                <div class="user-info-display">
                    <div class="user-avatar">👤</div>
                    <div class="user-details">
                        <div class="user-name">{{ user_info.name }}</div>
                        <div class="institution">{{ user_info.institution }}</div>
                    </div>
                </div>
                <div class="game-stats">
                    <div class="step-counter">Q{{ step + 1 }}</div>
                    <div class="step-label">{{ progression|round }}%</div>
                </div>
            </div>
            
            <div class="game-content">
                <div class="question-box">
                    <div class="question-text">{{ question }}</div>
                </div>
                
                <div class="progress-section">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ progression }}%;"></div>
                    </div>
                    <div class="progress-text">Progress: {{ progression|round }}%</div>
                </div>
                
                {% if error %}
                <div class="error-message">{{ error }}</div>
                {% endif %}
                
                <form method="POST" action="{{ url_for('answer') }}">
                    <div class="answer-grid">
                        <button type="submit" name="answer" value="y" class="btn-answer btn-yes">✓ Yes</button>
                        <button type="submit" name="answer" value="n" class="btn-answer btn-no">✗ No</button>
                        <button type="submit" name="answer" value="i" class="btn-answer btn-idk">? Don't Know</button>
                        <button type="submit" name="answer" value="p" class="btn-answer btn-probably">Probably</button>
                        <button type="submit" name="answer" value="pn" class="btn-answer btn-probably-not">Probably Not</button>
                        <button type="submit" name="answer" value="b" class="btn-answer btn-back" {% if step == 0 %}disabled{% endif %}>← Back</button>
                    </div>
                </form>
            </div>
        </div>
        
        {% elif stage == 'guess' %}
        <div class="guess-container">
            <div class="guess-content">
                <div class="header">
                    <div class="sparkle">✨</div>
                    <h1>I think I found it!</h1>
                </div>
                
                <div class="result-card">
                    {% if guess.photo %}
                    <img src="{{ guess.photo }}" alt="{{ guess.name }}" class="result-image" onerror="this.style.display='none'">
                    {% endif %}
                    <div class="result-name">{{ guess.name }}</div>
                    <div class="result-description">{{ guess.description }}</div>
                </div>
                
                <p style="text-align: center; font-size: 1.3em; margin-bottom: 25px; color: #333;">Is this your character?</p>
                
                <form method="POST" action="{{ url_for('answer') }}">
                    <div class="answer-grid two-col">
                        <button type="submit" name="answer" value="y" class="btn-answer btn-yes">✓ Yes, that's it!</button>
                        <button type="submit" name="answer" value="n" class="btn-answer btn-no">✗ No, try again</button>
                    </div>
                </form>
            </div>
        </div>
        
        {% elif stage == 'finished' %}
        <div class="info-container">
            <div class="result-card">
                <div class="sparkle">{% if win %}🎉{% else %}🏆{% endif %}</div>
                <h1>{% if win %}I Found It!{% else %}You Won!{% endif %}</h1>
                
                {% if photo %}
                <img src="{{ photo }}" alt="{{ name }}" class="result-image" onerror="this.style.display='none'">
                {% endif %}
                
                {% if name %}
                <div class="result-name">{{ name }}</div>
                {% endif %}
                
                {% if description %}
                <div class="result-description">{{ description }}</div>
                {% endif %}
                
                <div class="result-message">{{ final_message }}</div>
                
                <a href="{{ url_for('index') }}" class="btn btn-primary">Play Again</a>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    session.clear()
    return render_template_string(HTML_TEMPLATE, stage='info')

@app.route('/start', methods=['POST'])
def start_game():
    user_info = {
        'name': request.form['name'],
        'phone': request.form['phone'],
        'institution': request.form['institution']
    }
    session['user_info'] = user_info
    save_user_info(user_info)
    
    return render_template_string(HTML_TEMPLATE, 
        stage='welcome',
        user_info=user_info
    )

@app.route('/begin', methods=['POST'])
def begin_game():
    if 'user_info' not in session:
        return redirect(url_for('index'))
    
    # Get theme and child_mode from form
    theme = request.form.get('theme', 'c')
    child_mode = request.form.get('child_mode', 'false') == 'true'
    
    client = Client()
    try:
        # Start game with selected theme and child_mode
        client.start_game(language='en', theme=theme, child_mode=child_mode)
        
        session['question'] = client.question
        session['step'] = client.step
        session['progression'] = client.progression
        session['session_id'] = client.session_id
        session['signature'] = client.signature
        session['identifiant'] = client.identifiant
        session['language'] = client.language
        session['theme'] = client.theme
        session['child_mode'] = client.child_mode
        
        return redirect(url_for('game'))
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, stage='info', error=str(e))

@app.route('/game')
def game():
    if 'user_info' not in session:
        return redirect(url_for('index'))
    
    if session.get('win') and not session.get('finished'):
        return render_template_string(HTML_TEMPLATE, 
            stage='guess',
            user_info=session['user_info'],
            guess=session.get('guess', {}),
            error=session.pop('error', None)
        )
    
    if session.get('finished'):
        return render_template_string(HTML_TEMPLATE,
            stage='finished',
            win=session.get('win', False),
            name=session.get('name'),
            description=session.get('description'),
            photo=session.get('photo'),
            final_message=session.get('final_message', '')
        )
    
    return render_template_string(HTML_TEMPLATE,
        stage='game',
        user_info=session['user_info'],
        question=session.get('question', ''),
        step=session.get('step', 0),
        progression=session.get('progression', 0),
        error=session.pop('error', None)
    )

@app.route('/answer', methods=['POST'])
def answer():
    if 'user_info' not in session:
        return redirect(url_for('index'))
    
    answer_value = request.form['answer']
    
    if answer_value == 'b':
        return handle_back()
    
    client = Client()
    client.session_id = session['session_id']
    client.signature = session['signature']
    client.identifiant = session['identifiant']
    client.language = session['language']
    client.theme = session['theme']
    client.child_mode = session['child_mode']
    client.question = session['question']
    client.step = session['step']
    client.progression = session['progression']
    client.win = session.get('win', False)
    client.finished = session.get('finished', False)
    
    if session.get('win'):
        client.id_proposition = session.get('id_proposition', '')
        client.name_proposition = session.get('name_proposition', '')
        client.description_proposition = session.get('description_proposition', '')
        client.photo = session.get('photo', '')
        client.pseudo = session.get('pseudo', '')
        client.flag_photo = session.get('flag_photo', '')
        client.step_last_proposition = session.get('step_last_proposition', 0)
    
    try:
        client.answer(answer_value)
        
        session['question'] = str(client)
        session['step'] = client.step
        session['progression'] = client.progression
        session['finished'] = client.finished
        session['win'] = client.win
        
        if client.win and not client.finished:
            session['guess'] = {
                'name': client.name_proposition,
                'description': client.description_proposition,
                'photo': client.photo,
                'pseudo': client.pseudo
            }
            session['id_proposition'] = client.id_proposition
            session['name_proposition'] = client.name_proposition
            session['description_proposition'] = client.description_proposition
            session['photo'] = client.photo
            session['pseudo'] = client.pseudo
            session['flag_photo'] = client.flag_photo
            session['step_last_proposition'] = client.step
        
        if client.finished:
            session['final_message'] = client.question
            if client.photo:
                session['photo'] = client.photo
                session['name'] = client.name_proposition
                session['description'] = client.description_proposition
        
        return redirect(url_for('game'))
        
    except Exception as e:
        session['error'] = str(e)
        return redirect(url_for('game'))

def handle_back():
    client = Client()
    client.session_id = session['session_id']
    client.signature = session['signature']
    client.identifiant = session['identifiant']
    client.language = session['language']
    client.theme = session['theme']
    client.child_mode = session['child_mode']
    client.question = session['question']
    client.step = session['step']
    client.progression = session['progression']
    client.win = session.get('win', False)
    
    try:
        client.back()
        
        session['question'] = client.question
        session['step'] = client.step
        session['progression'] = client.progression
        session['win'] = False
        session.pop('guess', None)
        
        return redirect(url_for('game'))
    except CantGoBackAnyFurther:
        session['error'] = "You can't go back any further!"
        return redirect(url_for('game'))
    except Exception as e:
        session['error'] = str(e)
        return redirect(url_for('game'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)