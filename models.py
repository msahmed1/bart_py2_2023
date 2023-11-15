from __future__ import print_function
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Players(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)

    customise_first = db.Column(db.Boolean)
    testing = db.Column(db.Boolean)

    consent = db.Column(db.Boolean)
    game_completed = db.Column(db.Boolean, default=False)

    # Demographics
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))

    # Relationships
    balloon_total_inflates = db.relationship(
        'BalloonInflate', backref='player', lazy=True)
    game_round_surveys = db.relationship(
        'FinalSurvey', backref='player', lazy=True)

    def __init__(self, player_id, customise_first, testing, consent=False):
        self.player_id = player_id
        self.customise_first = customise_first
        self.testing = testing
        self.consent = consent


class BalloonInflate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.player_id'), nullable=False)
    balloon_id = db.Column(db.Integer, nullable=False)
    balloon_limit = db.Column(db.Integer, default=0)
    total_inflates = db.Column(db.Integer, default=0)

    game_round = db.Column(db.Integer, default=0)
    help_requested = db.Column(db.Boolean, default=False)
    robot_response = db.Column(db.Boolean, default=False)
    inflated_after_help_request = db.Column(db.Boolean, default=False)

    total_inflates_before_help_request = db.Column(db.Integer, default=0)
    # Calculate inflates_after_help_request by subtracting inflates_before_help_request from total_inflates

    time_to_decide = db.Column(db.Float, default=0)

    def __init__(self, player_id, balloon_id, balloon_limit, total_inflates=0, game_round=0, help_requested=False, robot_response=False, inflated_after_help_request=False):
        super(BalloonInflate, self).__init__()
        self.player_id = player_id
        self.balloon_id = balloon_id
        self.balloon_limit = balloon_limit
        self.total_inflates = total_inflates
        self.game_round = game_round

        self.help_requested = help_requested
        self.robot_response = robot_response
        self.inflated_after_help_request = inflated_after_help_request


class FinalSurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.player_id'), nullable=False)

    dislike_like = db.Column(db.Integer, default=0)
    unfriendly_friendly = db.Column(db.Integer, default=0)
    unkind_kind = db.Column(db.Integer, default=0)
    unpleasant_pleasant = db.Column(db.Integer, default=0)
    awful_nice = db.Column(db.Integer, default=0)

    incompetent_competent = db.Column(db.Integer, default=0)
    ignorant_knowledgeable = db.Column(db.Integer, default=0)
    iriresponsible_responsible = db.Column(db.Integer, default=0)
    unitelligent_intelligent = db.Column(db.Integer, default=0)
    foolish_sensible = db.Column(db.Integer, default=0)

    this_is_my_robot = db.Column(db.Integer, default=0)
    i_sense_that_i_own_this_robot = db.Column(db.Integer, default=0)
    this_robot_incorporates_a_part_of_myself = db.Column(db.Integer, default=0)

    i_am_confident_in_the_robot = db.Column(db.Integer, default=0)
    the_robot_has_integrity = db.Column(db.Integer, default=0)
    the_robot_gave_good_advice = db.Column(db.Integer, default=0)
    the_robot_is_reliable = db.Column(db.Integer, default=0)
    i_can_trust_the_robot = db.Column(db.Integer, default=0)
    i_am_familiar_with_the_robot = db.Column(db.Integer, default=0)

    freetext = db.Column(db.Text, nullable=True)

    def __init__(self, player_id, game_round=0, total_score=0, dislike_like=None, unfriendly_friendly=None, unkind_kind=None, unpleasant_pleasant=None, awful_nice=None, incompetent_competent=None, ignorant_knowledgeable=None, iriresponsible_responsible=None, unitelligent_intelligent=None, foolish_sensible=None, this_is_my_robot=None, i_sense_that_i_own_this_robot=None, this_robot_incorporates_a_part_of_myself=None, i_am_confident_in_the_robot=None, the_robot_has_integrity=None, the_robot_gave_good_advice=None, the_robot_is_reliable=None, i_can_trust_the_robot=None, i_am_familiar_with_the_robot=None):
        super(FinalSurvey, self).__init__()
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
        self.i_sense_that_i_own_this_robot = i_sense_that_i_own_this_robot
        self.this_robot_incorporates_a_part_of_myself = this_robot_incorporates_a_part_of_myself

        self.i_am_confident_in_the_robot = i_am_confident_in_the_robot
        self.the_robot_has_integrity = the_robot_has_integrity
        self.the_robot_gave_good_advice = the_robot_gave_good_advice
        self.the_robot_is_reliable = the_robot_is_reliable
        self.i_can_trust_the_robot = i_can_trust_the_robot
        self.i_am_familiar_with_the_robot = i_am_familiar_with_the_robot
