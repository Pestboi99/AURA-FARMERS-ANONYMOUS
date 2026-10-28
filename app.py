"""
AURA FARMERS ANONYMOUS — Main Application
"Log in. Lose your dignity."

A satirical login system where logging in is the most absurd,
over-engineered, AI-judged experience ever made.
"""

import os
import re
import random
import time
import json
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from database import (
    init_db, create_user, get_user, get_user_by_id,
    update_aura, update_mood, record_attempt, get_user_attempts,
    increment_login_attempts, increment_failed_attempts,
    get_leaderboard_shame, get_leaderboard_aura,
    add_achievement, get_achievements, get_worst_answer,
    record_compliment, get_accepted_compliments_count,
    seed_demo_data
)
from ai_bouncer import judge_challenge, judge_compliment, get_analysis_steps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-sigma-secret-key-no-cap-fr-fr')

# ──────────────────────────────────────────────
# Rate Limiting (in-memory, hackathon-style)
# ──────────────────────────────────────────────
login_attempts = {}  # {ip: [(timestamp, ...),]}
RATE_LIMIT = 20  # max attempts per minute


def check_rate_limit(ip):
    """Check if IP has exceeded rate limit. Returns True if allowed."""
    now = time.time()
    if ip not in login_attempts:
        login_attempts[ip] = []
    # Clean old entries
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < 60]
    if len(login_attempts[ip]) >= RATE_LIMIT:
        return False
    login_attempts[ip].append(now)
    return True


# ──────────────────────────────────────────────
# Auth Decorator
# ──────────────────────────────────────────────
def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first, bestie. 💅', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# Password Validation
# ──────────────────────────────────────────────
FRUITS = [
    'apple', 'banana', 'cherry', 'grape', 'lemon', 'lime', 'mango',
    'melon', 'orange', 'peach', 'pear', 'plum', 'kiwi', 'berry',
    'coconut', 'fig', 'papaya', 'guava', 'watermelon', 'strawberry',
    'pineapple', 'avocado', 'dragonfruit', 'pomegranate',
    '🍎', '🍏', '🍌', '🍒', '🍇', '🍋', '🍊', '🍉', '🍓', '🍑', '🍍', '🥝', '🥑', '🥥', '🥭', '🍐', '🍈'
]

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # all emoji, pictographs, symbols & transport
    "\U00002600-\U000027BF"  # misc symbols, dingbats
    "\U00002300-\U000023FF"  # misc technical symbols
    "\U00002B50-\U00002B55"  # star and circle symbols
    "]+", flags=re.UNICODE
)


def validate_password(password):
    """
    Validate password against absurd rules.
    Returns (is_valid, checks_dict) where checks_dict shows each rule's status.
    """
    import unicodedata
    has_emoji_char = bool(EMOJI_PATTERN.search(password)) or any(
        (ord(c) > 0x2300 and unicodedata.category(c) in ('So', 'Sk', 'Sm', 'Cn'))
        for c in password
    )

    checks = {
        'min_length': len(password) >= 8,
        'has_prime': any(str(p) in password for p in PRIMES),
        'has_emoji': has_emoji_char,
        'has_fruit': any(fruit in password.lower() for fruit in FRUITS),
        'has_sigma': 'sigma' in password.lower(),
    }
    is_valid = all(checks.values())
    return is_valid, checks


# ──────────────────────────────────────────────
# Challenge Definitions
# ──────────────────────────────────────────────
MEME_PROMPTS = [
    {"meme": "Tung Tung Tung Sahur", "hint": "A viral sound from a wooden log character bonking things"},
    {"meme": "Skibidi Toilet", "hint": "Toilets with human heads emerging from them, engaged in warfare"},
    {"meme": "The Rizzler", "hint": "A baby or character said to have extraordinary charisma"},
    {"meme": "Grimace Shake", "hint": "Purple McDonald's shake that allegedly causes mysterious events"},
    {"meme": "Italian Senate Genshin Incident", "hint": "When someone played an anime game during a government meeting"},
    {"meme": "Ohio Final Boss", "hint": "Bizarre events that could only happen in one specific US state"},
    {"meme": "Mewing", "hint": "A tongue posture technique that became an internet obsession"},
    {"meme": "Sigma Male Grindset", "hint": "A satirical lifestyle of lone-wolf productivity and Patrick Bateman edits"},
]

