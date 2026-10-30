from otree.api import *
import json
import random

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'mpl_example'
    players_per_group = None
    num_rounds = 1
    num_rows = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    response = models.StringField()
    selected_row = models.IntegerField()
    advice_purchased = models.BooleanField()
    selected_value = models.IntegerField()


def get_rows():
    # Define the rows for your MPL in one place.
    rows = []
    for i in range(1, Constants.num_rows + 1):
        left_option = f"Buy advice for ${i}"
        right_option = "Do not buy advice"

        rows.append({
            'id': i,
            'L': left_option,
            'R': right_option,
        })
    return rows


# PAGES

class MyPage(Page):
    form_model = 'player'
    form_fields = ['response']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            num_rows=Constants.num_rows,
            rows=get_rows(),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        response = json.loads(player.response)
        num_rows = len(response)
        selected_row_idx = random.randint(0, num_rows - 1)
        player.selected_row = selected_row_idx + 1  # 1-indexed

        # In MyPage: 0 = L (purchase), 1 = R (forego)
        player.advice_purchased = (response[selected_row_idx] == 0)
        player.selected_value = selected_row_idx + 1


class SingleSwitch(Page):
    form_model = 'player'
    form_fields = ['response']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            num_rows=Constants.num_rows,
            rows=get_rows(),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        response = json.loads(player.response)
        num_rows = len(response)
        selected_row_idx = random.randint(0, num_rows - 1)
        player.selected_row = selected_row_idx + 1  # 1-indexed

        # In SingleSwitch: 0 = L (purchase), 1 = R (forego)
        player.advice_purchased = (response[selected_row_idx] == 0)
        player.selected_value = selected_row_idx + 1


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        rows = get_rows()
        response = json.loads(player.response)
        for i, r_choice in enumerate(response):
            rows[i]['choice'] = r_choice

        return dict(
            num_rows=Constants.num_rows,
            rows=rows,
            selected_row=player.selected_row,
            is_purchase=player.advice_purchased,
            selected_value=player.selected_value,
        )


class SingleSwitchResults(Results):
    template_name = 'mpl/Results.html'


page_sequence = [MyPage, Results, SingleSwitch, SingleSwitchResults]
