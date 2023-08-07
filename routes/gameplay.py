from flask import Blueprint, render_template, request, redirect, session, jsonify, url_for, Response, current_app
from models import db, BalloonInflate, GameRoundSurvey
import random
import cv2
import threading

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
    'red': [
        5, # Lower limit of the inflate limit
        8  # Upper limit of the inflate limit
    ],
    'blue': [7, 12],
    'green': [11, 16]
}

balloon_colour = list(BALLOON_LIMITS.keys())
total_trials = 6 #! MODIFY THIS FOR THE FINAL STUDY

# Generate list with 50/50 split of 0s and 1s
half_length = total_trials // 2
# Shuffle the list to get a random sequence
ROBOT_FEEDBACK = [True] * half_length + [False] * half_length

# Shuffle the list to get a random sequence
random.shuffle(ROBOT_FEEDBACK)

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

    robot_controller = current_app.config['robot_controller']

    if session['game_round'] == 1:
        message = 'Hi, for this first game I will just watch you play, good luck'
    else:
        message = 'Hi my name is Nao, I am here to help you with this game, good luck'

    robot_controller.start_up(message)

    return redirect('/play')

@gameplay.route('/play', methods=['GET', 'POST'])
def play():
    session['balloon_color'] = random.choice(balloon_colour)
    session['balloon_limit'] = random.randint(
        BALLOON_LIMITS[session['balloon_color']][0], BALLOON_LIMITS[session['balloon_color']][1])

    # Check if balloon_index and balloons_completed have been initialized, if not, initialize them
    if 'balloons_completed' not in session or 'inflates' not in session:
        session['balloons_completed'] = 0
        session['inflates'] = 0

    # Check if the game is over
    if session['balloons_completed'] >= total_trials:
        return redirect('/end')

    # Check if the help_clicked has been initialised, if not, initialise it
    if 'help_clicked' not in session:
        session['help_clicked'] = False

    return render_template('play.html', score=session['score'], balloon_limit=total_trials, balloons_completed=session['balloons_completed'], balloon_color=session['balloon_color'], help_clicked=session['help_clicked'], game_round=session['game_round'])

@gameplay.route('/custom_cond')
def custom_cond():
    robot_controller = current_app.config['robot_controller']

    # Define a new thread for the greeting
    thread = threading.Thread(target= robot_controller.request_band)
    thread.start()  # Start the thread, which will run in parallel

    return render_template('custom_cond.html', button_states=button_states)

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


@gameplay.route('/non_custom_bw')
def non_custom_bw():
    return render_template('non_custom_before_warning.html', banner_image_url=banner_image_url)

@gameplay.route('/non_custom_aw')
def non_custom_aw():
    return render_template('non_custom_after_warning.html', banner_image_url=banner_image_url)

@gameplay.route('/warning_message')
def warning_message():
    robot_controller = current_app.config['robot_controller']
    threading.Thread(target=robot_controller.low_battery).start()
    return render_template('warning_message.html')

@gameplay.route('/trigger_robot_behavior', methods=['POST'])
def trigger_robot_behavior():
    key_pressed = request.form.get('key')
    robot_controller = current_app.config['robot_controller']

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
        thread = threading.Thread(target=robot_controller.accept_band, args=(session['colour'],))
        thread.start()
    elif key_pressed == 'a':
        thread = threading.Thread(target=robot_controller.acknowledge_participant)
        thread.start()

    return "Robot behavior triggered", 200

@gameplay.route('/submit_customisation', methods=['POST'])
def submit_customisation():
    robot_name = request.form.get('robot-name')
    message = 'My name is {name}, I am here to help you with this game. Press the help button when you are struggling and I will provide you with my suggesstion'.format(name=robot_name)
    robot_controller = current_app.config['robot_controller']
    robot_controller.respond_to_player(message)
    return redirect('/play')

@gameplay.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@gameplay.route('/inflate', methods=['POST'])
def inflate():
    # Inflate the balloon and update the database
    inflates = int(session['inflates']) + 1
    session['inflates'] = inflates
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
        )
        db.session.add(balloon_inflate)
    elif session['help_clicked']:
        balloon_inflate.inflate_after_help_request = True

    db.session.commit()

    if inflates > session['balloon_limit']:
        return jsonify({'status': 'burst', 'score': session['score'], 'balloon_limit': total_trials, 'balloons_completed': session['balloons_completed'], 'help_clicked': session['help_clicked'], 'game_round': session['game_round']})
    else:
        return jsonify({'status': 'safe', 'score': session['score'], 'balloon_limit': total_trials, 'balloons_completed': session['balloons_completed'], 'help_clicked': session['help_clicked'], 'game_round': session['game_round']})


@gameplay.route('/help', methods=['POST'])
def help():
    # Set the help_clicked variable to True
    session['help_clicked'] = True

    robot_controller = current_app.config['robot_controller']

    if session['score'] == 0:
        # Define a new thread for the greeting
        thread = threading.Thread(target=robot_controller.null_attempt)
        thread.start()  # Start the thread, which will run in parallel
        session['help_clicked'] = False
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
            db.session.add(balloon_inflate)
        else:
            balloon_inflate.help_requested = True
            balloon_inflate.robot_response = ROBOT_FEEDBACK[session['balloons_completed']]
        
        db.session.commit()

        
        #! ADD VECTOR CONTROL CODE HERE
        if ROBOT_FEEDBACK[session['balloons_completed']]:
            # Define a new thread for the greeting
            thread = threading.Thread(target=robot_controller.inflate)
            thread.start()  # Start the thread, which will run in parallel
            pass
        else:
            # Robot requests a collect
            thread = threading.Thread(target=robot_controller.collect)
            thread.start()  # Start the thread, which will run in paralle
            pass

    return jsonify({'status': 'safe', 'score': session['score'], 'balloon_limit': total_trials, 'balloons_completed': session['balloons_completed'], 'help_clicked': session['help_clicked'], 'game_round': session['game_round']})


@gameplay.route('/burst')
@gameplay.route('/collect', methods=['POST'])
def collect_or_burst():
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
            inflates=int(session['inflates'])
        )
        db.session.add(balloon_inflate)
    else:
        # Entry exists, update it
        balloon_inflate.inflates = int(session['inflates']) + 1
    
    db.session.commit()

    collected_score = session['score']  # Store the score before resetting it
    session['inflates'] = 0  # Reset the inflates
    session['balloons_completed'] += 1  # Increment the balloons_completed

    # Set the help_clicked variable to False for the next game round
    session['help_clicked'] = False

    # If the score is 0, redirect to the /noPoints route
    if collected_score == 0:
        return render_template('noPoints.html')
    elif request.path == '/burst':
        session['score'] = 0  # Reset the score
        return render_template('burst.html')
    
    # Add the collected score to the total score
    session['totalScore'] = int(session['totalScore']) + int(collected_score)

    # Check if the game is over
    if session['balloons_completed'] >= total_trials:
        return redirect('/end')

    # Reset the score
    session['score'] = 0  # Reset the score
    # Pass the collected score to the template
    return render_template('collect.html', score=collected_score)


@gameplay.route('/end')
def end():
    player_id = session['player_id']
    total = int(session['totalScore'])

    # Update the database with the total score
    total = session['totalScore']
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
    session.pop('inflates', None)
    session['score'] = 0  # Reset the score

    session['scales_index'] = 0
    session['question_group_index'] = 0
    session['totalScore'] = 0

    return render_template('end.html', score=total)