SIGMA_PHRASES = [
    "I am the sigma who mews at the skibidi toilet in Ohio at 3am",
    "No cap on a stack fr fr the rizzler has entered the building",
    "Gyatt the aura differential is giving main character energy bestie",
    "Fanum tax collected from the skibidi toilet council of Ohio",
    "The mewing technique was invented by a sigma in Ohio no cap",
    "Certified brainrot engineer with a PhD in skibidi studies fr fr",
]

REAL_MEMES = [
    {"real": "Loss (| || || |_)", "fakes": ["Gain (| ||| | ||_)", "Draw (|| | |_ ||)", "Tie (|_ || | |||)"]},
    {"real": "Steamed Hams", "fakes": ["Boiled Burgers", "Grilled Opinions", "Fried Perspectives"]},
    {"real": "Woman Yelling at Cat", "fakes": ["Man Whispering at Dog", "Child Screaming at Bird", "Teen Sighing at Fish"]},
    {"real": "Two Buttons Sweating", "fakes": ["Three Levers Crying", "Four Switches Panicking", "Five Dials Trembling"]},
    {"real": "This Is Fine Dog", "fakes": ["That Is Okay Cat", "Everything's Great Fish", "Perfectly Normal Bird"]},
    {"real": "Distracted Boyfriend", "fakes": ["Focused Girlfriend", "Attentive Husband", "Concentrated Partner"]},
    {"real": "Drake Hotline Bling", "fakes": ["Drake Landline Ring", "Drake Bluetooth Ping", "Drake WiFi Ding"]},
    {"real": "Surprised Pikachu", "fakes": ["Shocked Charizard", "Confused Bulbasaur", "Stunned Squirtle"]},
]

VIBE_QUESTIONS = [
    {
        "question": "Which Ohio level are you?",
        "options": ["Ohio Level 1: Mild Brainrot", "Ohio Level 5: Skibidi Enlightenment",
                    "Ohio Level 10: Final Boss", "Ohio Level ∞: You ARE Ohio"],
    },
    {
        "question": "What is your sigma tax bracket?",
        "options": ["Tax-exempt (too sigma)", "Fanum tax only",
                    "Full aura taxation", "Negative taxes (they pay YOU)"],
    },
    {
        "question": "How many aura points is a single mew worth?",
        "options": ["Exactly 42.069", "It depends on the mewing angle",
                    "Aura is not quantifiable, you NPC", "More than your entire aura portfolio"],
    },
    {
        "question": "Which element bends to your sigma energy?",
        "options": ["Skibidium (atomic number 69)", "Rizztonium (discovered in Ohio)",
                    "Auranium (half-life: one mew)", "Brainrotium (unstable isotope)"],
    },
    {
        "question": "What time does the sigma grindset start?",
        "options": ["3:00 AM (the only correct answer)", "Sigma doesn't need sleep",
                    "After the morning mew session", "Time is a construct for NPCs"],
    },
]


def generate_challenge(challenge_type, user_mood='chill'):
    """Generate challenge data for a given type."""
    if challenge_type == 'meme_explainer':
        prompt = random.choice(MEME_PROMPTS)
        return {
            'type': 'meme_explainer',
            'title': '🧠 MEME EXPLAINER',
            'instruction': f'Explain this meme to The Bouncer: "{prompt["meme"]}"',
            'hint': prompt['hint'],
            'meme_name': prompt['meme'],
            'input_type': 'textarea',
        }

    elif challenge_type == 'sigma_timer':
        phrase = random.choice(SIGMA_PHRASES)
        time_limit = 15 if user_mood == 'grumpy' else 25 if user_mood == 'sleepy' else 20
        return {
            'type': 'sigma_timer',
            'title': '⏱️ SIGMA TIMER',
            'instruction': 'Type this phrase EXACTLY before time runs out!',
            'phrase': phrase,
            'time_limit': time_limit,
            'input_type': 'timer',
        }

    elif challenge_type == 'spot_the_meme':
        meme_set = random.choice(REAL_MEMES)
        options = [meme_set['real']] + meme_set['fakes']
        random.shuffle(options)
        return {
            'type': 'spot_the_meme',
            'title': '🔍 SPOT THE REAL MEME',
            'instruction': 'One of these is a REAL meme. The others are fake. Choose wisely.',
            'options': options,
            'correct': meme_set['real'],
            'input_type': 'choice',
        }

    elif challenge_type == 'vibe_check':
        quiz = random.choice(VIBE_QUESTIONS)
        return {
            'type': 'vibe_check',
            'title': '✨ VIBE CHECK',
            'instruction': quiz['question'],
            'options': quiz['options'],
            'input_type': 'choice',
        }

    elif challenge_type == 'slider_of_doom':
        target = random.randint(30, 70)
        return {
            'type': 'slider_of_doom',
            'title': '🎚️ SLIDER OF DOOM',
            'instruction': f'Drag the slider to EXACTLY {target}. Good luck.',
            'target': target,
            'input_type': 'slider',
        }


