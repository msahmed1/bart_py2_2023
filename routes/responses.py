from flask import Blueprint, render_template, request, redirect, session
from models import db, GameRoundSurvey, Players
import datetime
import csv

responses = Blueprint('responses', __name__)

banner_image_url = 'static/logos.png'

survey_questions = [
    {
        "title": "Please rate your impressions of the robot on these scales:",
        "questions": [
            {"left": "Dislike", "right": "Like", "question": "", "name": "dislike_like"},
            {"left": "Unfriendly", "right": "Friendly", "question": "",
            "name": "unfriendly_friendly"},
            {"left": "Unkind", "right": "Kind", "question": "", "name": "unkind_kind"},
            {"left": "Unpleasant", "right": "Pleasant", "question": "",
            "name": "unpleasant_pleasant"},
            {"left": "Awful", "right": "Nice", "question": "", "name": "awful_nice"},
        ],
    },
    {
        "title": "Please rate your impressions of the robot on these scales:",
        "questions": [
            {"left": "Incompetent", "right": "Competent", "question": "",
            "name": "incompetent_competent"},
            {"left": "Ignorant", "right": "Knowledgeable", "question": "",
            "name": "ignorant_knowledgeable"},
            {"left": "Irresponsible", "right": "Responsible", "question": "",
            "name": "iriresponsible_responsible"},
            {"left": "Unintelligent", "right": "Intelligent", "question": "",
            "name": "unitelligent_intelligent"},
            {"left": "Foolish", "right": "Sensible", "question": "", "name": "foolish_sensible"},
        ],
    },
    {
        "title": "Please indicate the extent to which you agree or disagree with the following statements about your robot.",
        "questions": [
            {"left": "Disagree", "right": "Agree",
                "question": "This is my robot", "name": "this_is_my_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "I sense that I own this robot", "name": "i_sense_that_i_own_this_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "This robot incorporates a part of myself", "name": "this_robot_incorporates_a_part_of_myself"},
        ],
    },
    {
        "title": "Please indicate the extent to which you agree or disagree with the following statements about your robot.",
        "questions": [
            {"left": "Disagree", "right": "Agree",
                "question": "I am confident in the robot", "name": "i_am_confident_in_the_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "The robot provides security", "name": "the_robot_provides_security"},
            {"left": "Disagree", "right": "Agree",
                "question": "The robot has integrity", "name": "the_robot_has_integrity"},
            {"left": "Disagree", "right": "Agree",
                "question": "The robot gave good advice", "name": "the_robot_gave_good_advice"},
            {"left": "Disagree", "right": "Agree",
                "question": "The robot is reliable", "name": "the_robot_is_reliable"},
            {"left": "Disagree", "right": "Agree",
                "question": "I can trust the robot", "name": "i_can_trust_the_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "I am familiar with the robot", "name": "i_am_familiar_with_the_robot"},
        ],
    }
]

@responses.route('/survey', methods=['GET', 'POST'])
def survey():
    player_id = session['player_id']
    game_round = session['game_round']

    if(session['game_round'] == 1):
        if session['exp_cond'] == True:
            session['totalScore'] = 0
            session['game_round'] += 1
            session['exp_cond'] = False
            return redirect('/non_custom_post_error')
        else:
            session['totalScore'] = 0
            session['game_round'] += 1
            session['exp_cond'] = True
            return redirect('/custom_post_error')

    if 'question_group_index' not in session:
        session['question_group_index'] = 0
    
    # Handle the form submission
    if request.method == 'POST':
        # Get the GameRoundSurvey instance associated with the current player and game round
        game_round_survey = GameRoundSurvey.query.filter_by(
            player_id=player_id, game_round=game_round).first()

        # If it doesn't exist, create a new one
        if not game_round_survey:
            game_round_survey = GameRoundSurvey(
                player_id=player_id, game_round=game_round)
            db.session.add(game_round_survey)

        if session['scales_index'] < len(survey_questions):
            # Update the GameRoundSurvey instance's attributes based on the form data
            for question in (survey_questions[session['scales_index']])["questions"]:
                setattr(game_round_survey,
                        question["name"], request.form[question["name"]])
            
            # Commit the changes to the database
            db.session.commit()

            # Increment the scales index
            session['scales_index'] += 1

            # If there are more scales, redirect to the survey page again
            if session['scales_index'] < len(survey_questions):
                # If there are more scales, redirect to the survey page again
                return render_template('survey.html', title=survey_questions[session['scales_index']]["title"], scales=survey_questions[session['scales_index']]["questions"], action_url="/survey", banner_image_url=banner_image_url)    
    
    if session['scales_index'] < len(survey_questions):
        return render_template('survey.html', title=survey_questions[session['scales_index']]["title"], scales=survey_questions[session['scales_index']]["questions"], action_url="/survey", banner_image_url=banner_image_url)
    elif session['game_round'] < 3:
        if session['exp_cond'] == True:
            session['totalScore'] = 0
            session['game_round'] += 1
            session['exp_cond'] = False
            return redirect('/non_custom_pre_error')
        else:
            session['totalScore'] = 0
            session['game_round'] += 1
            session['exp_cond'] = True
            return redirect('/custom_pre_error')
    else:
        return render_template('freetext.html', banner_image_url=banner_image_url)
        

@responses.route('/freetext', methods=['GET', 'POST'])
def freetext():
    player_id = session['player_id']

    if request.method == 'POST':
        player = Players.query.filter_by(
            player_id=player_id).first()
        
        setattr(player, "freetext", request.form["response"])
        player.game_completed = True
        db.session.commit()

    return render_template('email.html', banner_image_url=banner_image_url)

@responses.route('/submit_email', methods=['POST'])
def submit_email():
    player_id = session['player_id']
    email = request.form.get('email1')

    if email != '':
        # Save the email to a CSV file
        with open('instance/emails.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([email, session['max_score'], datetime.datetime.now()])
    
    withdrawl_date = datetime.date.today() + datetime.timedelta(days=7)
    return render_template('close.html', banner_image_url=banner_image_url, participant_id=player_id, datetime = str(withdrawl_date.strftime("%b/%d/%Y")))