from flask import Blueprint, render_template, request, redirect, session, jsonify, url_for, Response, current_app
from models import db, BalloonInflate, GameRoundSurvey
import random
import cv2
import threading
from datetime import datetime
import numpy as np

def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
    camera.release()

gameplay = Blueprint('gameplay', __name__)

# Define the inflate limit for each balloon
BALLOON_LIMITS = {
    # 'red': 8,
    'green': 32
}

total_trials = 30 #! MODIFY THIS FOR THE FINAL STUDY
# Generate list with 50/50 split of 0s and 1s
half_length = total_trials // 2

def generate_random_integers(n, mean=16.5, std_dev=5):
    numbers = np.random.normal(mean, std_dev, n)
    rounded_numbers = np.round(numbers)
    return np.clip(rounded_numbers, 1, 32).astype(int)

balloon_colours = list(BALLOON_LIMITS.keys())
# 50% of the balloons are red and the other 50% is green
balloon_colour = [balloon_colours[0]] * total_trials #+ [balloon_colours[1]] * half_length

# Shuffle the list to get a random sequence
ROBOT_FEEDBACK = [True] * half_length + [False] * half_length

# Shuffle the list to get a random sequence
random.shuffle(ROBOT_FEEDBACK)
random.shuffle(balloon_colour)

banner_image_url = 'static/logos.png'

# Set up a dictionary to store the state of the buttons
button_states = {
    'voice1': False,
    'voice2': False,
    'voice3': False,
    'voice4': False
}

@gameplay.route('/gameIntro')
def gameIntro():
    return render_template('game_introduction.html', banner_image_url=banner_image_url)

@gameplay.route('/gameIntro_robot')
def gameIntro_robot():
    # Check if the game round has been initialized, if not, initialize it
    if 'game_round' not in session:
        session['game_round'] = 1  # Initialize game_round

    if session['game_round'] < 3:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_1")
    else:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_2")

    if session['game_round'] == 1:
        message = 'For this first game I will just watch you play, good luck'
        robot_controller.start_up(message)
    else:
        message = 'Hi, my name is Nao, I am here to help you with this game, good luck'
        robot_controller.start_up(message)    

    return redirect('/play')

@gameplay.route('/play', methods=['GET', 'POST'])
def play():
    # Check if balloon_index and balloons_completed have been initialized, if not, initialize them
    if 'balloons_completed' not in session or 'total_inflates' not in session:
        session['balloons_completed'] = 0
        session['total_inflates'] = 0

    # Check if the game is over
    if session['balloons_completed'] >= total_trials:
        return redirect('/end')

    # Check if the help_provided has been initialised, if not, initialise it
    if 'help_provided' not in session:
        session['help_provided'] = False

    session['balloon_color'] = balloon_colour[session['balloons_completed']]

    if session['balloons_completed'] == 0:
        global balloon_limit
        balloon_limit = generate_random_integers(total_trials)

    session['balloon_limit'] = balloon_limit[session['balloons_completed']]

     # If it is the second game round, handle the collect button functionality like the help button
    if session['game_round'] > 1:
        return render_template('play.html', score=session['score'], balloon_limit=total_trials, progress=session['balloons_completed']+1, balloon_color=session['balloon_color'], button_value=' Help ')

    return render_template('play.html', score=session['score'], balloon_limit=total_trials, progress=session['balloons_completed']+1, balloon_color=session['balloon_color'], button_value='Collect')

@gameplay.route('/condition_selection')
def condition_selection():
    if session['exp_cond']:
        return redirect('/custom_pre_error')
    else:
        return redirect('/non_custom_pre_error')

@gameplay.route('/custom_pre_error')
def custom_pre_error():
    return render_template('custom_before_error.html', banner_image_url=banner_image_url)

@gameplay.route('/custom_post_error')
def custom_post_error():
    # robot_controller = current_app.config['robot_controller']
    return render_template('custom_after_error.html', banner_image_url=banner_image_url)

@gameplay.route('/custom_cond')
def custom_cond():
    if session['game_round'] < 3:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_1")
    else:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_2")
        robot_controller.just_wake_up()


    robot_controller = current_app.config['robot_controller']

    threading.Thread(target=robot_controller.request_band).start()

    return render_template('customise_clothing.html')

@gameplay.route('/custom_voice')
def custom_voice():
    robot_controller = current_app.config['robot_controller']

    threading.Thread(target=robot_controller.request_voice_change).start()

    return render_template('customise_voice.html', button_states=button_states)

@gameplay.route('/custom_name')
def custom_name():
    robot_controller = current_app.config['robot_controller']

    threading.Thread(target=robot_controller.request_name_change).start()

    return render_template('customise_name.html')

@gameplay.route('/click/<button_name>')
def button_click(button_name):
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

@gameplay.route('/non_custom_pre_error')
def non_custom_pre_error():
    return render_template('non_custom_before_error.html', banner_image_url=banner_image_url)

