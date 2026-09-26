from otree.api import *

doc = """
Basecamp: 1 Group, 1 Round, 1 Static MPCR Public Goods Game.
"""


class C(BaseConstants):
    NAME_IN_URL = 'vcm_public_goods'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 6          # Basecamp: 1 round only
    ENDOWMENT = cu(20)
    MPCR = 0.40             # Basecamp: 1 static MPCR


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


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
    group.individual_share = group.total_contribution * C.MPCR

    for p in players:
        p.payoff = (C.ENDOWMENT - p.contribution) + group.individual_share


# PAGES
class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            past_rounds=player.in_previous_rounds(),
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment_kept=C.ENDOWMENT - player.contribution,
            past_rounds=player.in_all_rounds(),
        )


page_sequence = [Contribute, ResultsWaitPage, Results]