from __future__ import print_function
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Players(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    testing = db.Column(db.Boolean)
    consent = db.Column(db.Boolean)
    balloon_inflates = db.relationship(
        'BalloonInflate', backref='player', lazy=True)
    game_round_surveys = db.relationship(
        'GameRoundSurvey', backref='player', lazy=True)
    
    # Demographics
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    ethnicity = db.Column(db.String(50))
    education = db.Column(db.String(50))
    robot_familiarity = db.Column(db.Integer)
    

    def __init__(self, player_id, testing, consent=False):
        self.player_id = player_id
        self.testing = testing
        self.consent = consent


class BalloonInflate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.player_id'), nullable=False)
    balloon_id = db.Column(db.Integer, nullable=False)
    inflates = db.Column(db.Integer, default=0)

    game_round = db.Column(db.Integer, default=0)
    help_requested = db.Column(db.Boolean, default=False)
    robot_response = db.Column(db.Boolean, default=False)
    inflate_after_help_request = db.Column(db.Boolean, default=False)

    def __init__(self, player_id, balloon_id, inflates=0, game_round=0, help_requested=False, robot_response=False, inflate_after_help_request=False):
        super(BalloonInflate, self).__init__()
        self.player_id = player_id
        self.balloon_id = balloon_id
        self.inflates = inflates
        self.game_round = game_round

        self.help_requested = help_requested
        self.robot_response = robot_response
        self.inflate_after_help_request = inflate_after_help_request

class GameRoundSurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)
    game_round = db.Column(db.Integer, default=0)
    
    total_score = db.Column(db.Integer)

    dislike_like = db.Column(db.Integer)
    unfriendly_friendly = db.Column(db.Integer)
    unkind_kind = db.Column(db.Integer)
    unpleasant_pleasant = db.Column(db.Integer)
    awful_nice = db.Column(db.Integer)

    incompetent_competent = db.Column(db.Integer)
    ignorant_knowledgeable = db.Column(db.Integer)
    iriresponsible_responsible = db.Column(db.Integer)
    unitelligent_intelligent = db.Column(db.Integer)
    foolish_sensible = db.Column(db.Integer)

    this_is_my_robot = db.Column(db.Integer)
    i_feel_high_degree_of_personal_ownership_for_this_robot = db.Column(
        db.Integer)
    i_sense_that_i_own_this_robot = db.Column(db.Integer)
    robot_incorporates_a_part_of_myself = db.Column(db.Integer)

    my_robot_supplies_my_need_for_help_through_a_help_function = db.Column(
        db.Integer)
    my_robot_provides_competent_guidanceas_through_a_help_function = db.Column(
        db.Integer)
    my_robot_provides_very_sensible_and_effective_advice_if_needed = db.Column(
        db.Integer)

    def __init__(self, player_id, game_round=0, total_score=0, dislike_like=None, unfriendly_friendly=None, unkind_kind=None, unpleasant_pleasant=None, awful_nice=None, incompetent_competent=None, ignorant_knowledgeable=None, iriresponsible_responsible=None, unitelligent_intelligent=None, foolish_sensible=None, this_is_my_robot=None, i_feel_high_degree_of_personal_ownership_for_this_robot=None, i_sense_that_i_own_this_robot=None, robot_incorporates_a_part_of_myself=None, my_robot_supplies_my_need_for_help_through_a_help_function=None, my_robot_provides_competent_guidanceas_through_a_help_function=None, my_robot_provides_very_sensible_and_effective_advice_if_needed=None):
        super(GameRoundSurvey, self).__init__()
        self.player_id = player_id
        self.game_round = game_round
        self.total_score = total_score

        self.dislike_like = dislike_like
        self.unfriendly_friendly = unfriendly_friendly
        self.unkind_kind = unkind_kind
        self.unpleasant_pleasant = unpleasant_pleasant
        self.awful_nice = awful_nice

        self.incompetent_competent = incompetent_competent
        self.ignorant_knowledgeable = ignorant_knowledgeable
        self.iriresponsible_responsible = iriresponsible_responsible
        self.unitelligent_intelligent = unitelligent_intelligent
        self.foolish_sensible = foolish_sensible

        self.this_is_my_robot = this_is_my_robot
        self.i_feel_high_degree_of_personal_ownership_for_this_robot = i_feel_high_degree_of_personal_ownership_for_this_robot
        self.i_sense_that_i_own_this_robot = i_sense_that_i_own_this_robot
        self.robot_incorporates_a_part_of_myself = robot_incorporates_a_part_of_myself

        self.my_robot_supplies_my_need_for_help_through_a_help_function = my_robot_supplies_my_need_for_help_through_a_help_function
        self.my_robot_provides_competent_guidanceas_through_a_help_function = my_robot_provides_competent_guidanceas_through_a_help_function
        self.my_robot_provides_very_sensible_and_effective_advice_if_needed = my_robot_provides_very_sensible_and_effective_advice_if_needed