@gameplay.route('/non_custom_post_error')
def non_custom_post_error():
    return render_template('non_custom_after_error.html', banner_image_url=banner_image_url)

@gameplay.route('/error_message_non_customise')
def error_message_non_customise():
    if session['run_once']:
        robot_controller = current_app.config['robot_controller']
        threading.Thread(target=robot_controller.low_battery).start()
        # print("#################### low battery, non custom")
        # print("session['run_once'] = {}".format(session['run_once']))
        session['run_once'] = False
    return render_template('error_message_non_customise.html')

@gameplay.route('/error_message_customise')
def error_message_customise():
    if session['run_once']:
        robot_controller = current_app.config['robot_controller']
        threading.Thread(target=robot_controller.low_battery).start()
        # print("session['run_once'] = {}".format(session['run_once']))
        # print("#################### low battery, custom")
        session['run_once'] = False
    return render_template('error_message_customise.html')

@gameplay.route('/trigger_robot_behavior', methods=['POST'])
def trigger_robot_behavior():
    key_pressed = request.form.get('key')
    robot_controller = current_app.config['robot_controller']

    if 'colour' not in session or not session['colour']:
        session['colour'] = ''

    if key_pressed == 'r':
        robot_controller.change_colour('red')
        robot_controller.talk("red")
        session['colour'] = 'red'
    elif key_pressed == 'g':
        robot_controller.change_colour('green')
        robot_controller.talk("green")
        session['colour'] = 'green'
    elif key_pressed == 'b':
        robot_controller.change_colour('blue')
        robot_controller.talk("blue")
        session['colour'] = 'blue'
    elif key_pressed == 'q':
        robot_controller.accept_band(session['colour'],)

    return "Robot behavior triggered", 200

@gameplay.route('/submit_customisation', methods=['POST'])
def submit_customisation():
    robot_name = request.form.get('robot-name')
    robot_controller = current_app.config['robot_controller']
    robot_controller.start_game_after_customisation(robot_name)
    return redirect('/play')

@gameplay.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@gameplay.route('/inflate', methods=['POST'])
def inflate():
    # Inflate the balloon and update the database
    total_inflates = int(session['total_inflates']) + 1
    session['total_inflates'] = total_inflates
    session['score'] += 10  # Increment the score

    # update the database with the player compliance if the robot requests an inflate and help is clicked
    balloon_inflate = BalloonInflate.query.filter_by(
        player_id=session['player_id'],
        balloon_id=session['balloons_completed'],
        game_round=session['game_round']
    ).first()

    if balloon_inflate is None:
        balloon_inflate = BalloonInflate(
            player_id=session['player_id'],
            balloon_id=session['balloons_completed'],
            game_round=session['game_round'],
            balloon_limit=session['balloon_limit'],
        )
        db.session.add(balloon_inflate)
    elif session['help_provided']:
        balloon_inflate.inflated_after_help_request = True
        balloon_inflate.balloon_limit = session['balloon_limit']

    if 'help_timestamp' in session:
        inflate_timestamp = datetime.now()
        time_to_decide = (inflate_timestamp - session['help_timestamp']).total_seconds()
        balloon_inflate.time_to_decide = time_to_decide
        del session['help_timestamp']  # remove the timestamp from the session
    
    db.session.commit()

    if total_inflates > session['balloon_limit']:
        return jsonify({'status': 'burst', 'score': session['score'], 'balloon_limit': total_trials, 'progress': session['balloons_completed']+1, 'game_round': session['game_round']})
    else:
        return jsonify({'status': 'safe', 'score': session['score'], 'balloon_limit': total_trials, 'progress': session['balloons_completed']+1, 'game_round': session['game_round']})

def help():
    # Record the current time when "Help" is clicked
    session['help_timestamp'] = datetime.now()

    # Set the help_provided variable to True
    session['help_provided'] = True

    robot_controller = current_app.config['robot_controller']

    if session['score'] == 0:
        # Define a new thread for the greeting
        thread = threading.Thread(target=robot_controller.null_attempt)
        thread.start()  # Start the thread, which will run in parallel
        session['help_provided'] = False
    else:
        # update the database with the player compliance if the robot requests an inflate and help is clicked
        balloon_inflate = BalloonInflate.query.filter_by(
            player_id=session['player_id'],
            balloon_id=session['balloons_completed'],
            game_round=session['game_round']
        ).first()

        if balloon_inflate is None:
            balloon_inflate = BalloonInflate(
                player_id=session['player_id'],
                balloon_id=session['balloons_completed'],
                game_round=session['game_round'],
                help_requested=True,
                robot_response=ROBOT_FEEDBACK[session['balloons_completed']]
            )
            balloon_inflate.inflate_before_help_request = int(session['total_inflates'])
            db.session.add(balloon_inflate)
        else:
            balloon_inflate.help_requested = True
            balloon_inflate.robot_response = ROBOT_FEEDBACK[session['balloons_completed']]
            balloon_inflate.inflate_before_help_request = int(session['total_inflates'])
        
        db.session.commit()
        
        if ROBOT_FEEDBACK[session['balloons_completed']]:
            # Robot requests a inflate
            thread = threading.Thread(target=robot_controller.inflate)
            thread.start()
            pass
        else:
            # Robot requests a collect
            thread = threading.Thread(target=robot_controller.collect)
            thread.start()
            pass
    
    if session['help_provided'] == False and session['game_round'] > 1:
        return jsonify({'button_value': ' Help '})
    else:
        return jsonify({'button_value': 'Collect'})

