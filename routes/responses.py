from flask import Blueprint, render_template, request, redirect, session, current_app
from models import db, GameRoundSurvey
import threading
import datetime

responses = Blueprint('responses', __name__)

banner_image_url = 'static/logos.png'

intermediate_questions = [
    [
        {"left": "Dislike", "right": "Like", "name": "dislike_like"},
        {"left": "Unfriendly", "right": "Friendly",
         "name": "unfriendly_friendly"},
        {"left": "Unkind", "right": "Kind", "name": "unkind_kind"},
        {"left": "Unpleasant", "right": "Pleasant",
         "name": "unpleasant_pleasant"},
        {"left": "Awful", "right": "Nice", "name": "awful_nice"},
    ],
    [
        {"left": "Incompetent", "right": "Competent",
         "name": "incompetent_competent"},
        {"left": "Ignorant", "right": "Knowledgeable",
         "name": "ignorant_knowledgeable"},
        {"left": "Irresponsible", "right": "Responsible",
         "name": "iriresponsible_responsible"},
        {"left": "Unintelligent", "right": "Intelligent",
         "name": "unitelligent_intelligent"},
        {"left": "Foolish", "right": "Sensible", "name": "foolish_sensible"},
    ],
]

final_questions = [
    [
        {"left": "Disagree", "right": "Agree",
            "question": "This is my robot", "name": "this_is_my_robot"},
        {"left": "Disagree", "right": "Agree",
            "question": "I feel a very high degree of personal ownership for this robot", "name": "i_feel_high_degree_of_personal_ownership_for_this_robot"},
        {"left": "Disagree", "right": "Agree",
            "question": "I sense that I own this robot.", "name": "i_sense_that_i_own_this_robot"},
        {"left": "Disagree", "right": "Agree",
            "question": "Robot incorporates a part of myself.", "name": "robot_incorporates_a_part_of_myself"},
    ],
    # [
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "I feel I have control over my robot.", "name": "i_feel_i_have_control_over_my_robot"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "When I consider my robot, I feel in control.", "name": "when_i_consider_my_robot_i_feel_in_control"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "I feel that I have no control over my robot.", "name": "i_feel_that_i_have_no_control_over_my_robot"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "I feel in control of my robot.", "name": "i_feel_in_control_of_my_robot"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "In general, to what extent do you have control over your robot?", "name": "in_general_to_what_extent_do_you_have_control_over_your_robot"},
    # ],
    # [
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "I feel very involved in my relationship with my robot - like I have put a great deal into it.", "name": "i_feel_very_involved_in_my_relationship_with_my_robot_like_i_have_put_a_great_deal_into_it"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "I have invested a great deal in my relationship with my robot.", "name": "i_have_invested_a_great_deal_in_my_relationship_with_my_robot"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "The time I have spent on my robot is significant.", "name": "the_time_i_have_spent_on_my_robot_is_significant"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "Compared to other things, I have spent a lot of effort using my robot.", "name": "compared_to_other_things_i_have_spent_a_lot_of_effort_using_my_robot"},
    # ],
    # [
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot has the functionality I need.", "name": "my_robot_has_the_functionality_I_need"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot has the required features for my tasks.", "name": "my_robot_has_the_required_features_for_my_tasks"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot has the ability to do what I want it to do.", "name": "my_robot_has_the_ability_to_do_what_i_want_it_to_do"},
    # ],
    [
        {"left": "Disagree", "right": "Agree",
            "question": "My robot supplies my need for help through a help function.", "name": "my_robot_supplies_my_need_for_help_through_a_help_function"},
        {"left": "Disagree", "right": "Agree",
            "question": "My robot provides competent guidance (as needed) through a help function.", "name": "my_robot_provides_competent_guidanceas_through_a_help_function"},
        {"left": "Disagree", "right": "Agree",
            "question": "My robot provides very sensible and effective advice, if needed.", "name": "my_robot_provides_very_sensible_and_effective_advice_if_needed"},
    ],
    # [
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot is a very reliable technology.", "name": "my_robot_is_a_very_reliable_technology"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot does not fail me.", "name": "my_robot_does_not_fail_me"},
    #     {"left": "Disagree", "right": "Agree",
    #         "question": "My robot is extremely dependable.", "name": "my_robot_is_extremely_dependable"},
    # ]
]

@responses.route('/survey', methods=['GET', 'POST'])
def survey():
    player_id = session['player_id']
    game_round = session['game_round']

    if(session['game_round'] == 1):
        session['totalScore'] = 0
        session['game_round'] += 1
        return redirect('/custom_cond')

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

        if session['scales_index'] < len(intermediate_questions):
            # Update the GameRoundSurvey instance's attributes based on the form data
            for question in intermediate_questions[session['scales_index']]:
                setattr(game_round_survey,
                        question["name"], request.form[question["name"]])
            
            # Commit the changes to the database
            db.session.commit()

            # Increment the scales index
            session['scales_index'] += 1

            # If there are more scales, redirect to the survey page again
            if session['scales_index'] < len(intermediate_questions):
                scales = intermediate_questions[session['scales_index']]
                # If there are more scales, redirect to the survey page again
                return render_template('survey.html', scales=scales, action_url="/survey", banner_image_url=banner_image_url)
            
        elif session['question_group_index'] < len(final_questions):
            for question in final_questions[session['question_group_index']]:
                setattr(game_round_survey, question["name"], request.form[question["name"]])

            db.session.commit()

            session['question_group_index'] += 1

            if session['question_group_index'] < len(final_questions):
                # Set up a final survey index
                # Go through all the questions
                return render_template('final_survey.html', question_group=final_questions[session['question_group_index']], action_url="/survey", banner_image_url=banner_image_url)        
    
    if session['scales_index'] < len(intermediate_questions):
        return render_template('survey.html', scales=intermediate_questions[session['scales_index']], action_url="/survey", banner_image_url=banner_image_url)
    elif session['question_group_index'] < len(final_questions):
        return render_template('final_survey.html', question_group=final_questions[session['question_group_index']], action_url="/survey", banner_image_url=banner_image_url)
    elif session['game_round'] < 3:
        session['totalScore'] = 0
        session['game_round'] += 1
        return redirect('/non_custom_bw')
    else:
        robot_controller = current_app.config['robot_controller']
        thread = threading.Thread(target=robot_controller.sleep)
        thread.start()
        withdrawl_date = datetime.date.today() + datetime.timedelta(days=7)
        return render_template('close.html', banner_image_url=banner_image_url, participant_id=player_id, datetime = str(withdrawl_date.strftime("%b/%d/%Y")))


# @responses.route('/final_survey', methods=['GET', 'POST'])
# def final_survey():
#     player_id = session['player_id']
#     player = Players.query.get(player_id)

#     if 'question_group_index' not in session:
#         session['question_group_index'] = 0

#     # Handle the form submission
#     if request.method == 'POST':
#         for question in final_questions[session['question_group_index']]:
#             setattr(player, question["name"], request.form[question["name"]])

#         db.session.commit()

#         session['question_group_index'] += 1

#     if session['question_group_index'] < len(final_questions):
#         # Set up a final survey index
#         # Go through all the questions
#         return render_template('final_survey.html', question_group=final_questions[session['question_group_index']], action_url="/final_survey", banner_image_url=banner_image_url)
#     # If all the final surveys are completed, redirect to the '/close' route
#     else:
#         robot_controller = current_app.config['robot_controller']
#         thread = threading.Thread(target=robot_controller.sleep)
#         thread.start() 
#         return render_template('close.html')
