from otree.api import *

doc = """
Basecamp: 1 Group, 1 Round, 1 Static MPCR Public Goods Game.
"""


class C(BaseConstants):
    NAME_IN_URL = 'vcm_public_goods'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    ENDOWMENT = cu(20)
    MPCR_LOW = 0.40
    MPCR_HIGH = 0.70
    SWITCH_ROUND = 6


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    if subsession.round_number == C.SWITCH_ROUND:
        subsession.group_randomly()
    elif subsession.round_number > 1:
        subsession.group_like_round(subsession.round_number - 1)
    
    for g in subsession.get_groups():
        if subsession.round_number < C.SWITCH_ROUND:
            g.mpcr = C.MPCR_LOW
        else:
            g.mpcr = C.MPCR_HIGH


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    mpcr = models.FloatField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0,
        max=C.ENDOWMENT,
        label="How much will you contribute to the group project?",
    )


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = group.total_contribution * group.mpcr

    for p in players:
        p.payoff = (C.ENDOWMENT - p.contribution) + group.individual_share


# PAGES
class Information(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 or player.round_number == C.SWITCH_ROUND

    @staticmethod
    def vars_for_template(player: Player):
        rounds_remaining = (C.NUM_ROUNDS - player.round_number + 1) if player.round_number == C.SWITCH_ROUND else (C.SWITCH_ROUND - 1)
        return dict(
            rounds_remaining=rounds_remaining,
            other_players=C.PLAYERS_PER_GROUP - 1,
            cumulative_payoff=sum([p.payoff for p in player.in_previous_rounds()])
        )


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            past_rounds=player.in_previous_rounds(),
            cumulative_payoff=sum([p.payoff for p in player.in_previous_rounds()])
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        # Rounding to 2 decimal places to avoid float precision issues (like 1.20000000000002)
        marginal_return = round(group.mpcr * C.PLAYERS_PER_GROUP, 2)
        group_account_payout = group.total_contribution * marginal_return
        return dict(
            endowment_kept=C.ENDOWMENT - player.contribution,
            marginal_return=marginal_return,
            group_account_payout=group_account_payout,
            past_rounds=player.in_all_rounds(),
            cumulative_payoff=sum([p.payoff for p in player.in_all_rounds()])
        )


class Summary(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            past_rounds=player.in_all_rounds(),
            total_cash=player.participant.payoff_plus_participation_fee(),
            cumulative_payoff=sum([p.payoff for p in player.in_all_rounds()])
        )


page_sequence = [Information, Contribute, ResultsWaitPage, Results, Summary]