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
    'pineapple', 'avocado', 'dragonfruit', 'pomegranate', 'blueberry',
    'raspberry', 'blackberry', 'apricot', 'tomato', 'citrus',
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
    if not password:
        return False, {
            'min_length': False,
            'has_prime': False,
            'has_emoji': False,
            'has_fruit': False,
            'has_sigma': False,
        }

    import unicodedata
    has_emoji_char = bool(EMOJI_PATTERN.search(password)) or any(
        (ord(c) > 0x2300 and unicodedata.category(c) in ('So', 'Sk', 'Sm', 'Cn'))
        for c in password
    )

    # Count length: allow 8 characters OR 8 bytes in UTF-8 (handling multi-byte emojis)
    min_length_pass = len(password) >= 6 or len(password.encode('utf-8')) >= 8

    # Prime check: any prime number or the word 'prime'
    has_prime_pass = any(str(p) in password for p in PRIMES) or ('prime' in password.lower())

    # Fruit check: any fruit name or fruit emoji
    has_fruit_pass = any(fruit in password.lower() for fruit in FRUITS)

    # Sigma check: case-insensitive
    has_sigma_pass = 'sigma' in password.lower()

    checks = {
        'min_length': min_length_pass,
        'has_prime': has_prime_pass,
        'has_emoji': has_emoji_char,
        'has_fruit': has_fruit_pass,
        'has_sigma': has_sigma_pass,
    }
    is_valid = all(checks.values())
    return is_valid, checks


# ──────────────────────────────────────────────
# Brainrot Captcha System
# ──────────────────────────────────────────────
BRAINROT_CAPTCHA_CHALLENGES = [
    'npc_grid',        # Select all squares with sigma energy
    'runaway_checkbox', # Checkbox that runs from cursor
    'mewing_timer',    # Hold button for exactly 3.69s
    'brainrot_math',   # Solve math in brainrot units
    'rizz_unscramble', # Unscramble a brainrot phrase
]

NPC_GRID_ITEMS = [
    # (emoji, label, is_sigma)
    ('🗿', 'Mewing Stone', True),
    ('👑', 'Sigma Crown', True),
    ('🐺', 'Lone Wolf', True),
    ('💎', 'Grindset Gem', True),
    ('🏋️', 'Gym Gains', True),
    ('😈', 'Demon Mode', True),
    ('🔥', 'Sigma Flame', True),
    ('⚡', 'Rizz Lightning', True),
    ('🤡', 'NPC Clown', False),
    ('🐑', 'Sheep Follower', False),
    ('😴', 'Sleepy Beta', False),
    ('📱', 'Doomscroller', False),
    ('🍕', 'Pizza NPC', False),
    ('🪑', 'Sitting Andy', False),
    ('🧸', 'Teddy Beta', False),
    ('🐌', 'Slow Grinder', False),
    ('🎮', 'Gamer NPC', False),
    ('🍿', 'Watcher NPC', False),
    ('💤', 'Lazy Beta', False),
    ('🤖', 'Literal NPC', False),
]

BRAINROT_MATH_PROBLEMS = [
    {'question': 'If 1 skibidi = 3 aura points, and 1 fanum tax = 2 skibidis, how many aura points is 2 fanum taxes?', 'answer': 12},
    {'question': 'A sigma mews 7 times per hour. How many mews in a 3-hour grindset session?', 'answer': 21},
    {'question': 'You start with 100 aura. Ohio steals 42. A mewing session restores 17. What\'s your aura?', 'answer': 75},
    {'question': 'If rizzler has 5x more charisma than an NPC, and NPCs have 3 charisma, what\'s the rizzler\'s total?', 'answer': 15},
    {'question': 'Tung Tung hits 4 bonks/sec. Sahur lasts 6 seconds. How many total bonks?', 'answer': 24},
    {'question': 'A skibidi toilet recruits 2 toilets daily. Starting from 1, how many after 3 days? (including original)', 'answer': 8},
    {'question': 'Sigma grindset: wake at 3AM, sleep at 11PM. How many hours of grind?', 'answer': 20},
    {'question': 'If you lose 5 aura per L and gain 10 per W, after 3 Ws and 4 Ls, what\'s your net aura?', 'answer': 10},
]

