from flask import Blueprint, render_template, request, redirect, session, current_app
from models import db, GameRoundSurvey, Players
import threading
import datetime

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
                "question": "I feel a very high degree of personal ownership for this robot", "name": "i_feel_high_degree_of_personal_ownership_for_this_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "I sense that I own this robot.", "name": "i_sense_that_i_own_this_robot"},
            {"left": "Disagree", "right": "Agree",
                "question": "Robot incorporates a part of myself.", "name": "robot_incorporates_a_part_of_myself"},
        ],
    },
    {
        "title": "Please indicate the extent to which you agree or disagree with the following statements about your robot.",
        "questions": [
            {"left": "Disagree", "right": "Agree",
                "question": "My robot supplies my need for help through a help function.", "name": "my_robot_supplies_my_need_for_help_through_a_help_function"},
            {"left": "Disagree", "right": "Agree",
                "question": "My robot provides competent guidance (as needed) through a help function.", "name": "my_robot_provides_competent_guidanceas_through_a_help_function"},
            {"left": "Disagree", "right": "Agree",
                "question": "My robot provides very sensible and effective advice, if needed.", "name": "my_robot_provides_very_sensible_and_effective_advice_if_needed"},
        ],
    },
    {
        "title": "By Using this robotic advisor...",
        "questions": [
            {"left": "Disagree", "right": "Completely agree", "question": "I can decide more quickly and easily which action to take than without using this robotic advisor", "name": "i_can_decide_more_quickly_and_easily_which_action_to_take_than_without_using_this_robotic_advisor"},
            {"left": "Disagree", "right": "Completely agree", "question": "I can make better decisions than without using this robotic advisor", "name": "i_can_make_better_decisions_than_without_using_this_robotic_advisor"},
            {"left": "Disagree", "right": "Completely agree", "question": "I am better informed about what action to take than without using this robotic advisor", "name": "i_am_better_informed_about_what_action_to_take_than_without_using_this_robotic_advisor"},
            {"left": "Disagree", "right": "Completely agree", "question": "I can make more accurate decisions than without using this robotic advisor", "name": "i_can_make_more_accurate_decisions_than_without_using_this_robotic_advisor"},
            {"left": "Disagree", "right": "Completely agree", "question": "I can better decide whether I want to inflate the balloon or not" , "name": "i_can_better_decide_whether_i_want_to_inflate_the_balloon_or_not"},
        ]
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
        db.session.commit()

    withdrawl_date = datetime.date.today() + datetime.timedelta(days=7)
    return render_template('close.html', banner_image_url=banner_image_url, participant_id=player_id, datetime = str(withdrawl_date.strftime("%b/%d/%Y")))