@gameplay.route('/burst')
@gameplay.route('/collect', methods=['POST'])
def collect_or_burst():

    if session['help_provided'] == False and session['game_round'] > 1 and session['balloons_completed'] < total_trials and session['total_inflates'] <= session['balloon_limit']:
        return help()
    
    # Record the balloon inflate in the database
    # Check if an entry already exists for this balloon
    balloon_inflate = BalloonInflate.query.filter_by(
        player_id=session['player_id'],
        balloon_id=session['balloons_completed'],
        game_round=session['game_round']
    ).first()

    if balloon_inflate is None:
        balloon_inflate = BalloonInflate(
            player_id=session['player_id'],
            balloon_id=session['balloons_completed'],
            game_round=session['game_round'],
            total_inflates=session['total_inflates'],
            balloon_limit=session['balloon_limit']
        )
        db.session.add(balloon_inflate)
    else:
        balloon_inflate.total_inflates = session['total_inflates']
        balloon_inflate.balloon_limit = session['balloon_limit']
    
    if 'help_timestamp' in session:
        collect_timestamp = datetime.now()
        time_to_decide = (collect_timestamp - session['help_timestamp']).total_seconds()
        balloon_inflate.time_to_decide = time_to_decide
        del session['help_timestamp']  # remove the timestamp from the session

    db.session.commit()

    collected_score = session['score']  # Store the score before resetting it
    session['total_inflates'] = 0  # Reset the total_inflates
    session['balloons_completed'] += 1  # Increment the balloons_completed

    # TODO: If help provided then recorde total_inflates after help provided
    
    # Set the help_provided variable to False for the next game round
    session['help_provided'] = False

    # If the score is 0, redirect to the /noPoints route
    if collected_score == 0:
        robot_controller = current_app.config['robot_controller']
        threading.Thread(target=robot_controller.no_points).start()
        return jsonify({'redirect_url': url_for('gameplay.noPoints')})
    elif request.path == '/burst' or session['total_inflates'] > session['balloon_limit']:
        robot_controller = current_app.config['robot_controller']
        threading.Thread(target=robot_controller.burst).start()
        session['score'] = 0  # Reset the score
        return render_template('burst.html')
    
    # Add the collected score to the total score
    session['totalScore'] = int(session['totalScore']) + int(collected_score)

    # Check if the game is over
    if session['balloons_completed'] >= total_trials:
        return jsonify({'redirect_url': url_for('gameplay.end')})

    # Pass the collected score to the template
    return jsonify({'redirect_url': url_for('gameplay.collect_page')})

@gameplay.route('/noPoints')
def noPoints():
    return render_template('noPoints.html')

@gameplay.route('/collect_page')
def collect_page():
    collected_score = session['score']  # Store the score before resetting it
    # Reset the score
    session['score'] = 0  # Reset the score
    return render_template('collect.html', score=collected_score)

@gameplay.route('/end')
def end():
    player_id = session['player_id']
    total = int(session['totalScore'])

    # Update the database with the total score
    total = session['totalScore']
    if session['totalScore'] > session['max_score']:
        session['max_score'] = session['totalScore']
    game_round_survey = GameRoundSurvey.query.filter_by(player_id=player_id, game_round=session['game_round']).first()

    if game_round_survey is None:
        # Player does not exist, create a new one
        game_round_survey = GameRoundSurvey(player_id=session['player_id'], game_round=session['game_round'], total_score=total)
        db.session.add(game_round_survey)
    else:
        # Player exists, update their attributes
        game_round_survey.total_score = total

    db.session.commit()

    # Reset the session variables
    session.pop('balloons_completed', None)
    session.pop('total_inflates', None)
    session['score'] = 0  # Reset the score

    session['scales_index'] = 0
    session['question_group_index'] = 0
    session['totalScore'] = 0
    
    return render_template('total_score.html', score=total)

@gameplay.route('/reconnect_to_robot')
def reconnect_to_robot():
    if session['game_round'] < 3:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_1")
    else:
        robot_controller = current_app.config['robot_controller']
        robot_controller.set_robot_ip("robot_2")
    
    robot_controller.attempt_reconnect()

    return "Attempting to reconnect to robot", 200