RIZZ_PHRASES = [
    {'scrambled': 'dibikis letoit', 'answer': 'skibidi toilet'},
    {'scrambled': 'het zzirler', 'answer': 'the rizzler'},
    {'scrambled': 'giams laem', 'answer': 'sigma male'},
    {'scrambled': 'namuf xat', 'answer': 'fanum tax'},
    {'scrambled': 'tung tung ruahs', 'answer': 'tung tung sahur'},
    {'scrambled': 'ihoo nifal sobs', 'answer': 'ohio final boss'},
    {'scrambled': 'gniwem chnqtieue', 'answer': 'mewing technique'},
    {'scrambled': 'raua mfarres', 'answer': 'aura farmers'},
]


def generate_captcha_challenge(challenge_type):
    """Generate a captcha challenge for registration."""
    if challenge_type == 'npc_grid':
        # Pick 9 items for a 3x3 grid, ensuring 2-4 are sigma
        sigma_items = [i for i in NPC_GRID_ITEMS if i[2]]
        npc_items = [i for i in NPC_GRID_ITEMS if not i[2]]
        n_sigma = random.randint(2, 4)
        n_npc = 9 - n_sigma
        chosen_sigma = random.sample(sigma_items, min(n_sigma, len(sigma_items)))
        chosen_npc = random.sample(npc_items, min(n_npc, len(npc_items)))
        grid = chosen_sigma + chosen_npc
        random.shuffle(grid)
        correct_indices = [i for i, item in enumerate(grid) if item[2]]
        return {
            'type': 'npc_grid',
            'title': '🗿 SELECT ALL SIGMA ENERGY',
            'instruction': 'Select ALL squares that contain SIGMA energy. Miss one and you\'re an NPC.',
            'grid': [{'emoji': item[0], 'label': item[1], 'index': i} for i, item in enumerate(grid)],
            'correct_indices': correct_indices,
        }

    elif challenge_type == 'runaway_checkbox':
        return {
            'type': 'runaway_checkbox',
            'title': '☑️ PROVE YOU\'RE NOT AN NPC',
            'instruction': 'Click the checkbox. It might not want to be clicked though... 😈',
        }

    elif challenge_type == 'mewing_timer':
        target = random.choice([3.00, 3.50, 4.00, 2.80])
        tolerance = 0.70
        return {
            'type': 'mewing_timer',
            'title': '🗿 MEWING PRECISION TEST',
            'instruction': f'Hold the MEW button for {target} seconds (±{tolerance}s). Release when confident in your mewing posture!',
            'target_time': target,
            'tolerance': tolerance,
        }

    elif challenge_type == 'brainrot_math':
        problem = random.choice(BRAINROT_MATH_PROBLEMS)
        return {
            'type': 'brainrot_math',
            'title': '🧮 BRAINROT MATHEMATICS',
            'instruction': problem['question'],
            'answer': problem['answer'],
        }

    elif challenge_type == 'rizz_unscramble':
        phrase = random.choice(RIZZ_PHRASES)
        return {
            'type': 'rizz_unscramble',
            'title': '🔀 UNSCRAMBLE THE RIZZ',
            'instruction': f'Unscramble this brainrot phrase:',
            'scrambled': phrase['scrambled'],
            'answer': phrase['answer'],
        }


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
    """Registration page with absurd password rules and brainrot captcha."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # If captcha was already completed, skip validation and create account
        if session.get('captcha_completed'):
            pending_username = session.pop('pending_username', username)
            pending_hash = session.pop('pending_password_hash', generate_password_hash(password))
            # Clean up all captcha state
            for key in ['captcha_completed', 'captcha_challenges', 'captcha_index',
                        'captcha_passed', 'captcha_failed', 'current_captcha']:
                session.pop(key, None)

            user = create_user(pending_username, pending_hash)
            if user is None:
                flash('That username is already taken by another sigma. Pick a new one.', 'error')
                return render_template('register.html', username=pending_username)

            flash('Account created! You survived the CAPTCHA GAUNTLET. Now survive the login... if you can. 💀', 'success')
            return redirect(url_for('login'))

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters. Even NPCs know this.', 'error')
            return render_template('register.html')

        if len(username) > 30:
            flash('That username is longer than a sigma\'s attention span. Max 30 chars.', 'error')
            return render_template('register.html')

        is_valid, checks = validate_password(password)
        if not is_valid:
            flash('Your password doesn\'t meet the SIGMA REQUIREMENTS. Try again, NPC.', 'error')
            return render_template('register.html', checks=checks, username=username, password=password)

        # Store credentials and start captcha gauntlet
        session['pending_username'] = username
        session['pending_password_hash'] = generate_password_hash(password)
        # Pick 3 random captcha challenges
        captcha_challenges = random.sample(BRAINROT_CAPTCHA_CHALLENGES, 3)
        session['captcha_challenges'] = captcha_challenges
        session['captcha_index'] = 0
        session['captcha_passed'] = 0
        session['captcha_failed'] = 0
        session['captcha_completed'] = False

        # Generate first challenge
        challenge = generate_captcha_challenge(captcha_challenges[0])
        session['current_captcha'] = challenge

        return render_template('register.html',
                               captcha_mode=True,
                               captcha=challenge,
                               captcha_index=0,
                               captcha_total=3,
                               username=username)


    # Clean up any stale captcha state on fresh GET
    for key in ['captcha_challenges', 'captcha_index', 'captcha_passed',
                'captcha_failed', 'captcha_completed', 'current_captcha',
                'pending_username', 'pending_password_hash']:
        session.pop(key, None)

    return render_template('register.html')


@app.route('/validate-password', methods=['POST'])
def validate_password_api():
    """API endpoint for live password validation."""
    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    _, checks = validate_password(password)
    return jsonify(checks)


@app.route('/captcha/verify', methods=['POST'])
def verify_captcha():
    """API endpoint to verify a captcha challenge answer."""
    if 'captcha_challenges' not in session:
        return jsonify({'error': 'No captcha session active'}), 400

    data = request.get_json(silent=True) or {}
    challenge_type = data.get('type', '')
    answer = data.get('answer')

    current = session.get('current_captcha', {})
    passed = False
    message = ''
    roast = ''

    CAPTCHA_ROASTS_PASS = [
        'Acceptable. Your sigma energy is... detectable.',
        'The council acknowledges your existence. Barely.',
        'You passed, but don\'t let it go to your head, NPC.',
        'Huh. Didn\'t expect that from someone with your aura.',
        'The mewing moai nods approvingly. 🗿',
        'Certified non-NPC behavior. For now.',
    ]

    CAPTCHA_ROASTS_FAIL = [
        'WRONG. Your brainrot levels are disappointingly low.',
        'An NPC would\'ve gotten that right. You\'re BELOW NPC.',
        'The sigma council has noted your failure. -1000 aura.',
        'Tung Tung Tung Sahur bonks you for that answer. 💀',
        'Even the skibidi toilets are laughing at you rn.',
        'Your rizz just went into negative territory fr fr.',
        'Ohio called. They don\'t even want you there.',
    ]

    if challenge_type == 'npc_grid':
        selected = set(answer) if isinstance(answer, list) else set()
        correct = set(current.get('correct_indices', []))
        correct_selected = selected & correct
        extra_selected = selected - correct
        passed = (selected == correct) or (len(correct_selected) >= 2 and len(extra_selected) <= 1)
        if passed:
            message = 'Sigma energy correctly identified!'
        else:
            missed = correct - selected
            if missed and extra_selected:
                message = f'You missed {len(missed)} sigma(s) and selected {len(extra_selected)} NPC(s).'
            elif missed:
                message = f'You missed {len(missed)} sigma square(s). Almost had it!'
            else:
                message = f'You clicked {len(extra_selected)} NPC square(s).'

    elif challenge_type == 'runaway_checkbox':
        click_count = data.get('click_count', 0)
        passed = bool(answer)
        if passed:
            if click_count > 3:
                message = f'You cornered and caught it! Excellent sigma reflexes.'
            else:
                message = 'You caught it on the first try! Superhuman speed.'
        else:
            message = 'Checkbox was not checked. Try clicking it again!'

    elif challenge_type == 'mewing_timer':
        try:
            held_time = float(answer)
            target = float(current.get('target_time', 3.00))
            tolerance = float(current.get('tolerance', 0.70))
            diff = abs(held_time - target)
            passed = diff <= tolerance
            if passed:
                message = f'Held for {held_time:.2f}s (target: {target}s ±{tolerance}s). Flawless jawline precision.'
            else:
                if held_time < target:
                    message = f'Held for {held_time:.2f}s, needed {target}s (±{tolerance}s). A bit too early!'
                else:
                    message = f'Held for {held_time:.2f}s, needed {target}s (±{tolerance}s). Held a bit too long!'
        except (ValueError, TypeError):
            message = 'Invalid mewing data.'

    elif challenge_type == 'brainrot_math':
        try:
            user_answer = int(str(answer).strip())
            correct_answer = current.get('answer', 0)
            passed = user_answer == correct_answer
            if passed:
                message = f'Correct! {correct_answer} is right. Brainrot math certified.'
            else:
                message = f'You entered {user_answer}. The answer was {correct_answer}.'
        except (ValueError, TypeError):
            message = 'Please enter a valid number.'

    elif challenge_type == 'rizz_unscramble':
        correct_answer = current.get('answer', '').lower().strip()
        user_clean = re.sub(r'[^a-z0-9]', '', str(answer).lower())
        correct_clean = re.sub(r'[^a-z0-9]', '', str(correct_answer).lower())
        passed = (user_clean == correct_clean) or (correct_clean in user_clean)
        if passed:
            message = f'Correct! "{correct_answer}" — brainrot literacy 100/100.'
        else:
            message = f'You typed "{answer}". The answer was "{correct_answer}".'

    roast = random.choice(CAPTCHA_ROASTS_PASS if passed else CAPTCHA_ROASTS_FAIL)

    # Update session state
    idx = session.get('captcha_index', 0)
    challenges = session.get('captcha_challenges', [])

    if passed:
        session['captcha_passed'] = session.get('captcha_passed', 0) + 1
    else:
        session['captcha_failed'] = session.get('captcha_failed', 0) + 1

    next_idx = idx + 1
    session['captcha_index'] = next_idx

    # Check if all challenges are done
    all_done = next_idx >= len(challenges)
    captcha_success = False
    next_captcha = None

    if all_done:
        total_passed = session.get('captcha_passed', 0)
        # Pass if passed at least 1 or 2
        if total_passed >= 1:
            session['captcha_completed'] = True
            captcha_success = True
        else:
            # Keep credentials so they can easily retry
            session['captcha_index'] = 0
            session['captcha_passed'] = 0
            session['captcha_failed'] = 0
    else:
        # Generate next challenge
        next_challenge = generate_captcha_challenge(challenges[next_idx])
        session['current_captcha'] = next_challenge
        next_captcha = next_challenge

    return jsonify({
        'passed': passed,
        'message': message,
        'roast': roast,
        'all_done': all_done,
        'captcha_success': captcha_success,
        'next_captcha': next_captcha,
        'progress': {
            'current': next_idx,
            'total': len(challenges),
            'passed': session.get('captcha_passed', 0),
            'failed': session.get('captcha_failed', 0),
        }
    })


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
