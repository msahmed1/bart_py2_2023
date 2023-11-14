from flask import Blueprint, render_template, request, redirect, session, current_app, jsonify
from models import db, Players
import random
import threading

# Set up a dictionary to store the state of the buttons
button_states = {
    'voice1': False,
    'voice2': False,
    'voice3': False,
    'voice4': False
}

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
    session.pop('total_inflates', None)
    session.pop('score', None)
    session.pop('scales_index', None)
    session.pop('question_group_index', None)
    session.pop('help_provided', None)
    session.pop('balloon_color', None)
    session.pop('totalScore', None)
    session.pop('score', None)
    session.pop('total_inflates', None)
    session.pop('balloon_number', None)
    session.pop('balloon_limit', None)
    session.pop('exp_cond', None)
    session.pop('max_score', None)

    session['totalScore'] = 0
    session['max_score'] = 0
    session['score'] = 0
    session['total_inflates'] = 0
    session['balloon_number'] = 0
    session['run_once'] = True
    session['more_than_one_reconnect'] = False

    robot_controller = current_app.config['robot_controller']

    robot_controller.set_robot_ip("robot_2")
    robot_controller.sleep()

    robot_controller.set_robot_ip("robot_1")
    robot_controller.sleep()

    non_custom_first = Players.query.filter_by(customise_first=False, testing=False, game_completed=True).count()
    custom_first = Players.query.filter_by(customise_first=True, testing=False, game_completed=True).count()

    return render_template('set_up.html', non_custom_first=non_custom_first, custom_first=custom_first)

@onboarding.route('/submit_setup', methods=['POST'])
def submit_setup():
    # Get the toggle state from the form
    session['exp_cond'] = 'toggleState' in request.form

    robot_controller = current_app.config['robot_controller']
    robot_controller.face_participant()
    # robot_controller.set_robot_ip("robot_1")
    # robot_controller.start_up()

    # if session['exp_cond']:
    #     robot_controller.set_robot_ip("robot_2")
    #     robot_controller.sleep()
    
    return render_template('onboarding.html')

@onboarding.route('/submit_id', methods=['POST'])
def submit_id():
    player_id = generate_id()
    while Players.query.get(player_id) is not None:  # Check if the ID already exists in the database
        player_id = generate_id()  # Generate a new ID

    player = Players(player_id, not session['exp_cond'], False)
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
    player = Players(player_id, not session['exp_cond'], True)
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
    gender = request.form.get('other-gender-text')

    player = Players.query.get(player_id)  # Get the player from the database

    player.age = age
    player.gender = gender

    db.session.commit()  # Commit the changes to the database
    
    return redirect('/robot_setup')

@onboarding.route('/robot_setup')
def robot_setup():
    return render_template('custom_setup.html', button_states=button_states, banner_image_url=banner_image_url)

@onboarding.route('/voice/<button_name>')
def voice_button_click(button_name):
    if button_name in button_states:
        # Set the state of all buttons to False
        for key in button_states:
            button_states[key] = False
        # Set the state of the clicked button to True
        button_states[button_name] = True
        # Call the function in robot_controller
        robot_controller = current_app.config['robot_controller']
        threading.Thread(target=robot_controller.set_voice, args=(button_name,)).start()
    return jsonify({'status': 'success'})

@onboarding.route('/colour/<button_name>')
def colour_button_click(button_name):
    # Call the function in robot_controller
    robot_controller = current_app.config['robot_controller']
    threading.Thread(target=robot_controller.change_colour, args=(button_name,)).start()
    return jsonify({'status': 'success'})

@onboarding.route('/submit_customisation', methods=['POST'])
def submit_customisation():
    robot_name = request.form.get('robot-name')
    session['robot_name'] = robot_name
    # Save the name and use it to introduce the robot
    return redirect('/gameIntro')