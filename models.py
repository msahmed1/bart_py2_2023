from __future__ import print_function
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Players(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
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
    
    # End of study questions
    this_is_my_robot = db.Column(db.Integer)
    i_feel_high_degree_of_personal_ownership_for_this_robot = db.Column(
        db.Integer)
    i_sense_that_i_own_this_robot = db.Column(db.Integer)
    robot_incorporates_a_part_of_myself = db.Column(db.Integer)

    i_feel_i_have_control_over_my_robot = db.Column(db.Integer)
    when_i_consider_my_robot_i_feel_in_control = db.Column(db.Integer)
    i_feel_that_i_have_no_control_over_my_robot = db.Column(db.Integer)
    i_feel_in_control_of_my_robot = db.Column(db.Integer)
    in_general_to_what_extent_do_you_have_control_over_your_robot = db.Column(
        db.Integer)

    i_feel_very_involved_in_my_relationship_with_my_robot_like_i_have_put_a_great_deal_into_it = db.Column(
        db.Integer)
    i_have_invested_a_great_deal_in_my_relationship_with_my_robot = db.Column(
        db.Integer)
    the_time_i_have_spent_on_my_robot_is_significant = db.Column(db.Integer)
    compared_to_other_things_i_have_spent_a_lot_of_effort_using_my_robot = db.Column(
        db.Integer)

    my_robot_has_the_functionality_I_need = db.Column(db.Integer)
    my_robot_has_the_required_features_for_my_tasks = db.Column(db.Integer)
    my_robot_has_the_ability_to_do_what_i_want_it_to_do = db.Column(db.Integer)

    my_robot_supplies_my_need_for_help_through_a_help_function = db.Column(
        db.Integer)
    my_robot_provides_competent_guidanceas_through_a_help_function = db.Column(
        db.Integer)
    my_robot_provides_very_sensible_and_effective_advice_if_needed = db.Column(
        db.Integer)

    my_robot_is_a_very_reliable_technology = db.Column(db.Integer)
    my_robot_does_not_fail_me = db.Column(db.Integer)
    my_robot_is_extremely_dependable = db.Column(db.Integer)

    def __init__(self, player_id, this_is_my_robot=None, i_feel_high_degree_of_personal_ownership_for_this_robot=None, i_sense_that_i_own_this_robot=None, robot_incorporates_a_part_of_myself=None, i_feel_i_have_control_over_my_robot=None, when_i_consider_my_robot_i_feel_in_control=None, i_feel_that_i_have_no_control_over_my_robot=None, i_feel_in_control_of_my_robot=None, in_general_to_what_extent_do_you_have_control_over_your_robot=None, i_feel_very_involved_in_my_relationship_with_my_robot_like_i_have_put_a_great_deal_into_it=None, i_have_invested_a_great_deal_in_my_relationship_with_my_robot=None, the_time_i_have_spent_on_my_robot_is_significant=None, compared_to_other_things_i_have_spent_a_lot_of_effort_using_my_robot=None, my_robot_has_the_functionality_I_need=None, my_robot_has_the_required_features_for_my_tasks=None, my_robot_has_the_ability_to_do_what_i_want_it_to_do=None, my_robot_supplies_my_need_for_help_through_a_help_function=None, my_robot_provides_competent_guidanceas_through_a_help_function=None, my_robot_provides_very_sensible_and_effective_advice_if_needed=None, my_robot_is_a_very_reliable_technology=None, my_robot_does_not_fail_me=None, my_robot_is_extremely_dependable=None, consent=False):
        self.player_id = player_id
        self.consent = consent

        self.this_is_my_robot = this_is_my_robot
        self.i_feel_high_degree_of_personal_ownership_for_this_robot = i_feel_high_degree_of_personal_ownership_for_this_robot
        self.i_sense_that_i_own_this_robot = i_sense_that_i_own_this_robot
        self.robot_incorporates_a_part_of_myself = robot_incorporates_a_part_of_myself

        self.i_feel_i_have_control_over_my_robot = i_feel_i_have_control_over_my_robot
        self.when_i_consider_my_robot_i_feel_in_control = when_i_consider_my_robot_i_feel_in_control
        self.i_feel_that_i_have_no_control_over_my_robot = i_feel_that_i_have_no_control_over_my_robot
        self.i_feel_in_control_of_my_robot = i_feel_in_control_of_my_robot
        self.in_general_to_what_extent_do_you_have_control_over_your_robot = in_general_to_what_extent_do_you_have_control_over_your_robot

        self.i_feel_very_involved_in_my_relationship_with_my_robot_like_i_have_put_a_great_deal_into_it = i_feel_very_involved_in_my_relationship_with_my_robot_like_i_have_put_a_great_deal_into_it
        self.i_have_invested_a_great_deal_in_my_relationship_with_my_robot = i_have_invested_a_great_deal_in_my_relationship_with_my_robot
        self.the_time_i_have_spent_on_my_robot_is_significant = the_time_i_have_spent_on_my_robot_is_significant
        self.compared_to_other_things_i_have_spent_a_lot_of_effort_using_my_robot = compared_to_other_things_i_have_spent_a_lot_of_effort_using_my_robot

        self.my_robot_has_the_functionality_I_need = my_robot_has_the_functionality_I_need
        self.my_robot_has_the_required_features_for_my_tasks = my_robot_has_the_required_features_for_my_tasks
        self.my_robot_has_the_ability_to_do_what_i_want_it_to_do = my_robot_has_the_ability_to_do_what_i_want_it_to_do

        self.my_robot_supplies_my_need_for_help_through_a_help_function = my_robot_supplies_my_need_for_help_through_a_help_function
        self.my_robot_provides_competent_guidanceas_through_a_help_function = my_robot_provides_competent_guidanceas_through_a_help_function
        self.my_robot_provides_very_sensible_and_effective_advice_if_needed = my_robot_provides_very_sensible_and_effective_advice_if_needed

        self.my_robot_is_a_very_reliable_technology = my_robot_is_a_very_reliable_technology
        self.my_robot_does_not_fail_me = my_robot_does_not_fail_me
        self.my_robot_is_extremely_dependable = my_robot_is_extremely_dependable


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
