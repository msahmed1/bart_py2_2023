from flask import Blueprint, render_template, request, redirect, session, current_app, jsonify
from models import db, Players
import random

onboarding = Blueprint('onboarding', __name__)

banner_image_url = 'static/logos.png'

def generate_id():
    first_digit = random.randint(1, 9)
    middle_digits = random.randint(0, 99)
    last_digit = random.randint(1, 9)
    return first_digit * 1000 + middle_digits * 10 + last_digit

@onboarding.route('/')
def index():
    # Clear all the session variables
    session.pop('game_round', None)
    session.pop('player_id', None)
    session.pop('balloons_completed', None)
    session.pop('inflates', None)
    session.pop('score', None)
    session.pop('scales_index', None)
    session.pop('question_group_index', None)
    session.pop('help_provided', None)
    session.pop('balloon_color', None)
    session.pop('totalScore', None)
    session.pop('score', None)
    session.pop('inflates', None)
    session.pop('balloon_number', None)
    session.pop('balloon_limit', None)
    session.pop('colour', None)

    session['totalScore'] = 0
    session['score'] = 0
    session['inflates'] = 0
    session['balloon_number'] = 0

    robot_controller = current_app.config['robot_controller']
    robot_controller.set_robot_ip("robot_1")
    robot_controller.sleep()

    robot_controller.set_robot_ip("robot_2")
    robot_controller.sleep()

    count_false = Players.query.filter_by(customise_first=False, testing=False).count()
    count_true = Players.query.filter_by(customise_first=True, testing=False).count()

    return render_template('set_up.html', count_false=count_false, count_true=count_true)

@onboarding.route('/submit_setup', methods=['POST'])
def submit_setup():
    # Get the toggle state from the form
    session['toggle_state'] = 'toggleState' in request.form

    return render_template('onboarding.html')

@onboarding.route('/submit_id', methods=['POST'])
def submit_id():
    player_id = generate_id()
    while Players.query.get(player_id) is not None:  # Check if the ID already exists in the database
        player_id = generate_id()  # Generate a new ID

    player = Players(player_id, session['toggle_state'], False)  # Pass the consent to the Players constructor
    session['player_id'] = player_id
    db.session.add(player)
    
    db.session.commit()
    return redirect('/consent')

@onboarding.route('/submit_dev_id', methods=['POST'])
def submit_dev_id():
    player_id = generate_id()
    while Players.query.get(player_id) is not None:  # Check if the ID already exists in the database
        player_id = generate_id()  # Generate a new I
    
    # Set testing to True if dev button is clicked
    player = Players(player_id, session['toggle_state'], True)  # Pass the consent to the Players constructor
    session['player_id'] = player_id
    db.session.add(player)
    
    db.session.commit()
    return redirect('/consent')

@onboarding.route('/consent')
def consent():
    return render_template('consent.html', banner_image_url=banner_image_url)

@onboarding.route('/submit_consent', methods=['POST'])
def submit_consent():
    player_id = session['player_id']
    consent = 'consent' in request.form  # This will be True if the player checked the "I Agree" box, and False otherwise
    player = Players.query.get(player_id)  # Get the player from the database
    player.consent = consent  # Update the player's consent
    db.session.commit()  # Commit the changes to the database
    return redirect('/demograph')  # Redirect to the play page

@onboarding.route('/demograph')
def demograph_form():
    return render_template('demograph.html', banner_image_url=banner_image_url)

@onboarding.route('/submit_demograph', methods=['POST'])
def submit_demograph():
    player_id = session['player_id']
    age = request.form['age']
    gender = request.form['gender']
    # ethnicity = request.form['ethnicity']
    # education = request.form['education']
    # robot_familiarity = request.form['robot_familiarity']

    player = Players.query.get(player_id)  # Get the player from the database

    player.age = age
    player.gender = gender
    # player.ethnicity = ethnicity
    # player.education = education
    # player.robot_familiarity = robot_familiarity

    db.session.commit()  # Commit the changes to the database
    
    return redirect('/gameIntro')
