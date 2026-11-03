from otree.api import *
import json
import random

doc = """
Standalone Risk Preferences Elicitation App (Pie Chart Lotteries).
"""


class C(BaseConstants):
    NAME_IN_URL = 'risk'
    PLAYERS_PER_GROUP = None
    # Format: (qid, [[L_probs], [L_payoffs]], [[R_probs], [R_payoffs]])
    QUESTIONS = [
        ('ls10_lr', [[50, 0, 50], [10, 30, 50]], [[10, 80, 10], [10, 30, 50]]),
        ('ls13', [[70, 0, 30], [10, 30, 50]], [[50, 40, 10], [10, 30, 50]]),
        ('ls18', [[40, 0, 60], [10, 30, 50]], [[10, 75, 15], [10, 30, 50]]),
        ('rae1', [[50, 50, 0], [0, 10, 20]], [[75, 0, 25], [0, 10, 20]]),
        ('rae10', [[0, 75, 25], [0, 35, 70]], [[50, 0, 50], [0, 35, 70]]),
    ]
    NUM_ROUNDS = len(QUESTIONS)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    qid = models.StringField()
    left_lottery = models.StringField()
    right_lottery = models.StringField()
    response = models.StringField(choices=['L', 'R'])
    random_number = models.IntegerField()
    paid_round = models.IntegerField()
    earnings = models.IntegerField()


# FUNCTIONS

def creating_session(subsession: Subsession):
    question = C.QUESTIONS[subsession.round_number - 1]
    assert sum(question[1][0]) == 100 and sum(question[2][0]) == 100, (
        f"Lottery probabilities in {question[0]} must sum to 100."
    )
    for p in subsession.get_players():
        p.qid = question[0]
        p.left_lottery = json.dumps(question[1])
        p.right_lottery = json.dumps(question[2])
        p.random_number = random.randint(1, 100)


def check_partition(random_int, original_partition):
    """
    Checks which part of the original partition a random integer (1..total) falls into.
    Returns the 0-based index of the partition segment.
    """
    total_length = sum(original_partition)
    if not 1 <= random_int <= total_length:
        return None

    cumulative_sum = 0
    for i, size in enumerate(original_partition):
        cumulative_sum += size
        if random_int <= cumulative_sum:
            return i
    return None


# PAGES

class MyPage(Page):
    form_model = 'player'
    form_fields = ['response']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            qid=player.qid,
            left_lottery=json.loads(player.left_lottery),
            right_lottery=json.loads(player.right_lottery),
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            left_lottery=json.loads(player.left_lottery),
            right_lottery=json.loads(player.right_lottery),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened or not player.field_maybe_none('response'):
            player.response = random.choice(['L', 'R'])

        # After participant makes all choices, select a round for payment and determine payoff.
        if player.round_number == C.NUM_ROUNDS:
            p_prior = random.choice(player.in_all_rounds())

            if p_prior.response == 'L':
                lottery = json.loads(p_prior.left_lottery)
            else:
                lottery = json.loads(p_prior.right_lottery)

            outcome = check_partition(p_prior.random_number, lottery[0])
            payoff = lottery[1][outcome]

            player.paid_round = p_prior.round_number
            player.earnings = payoff
            player.payoff = cu(payoff)


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        p_prior = player.in_round(player.paid_round)
        left_lottery = json.loads(p_prior.left_lottery)
        right_lottery = json.loads(p_prior.right_lottery)
        selected_lottery = left_lottery if p_prior.response == 'L' else right_lottery

        return dict(
            num_rounds=C.NUM_ROUNDS,
            paid_round=player.paid_round,
            qid=p_prior.qid,
            left_lottery=left_lottery,
            right_lottery=right_lottery,
            selected_lottery=selected_lottery,
            random_number=p_prior.random_number,
            earnings=player.earnings,
            response=p_prior.response,
        )

    @staticmethod
    def js_vars(player: Player):
        p_prior = player.in_round(player.paid_round)
        left_lottery = json.loads(p_prior.left_lottery)
        right_lottery = json.loads(p_prior.right_lottery)
        selected_lottery = left_lottery if p_prior.response == 'L' else right_lottery

        return dict(
            response=p_prior.response,
            left_lottery=left_lottery,
            right_lottery=right_lottery,
            selected_lottery=selected_lottery,
        )


page_sequence = [MyPage, Results]
