from otree.api import *


doc = """
Video instructions app
"""


class C(BaseConstants):
    NAME_IN_URL = 'video'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    VIMEO_ID = '76979871'  # Replace with your Vimeo video ID


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    video_watched = models.BooleanField(initial=False, blank=True)


# PAGES
class myVideo(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            vimeo_id=C.VIMEO_ID,
        )


page_sequence = [myVideo]
