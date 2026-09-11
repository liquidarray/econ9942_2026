from otree.api import *
import random

doc = """
A multi-round Rock-Paper-Scissors tournament against a computer opponent.
"""


class C(BaseConstants):
    NAME_IN_URL = 'rps_tournament'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10  # Tournament length


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    player_choice = models.StringField(
        choices=['Rock', 'Paper', 'Scissors'],
        label="Make your choice:"
    )
    computer_choice = models.StringField()
    # Explicitly tracking the computer's points to avoid "silent" variables
    computer_points = models.IntegerField(initial=0)


# --- PAGES (THE CONTROLLERS) ---

class Decision(Page):
    form_model = 'player'
    form_fields = ['player_choice']

    @staticmethod
    def vars_for_template(player: Player):
        # Calculate the score BEFORE the current round plays out
        prev_players = player.in_previous_rounds()
        return dict(
            human_total=sum([p.payoff or 0 for p in prev_players]),
            computer_total=sum([p.computer_points or 0 for p in prev_players])
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.computer_choice = random.choice(['Rock', 'Paper', 'Scissors'])

        p = player.player_choice
        c = player.computer_choice

        # Determine winner and assign round points
        if p == c:
            player.payoff = 0
            player.computer_points = 0
        elif (p == 'Rock' and c == 'Scissors') or \
                (p == 'Paper' and c == 'Rock') or \
                (p == 'Scissors' and c == 'Paper'):
            player.payoff = 1
            player.computer_points = 0
        else:
            player.payoff = 0
            player.computer_points = 1


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Calculate the score AFTER the current round has been scored
        all_players = player.in_all_rounds()
        return dict(
            human_total=sum([p.payoff or 0 for p in all_players]),
            computer_total=sum([p.computer_points or 0 for p in all_players])
        )


page_sequence = [Decision, Results]