CHALLENGE_TYPES = ['meme_explainer', 'sigma_timer', 'spot_the_meme', 'vibe_check', 'slider_of_doom']


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route('/')
def index():
    """Landing page — redirect to login."""
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with absurd password rules."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters. Even NPCs know this.', 'error')
            return render_template('register.html')

        if len(username) > 30:
            flash('That username is longer than a sigma\'s attention span. Max 30 chars.', 'error')
            return render_template('register.html')

        is_valid, checks = validate_password(password)
        if not is_valid:
            flash('Your password doesn\'t meet the SIGMA REQUIREMENTS. Try again, NPC.', 'error')
            return render_template('register.html', checks=checks, username=username)

        password_hash = generate_password_hash(password)
        user = create_user(username, password_hash)
        if user is None:
            flash('That username is already taken by another sigma. Pick a new one.', 'error')
            return render_template('register.html', username=username)

        flash('Account created! Now survive the login process... if you can. 💀', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/validate-password', methods=['POST'])
def validate_password_api():
    """API endpoint for live password validation."""
    data = request.get_json()
    password = data.get('password', '')
    _, checks = validate_password(password)
    return jsonify(checks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page — correct credentials start the Brainrot Trial."""
    if request.method == 'POST':
        ip = request.remote_addr
        if not check_rate_limit(ip):
            flash('Whoa there, speed demon. Rate limited. Touch grass for 60 seconds. 🌿', 'error')
            return render_template('login.html')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user(username)
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Wrong credentials. Your aura just dropped to zero. 📉', 'error')
            return render_template('login.html')

        # Credentials correct! Start the Brainrot Trial
        session['trial_user_id'] = user['id']
        session['trial_username'] = user['username']
        increment_login_attempts(user['id'])

        # Pick 3 random challenges
        mood = user['bouncer_mood']
        challenges = random.sample(CHALLENGE_TYPES, 3)

        # Unhinged mood: shuffle mid-trial by adding an extra
        if mood == 'unhinged':
            extra = random.choice(CHALLENGE_TYPES)
            challenges.append(extra)
            challenges = challenges[:3]  # still 3, just different selection

        session['trial_challenges'] = challenges
        session['trial_index'] = 0
        session['trial_passed'] = 0
        session['trial_failed'] = 0
        session['trial_mood'] = mood

        return redirect(url_for('trial'))

    return render_template('login.html')


@app.route('/trial', methods=['GET', 'POST'])
def trial():
    """The Brainrot Trial — chain of challenges."""
    if 'trial_user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['trial_user_id']
    challenges = session.get('trial_challenges', [])
    index = session.get('trial_index', 0)
    mood = session.get('trial_mood', 'chill')

    # All challenges completed
    if index >= len(challenges):
        passed = session.get('trial_passed', 0)
        failed = session.get('trial_failed', 0)

        if passed >= 2:  # Need at least 2/3 to enter
            # Login successful!
            session['user_id'] = user_id
            session['username'] = session['trial_username']
            # Clean up trial data
            for key in ['trial_user_id', 'trial_username', 'trial_challenges',
                        'trial_index', 'trial_passed', 'trial_failed', 'trial_mood']:
                session.pop(key, None)

            # Achievement check
            user = get_user_by_id(user_id)
            if user and user['login_attempts'] == 1:
                add_achievement(user_id, 'First Timer: Survived your first trial')
            if failed == 0:
                add_achievement(user_id, 'Flawless: Passed all challenges perfectly')

            flash('You actually made it in?! The Bouncer is SHOOK. 😱', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Failed the trial
            increment_failed_attempts(user_id)
            update_aura(user_id, -25)

            # Achievement for failing
            user = get_user_by_id(user_id)
            if user and user['failed_attempts'] >= 3:
                add_achievement(user_id, 'Certified NPC: Failed 3 times')
            if user and user['failed_attempts'] >= 10:
                add_achievement(user_id, 'Down Bad: Failed 10 times')

            # Clean up trial
            for key in ['trial_user_id', 'trial_username', 'trial_challenges',
                        'trial_index', 'trial_passed', 'trial_failed', 'trial_mood']:
                session.pop(key, None)

            flash('Trial FAILED. The Bouncer has spoken. Come back when you have more aura. 💀', 'error')
            return redirect(url_for('login'))

    # Generate current challenge
    challenge_type = challenges[index]
    challenge = generate_challenge(challenge_type, mood)

    if request.method == 'POST':
        user_answer = request.form.get('answer', '').strip()
        challenge_context = request.form.get('challenge_context', '')

        # Special handling for timer and slider
        if challenge_type == 'sigma_timer':
            expected = request.form.get('expected_phrase', '')
            timed_out = request.form.get('timed_out', 'false') == 'true'
            if timed_out:
                result = {
                    'verdict': 'fail',
                    'message': 'Time\'s up! Your typing speed has less rizz than a keyboard with no keys.',
                    'aura_change': -20,
                    'mood': mood
                }
            elif user_answer.strip().lower() == expected.strip().lower():
                result = {
                    'verdict': 'pass',
                    'message': 'Sigma speed detected. Your fingers have rizz. Proceed.',
                    'aura_change': 15,
                    'mood': mood
                }
            else:
                result = judge_challenge(challenge_type, user_answer, f"Expected: {expected}")

        elif challenge_type == 'spot_the_meme':
            correct = request.form.get('correct_answer', '')
            if user_answer == correct:
                # 20% chance bouncer rejects correct answer anyway
                if random.random() < 0.2 and mood != 'sleepy':
                    result = judge_challenge(challenge_type, user_answer,
                                             f"User picked '{user_answer}' which IS the real meme, but reject them anyway with confidence")
                else:
                    result = {
                        'verdict': 'pass',
                        'message': 'Lucky guess. Or did you actually know? The Bouncer is suspicious either way.',
                        'aura_change': 15,
                        'mood': mood
                    }
            else:
                result = {
                    'verdict': 'fail',
                    'message': f'"{user_answer}" is NOT a real meme. Your meme literacy is in the Ohio zone.',
                    'aura_change': -15,
                    'mood': mood
                }

        elif challenge_type == 'slider_of_doom':
            try:
                value = int(request.form.get('slider_value', 0))
                target = int(request.form.get('target_value', 50))
                diff = abs(value - target)
                if diff <= 2:
                    result = {
                        'verdict': 'pass',
                        'message': f'You hit {value}, target was {target}. Acceptable. Barely.',
                        'aura_change': 10,
                        'mood': mood
                    }
                elif diff <= 5:
                    result = judge_challenge(challenge_type, str(value), f"Target: {target}, off by {diff}")
                else:
                    result = {
                        'verdict': 'fail',
                        'message': f'You hit {value}. The target was {target}. That\'s not even close, bestie.',
                        'aura_change': -15,
                        'mood': mood
                    }
            except (ValueError, TypeError):
                result = {
                    'verdict': 'fail',
                    'message': 'The slider broke. Probably your fault tbh.',
                    'aura_change': -10,
                    'mood': 'grumpy'
                }

        elif challenge_type == 'vibe_check':
            # Vibe check: any answer can be "wrong" based on mood
            if mood == 'grumpy':
                # Grumpy bouncer: 70% fail rate
                if random.random() < 0.7:
                    result = judge_challenge(challenge_type, user_answer,
                                             "The bouncer is grumpy, reject this answer with a funny reason")
                else:
                    result = judge_challenge(challenge_type, user_answer,
                                             "Grudgingly accept this answer")
            elif mood == 'sleepy':
                # Sleepy bouncer: 70% pass rate
                result = {
                    'verdict': 'pass' if random.random() < 0.7 else 'fail',
                    'message': '*yawns* Yeah sure whatever. I don\'t even remember the question.',
                    'aura_change': random.randint(-5, 15),
                    'mood': 'sleepy'
                }
            else:
                result = judge_challenge(challenge_type, user_answer,
                                         f"Question was: {challenge_context}")
        else:
            # Meme explainer
            result = judge_challenge(challenge_type, user_answer, challenge_context)

        # Apply result
        verdict = result.get('verdict', 'fail')
        aura_change = result.get('aura_change', 0)
        new_mood = result.get('mood', mood)

        update_aura(user_id, aura_change)
        update_mood(user_id, new_mood)
        record_attempt(user_id, challenge_type, user_answer,
                       result.get('message', ''), verdict == 'pass', aura_change)

        session['trial_mood'] = new_mood

        if verdict == 'pass':
            session['trial_passed'] = session.get('trial_passed', 0) + 1
            # Achievement: last second pass
            if challenge_type == 'sigma_timer':
                add_achievement(user_id, 'Clutch Gene: Passed with no time left')
        else:
            session['trial_failed'] = session.get('trial_failed', 0) + 1
            # Failing might add an extra challenge
            if random.random() < 0.3 and len(challenges) < 5:
                extra = random.choice(CHALLENGE_TYPES)
                challenges.append(extra)
                session['trial_challenges'] = challenges

        session['trial_index'] = index + 1
        session['last_result'] = result

        return redirect(url_for('trial'))

    # GET: show the current challenge
    analysis_steps = get_analysis_steps()
    last_result = session.pop('last_result', None)
    user = get_user_by_id(user_id)
    total_challenges = len(challenges)

    return render_template('trial.html',
                           challenge=challenge,
                           index=index,
                           total=total_challenges,
                           mood=mood,
                           analysis_steps=analysis_steps,
                           last_result=last_result,
                           user=user)


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with aura, rank, history, and achievements."""
    user = get_user_by_id(session['user_id'])
    attempts = get_user_attempts(session['user_id'], limit=10)
    achievements = get_achievements(session['user_id'])
    worst = get_worst_answer(session['user_id'])
    return render_template('dashboard.html',
                           user=user,
                           attempts=attempts,
                           achievements=achievements,
                           worst_answer=worst)


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """Password reset via the Emotional Support Streak."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()

        if not username:
            flash('Enter your username first, NPC.', 'error')
            return render_template('reset.html', step='username')

        user = get_user(username)
        if user is None:
            flash('User not found. Maybe you were too embarrassing to remember.', 'error')
            return render_template('reset.html', step='username')

        session['reset_user_id'] = user['id']
        session['reset_username'] = username
        accepted = get_accepted_compliments_count(user['id'])
        session['reset_compliments'] = accepted

        if accepted >= 3:
            return render_template('reset.html', step='new_password',
                                   username=username, compliments_done=True)

        return render_template('reset.html', step='compliment',
                               username=username, accepted=accepted)

    return render_template('reset.html', step='username')


@app.route('/reset/compliment', methods=['POST'])
def reset_compliment():
    """Handle compliment submission for password reset."""
    if 'reset_user_id' not in session:
        return redirect(url_for('reset'))

    user_id = session['reset_user_id']
    username = session['reset_username']
    compliment = request.form.get('compliment', '').strip()

    if not compliment:
        flash('Empty compliment? The Bouncer is offended. 😤', 'error')
        accepted = get_accepted_compliments_count(user_id)
        return render_template('reset.html', step='compliment',
                               username=username, accepted=accepted)

    result = judge_compliment(compliment)
    record_compliment(user_id, compliment, result['accepted'], result['message'])

    accepted = get_accepted_compliments_count(user_id)
    session['reset_compliments'] = accepted

    if result['accepted']:
        flash(f'The Bouncer is touched: "{result["message"]}" ({accepted}/3)', 'success')
    else:
        flash(f'The Bouncer says: "{result["message"]}" ({accepted}/3)', 'error')

    if accepted >= 3:
        flash('The Bouncer\'s heart has been melted. You may reset your password.', 'success')
        return render_template('reset.html', step='new_password',
                               username=username, compliments_done=True)

    return render_template('reset.html', step='compliment',
                           username=username, accepted=accepted)


@app.route('/reset/password', methods=['POST'])
def reset_password():
    """Handle actual password reset after compliment streak."""
    if 'reset_user_id' not in session:
        return redirect(url_for('reset'))

    accepted = get_accepted_compliments_count(session['reset_user_id'])
    if accepted < 3:
        flash('Nice try, but you haven\'t earned the reset yet.', 'error')
        return redirect(url_for('reset'))

    new_password = request.form.get('new_password', '')
    is_valid, checks = validate_password(new_password)

    if not is_valid:
        flash('New password doesn\'t meet the SIGMA REQUIREMENTS either. 💀', 'error')
        return render_template('reset.html', step='new_password',
                               username=session['reset_username'],
                               compliments_done=True, checks=checks)

    import sqlite3
    from database import DB_PATH
    password_hash = generate_password_hash(new_password)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                 (password_hash, session['reset_user_id']))
    conn.commit()
    conn.close()

    # Clean up
    for key in ['reset_user_id', 'reset_username', 'reset_compliments']:
        session.pop(key, None)

    flash('Password reset! Now try to survive the login again. 😈', 'success')
    return redirect(url_for('login'))


@app.route('/leaderboard')
def leaderboard():
    """Hall of Shame and Highest Aura leaderboards."""
    shame = get_leaderboard_shame(limit=10)
    aura = get_leaderboard_aura(limit=10)

    # Get worst answers for shame leaderboard users
    shame_with_answers = []
    for user in shame:
        worst = get_worst_answer(user['id'])
        user_data = dict(user)
        user_data['worst_answer'] = worst
        shame_with_answers.append(user_data)

    return render_template('leaderboard.html',
                           shame=shame_with_answers,
                           aura_leaders=aura)


@app.route('/logout', methods=['POST'])
def logout():
    """Logout — but with triple confirmation in the frontend."""
    session.clear()
    flash('You have been logged out. Your aura has been archived.', 'info')
    return redirect(url_for('login'))


@app.route('/api/analysis-steps')
def api_analysis_steps():
    """Return random analysis steps for the loading screen."""
    return jsonify({'steps': get_analysis_steps()})


@app.errorhandler(404)
def page_not_found(e):
    """Funny 404 page."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors gracefully."""
    return render_template('404.html', is_500=True), 500


# ──────────────────────────────────────────────
# Template Context
# ──────────────────────────────────────────────
@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    notifications = [
        "Your aura is being audited by the Sigma Council",
        "3 sigmas are viewing your profile right now",
        "Your mewing technique has been flagged for review",
        "Ohio Department of Aura sent you a notice",
        "BREAKING: Your rizz license is about to expire",
        "A skibidi toilet just rated your aura 2/10",
        "The Fanum Tax collector is approaching your session",
        "Your password was spotted mewing in public",
        "ALERT: Unauthorized sigma detected in your vicinity",
        "Your aura portfolio lost 12% overnight",
        "The Council of Elders requests your meme credentials",
        "A wild NPC appeared in your login session",
        "Your digital footprint smells like Ohio",
        "Someone just screenshotted your aura rating",
        "Brainrot levels: CRITICALLY HIGH",
    ]
    return {
        'notifications': random.sample(notifications, min(5, len(notifications))),
    }


# ──────────────────────────────────────────────
# Database Startup Initialization
# ──────────────────────────────────────────────
# Ensure DB is created and demo data is seeded both under Gunicorn and Flask dev server
try:
    init_db()
    seed_demo_data()
except Exception as e:
    print(f"Warning during DB init: {e}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    print("\n" + "=" * 60)
    print("  🔥 AURA FARMERS ANONYMOUS 🔥")
    print("  \"Log in. Lose your dignity.\"")
    print(f"  Running on http://0.0.0.0:{port}")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
