from otree.api import *
import json
import random

doc = """
Minimal Quadratic Scoring Rule (QSR) Belief Elicitation Demo.

Demonstrates two conjecture types, two UI layouts, and two reward modes:
1. Exogenous truth + Horizontal choice-row UI + Direct Cash QSR:
   The correct bin is fixed and embedded directly with the question definition, and the QSR
   formula directly computes cash earnings in dollars ($).
2. Endogenous truth + Vertical column-chart UI + Points (Binarized Lottery Procedure / BLP):
   The correct bin is a function of oTree code (a computerized random die roll), and the QSR
   formula computes points (0 to 100) that determine the probability of winning a cash prize.
"""


class C(BaseConstants):
    NAME_IN_URL = 'beliefs'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TOKENS = 10

    # -------------------------------------------------------------------------
    # CASE 1: Exogenous Truth — Direct Cash QSR ($)
    # Score for bin k = EXOG_ALPHA + EXOG_BETA * (2 * p_k - sum_i(p_i^2))
    # With EXOG_ALPHA = 5.00 and EXOG_BETA = 5.00, cash earnings range from $0.00 to $10.00.
    # -------------------------------------------------------------------------
    EXOG_ALPHA = 5.0
    EXOG_BETA = 5.0
    EXOGENOUS_QUESTION = dict(
        prompt=(
            "In 1969, Ragnar Frisch and Jan Tinbergen were awarded the very first "
            "Nobel Memorial Prize in Economic Sciences. Which of the following economists "
            "was the sole recipient of the second prize in 1970?"
        ),
        labels=[
            "Milton Friedman",
            "Paul Samuelson",
            "Kenneth Arrow",
            "Friedrich Hayek",
        ],
        correct_bin=1,  # 0-indexed: "Paul Samuelson" is index 1 (Choice B)
    )

    # -------------------------------------------------------------------------
    # CASE 2: Endogenous Truth — Points QSR with Binarized Lottery Procedure (BLP)
    # With ENDOG_ALPHA = 50.0 and ENDOG_BETA = 50.0, scores range from 0.00 to 100.00 points.
    # -------------------------------------------------------------------------
    ENDOG_ALPHA = 50.0
    ENDOG_BETA = 50.0
    ENDOG_PRIZE = 10.00
    ENDOGENOUS_PROMPT = (
        "The computer has rolled a fair 6-sided die (faces 1 through 6). "
        "What number did the computer roll?"
    )
    ENDOGENOUS_LABELS = ["1", "2", "3", "4", "5", "6"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- Case 1: Exogenous question fields (Direct Cash QSR) ---
    response_exogenous = models.StringField()
    correct_bin_exogenous = models.IntegerField()
    accuracy_exogenous = models.FloatField()
    efficiency_exogenous = models.FloatField()
    earnings_exogenous = models.FloatField(initial=0.0)

    # --- Case 2: Endogenous die-roll fields (Points / BLP QSR) ---
    die_roll = models.IntegerField()
    response_endogenous = models.StringField()
    correct_bin_endogenous = models.IntegerField()
    accuracy_endogenous = models.FloatField()
    points_endogenous = models.FloatField(initial=0.0)
    win_prob_endogenous = models.FloatField()
    blp_draw_endogenous = models.FloatField()
    earnings_endogenous = models.FloatField(initial=0.0)


# =============================================================================
# SESSION INITIALIZATION & SCORING FUNCTIONS
# =============================================================================

def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        # Case 1: Truth comes directly from the exogenous question definition
        p.correct_bin_exogenous = C.EXOGENOUS_QUESTION['correct_bin']

        # Case 2: Truth is generated endogenously by oTree code (a random 6-sided die roll)
        p.die_roll = random.randint(1, 6)
        p.correct_bin_endogenous = p.die_roll - 1  # Map die face (1..6) to 0-based bin index (0..5)
        p.blp_draw_endogenous = random.random()


def calculate_qsr(tokens_list: list[int], correct_bin: int, alpha: float, beta: float):
    """
    Computes QSR metrics given a list of integer token allocations and the 0-based correct_bin.
    Returns (accuracy, score, efficiency).
    """
    probs = [t / C.NUM_TOKENS for t in tokens_list]
    accuracy = probs[correct_bin]
    sum_of_squares = sum(p ** 2 for p in probs)
    score = alpha + beta * ((2.0 * accuracy) - sum_of_squares)
    efficiency = score / (alpha + beta)
    return accuracy, score, efficiency


def score_exogenous(player: Player):
    """Direct Cash QSR: score is paid directly in dollars."""
    tokens = json.loads(player.response_exogenous)
    acc, cash_score, eff = calculate_qsr(
        tokens, player.correct_bin_exogenous, C.EXOG_ALPHA, C.EXOG_BETA
    )
    player.accuracy_exogenous = acc
    player.earnings_exogenous = cash_score
    player.efficiency_exogenous = eff
    player.payoff += cu(cash_score)


def score_endogenous(player: Player):
    """Points / BLP QSR: score is in points (0-100), determining probability of winning prize."""
    tokens = json.loads(player.response_endogenous)
    acc, points, win_prob = calculate_qsr(
        tokens, player.correct_bin_endogenous, C.ENDOG_ALPHA, C.ENDOG_BETA
    )
    player.accuracy_endogenous = acc
    player.points_endogenous = points
    player.win_prob_endogenous = win_prob
    player.earnings_endogenous = C.ENDOG_PRIZE if player.blp_draw_endogenous < win_prob else 0.0
    player.payoff += cu(player.earnings_endogenous)


# =============================================================================
# PAGES
# =============================================================================

class Exogenous(Page):
    """
    Case 1: Truth is exogenous and embedded with the question.
    Uses the horizontal choice-row QSR template with direct cash ($) payoffs.
    """
    template_name = 'beliefs/Horizontal.html'
    form_model = 'player'
    form_fields = ['response_exogenous']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            question_text=C.EXOGENOUS_QUESTION['prompt'],
            bin_labels=C.EXOGENOUS_QUESTION['labels'],
            bin_labels_json=json.dumps(C.EXOGENOUS_QUESTION['labels']),
            num_tokens=C.NUM_TOKENS,
            alpha=C.EXOG_ALPHA,
            beta=C.EXOG_BETA,
            form_field_name='response_exogenous',
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        score_exogenous(player)


class Endogenous(Page):
    """
    Case 2: Truth is a function of oTree code (computerized random die roll).
    Uses the vertical column-chart QSR template with points (BLP).
    """
    template_name = 'beliefs/Vertical.html'
    form_model = 'player'
    form_fields = ['response_endogenous']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            question_text=C.ENDOGENOUS_PROMPT,
            bin_labels_json=json.dumps(C.ENDOGENOUS_LABELS),
            num_tokens=C.NUM_TOKENS,
            alpha=C.ENDOG_ALPHA,
            beta=C.ENDOG_BETA,
            form_field_name='response_endogenous',
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        score_endogenous(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        exog_tokens = json.loads(player.response_exogenous)
        endog_tokens = json.loads(player.response_endogenous)

        exog_rows = []
        for idx, (label, tok) in enumerate(zip(C.EXOGENOUS_QUESTION['labels'], exog_tokens)):
            _, cash_val, _ = calculate_qsr(exog_tokens, idx, C.EXOG_ALPHA, C.EXOG_BETA)
            exog_rows.append(dict(
                index=idx,
                label=label,
                tokens=tok,
                score_display=f"${cash_val:.2f}",
                is_correct=(idx == player.correct_bin_exogenous),
            ))

        endog_rows = []
        for idx, (label, tok) in enumerate(zip(C.ENDOGENOUS_LABELS, endog_tokens)):
            _, pts_val, _ = calculate_qsr(endog_tokens, idx, C.ENDOG_ALPHA, C.ENDOG_BETA)
            endog_rows.append(dict(
                index=idx,
                label=label,
                tokens=tok,
                score_display=f"{pts_val:.2f} points",
                is_correct=(idx == player.correct_bin_endogenous),
            ))

        max_points = C.ENDOG_ALPHA + C.ENDOG_BETA

        return dict(
            # Case 1 summary (Direct Cash QSR)
            exog_prompt=C.EXOGENOUS_QUESTION['prompt'],
            exog_rows=exog_rows,
            exog_true_label=C.EXOGENOUS_QUESTION['labels'][player.correct_bin_exogenous],
            exog_accuracy_pct=f"{player.accuracy_exogenous * 100:.0f}%",
            exog_efficiency_pct=f"{player.efficiency_exogenous * 100:.1f}%",
            exog_earnings=f"${player.earnings_exogenous:.2f}",
            exog_max_cash=f"${(C.EXOG_ALPHA + C.EXOG_BETA):.2f}",
            # Case 2 summary (Points / BLP QSR)
            endog_prompt=C.ENDOGENOUS_PROMPT,
            endog_rows=endog_rows,
            endog_die_roll=player.die_roll,
            endog_true_label=C.ENDOGENOUS_LABELS[player.correct_bin_endogenous],
            endog_accuracy_pct=f"{player.accuracy_endogenous * 100:.0f}%",
            endog_points=f"{player.points_endogenous:.2f}",
            endog_max_points=f"{max_points:.0f}",
            endog_blp_threshold=f"{player.blp_draw_endogenous * max_points:.2f}",
            endog_won=(player.blp_draw_endogenous < player.win_prob_endogenous),
            endog_earnings=f"${player.earnings_endogenous:.2f}",
            total_earnings=f"${(player.earnings_exogenous + player.earnings_endogenous):.2f}",
        )


page_sequence = [Exogenous, Endogenous, Results]
