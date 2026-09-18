from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'input_examples'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    A = models.IntegerField(min=1, max=3, label='Enter integer between 1 and 3 inclusive')

    B = models.IntegerField(choices=[0, 1, 2, 3])

    C = models.IntegerField(choices=[[1, 'apple'],
                                     [2, 'banana'],
                                     [3, 'cranberry']])

    D = models.IntegerField(choices=[[1, 'apple'],
                                     [2, 'banana'],
                                     [3, 'cranberry']],
                            widget=widgets.RadioSelect)

    E = models.IntegerField(choices=[[1, 'apple'],
                                     [2, 'banana'],
                                     [3, 'cranberry']],
                            widget=widgets.RadioSelectHorizontal)





    F = models.IntegerField()







    G = models.IntegerField(choices=[[1, 'apple'],
                                     [2, 'banana'],
                                     [3, 'cranberry']])


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields = ['A', 'B', 'C', 'D', 'E']


class MyPage2(Page):
    form_model = 'player'
    form_fields = ['F']


class MyPage3(Page):
    form_model = 'player'
    form_fields = ['G']


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, MyPage2, MyPage3, ResultsWaitPage, Results]
