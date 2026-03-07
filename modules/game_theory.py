"""Game theory models for energy-based payoff analysis."""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# 2×2 Payoff Matrix
# ---------------------------------------------------------------------------

def payoff_matrix_2x2(e_resource, e_conflict_attack, e_conflict_defend, e_trade_cost):
    """
    Construct a 2-player payoff matrix with energy variables.

    Parameters
    ----------
    e_resource : float
        Energy value of the contested resource.
    e_conflict_attack : float
        Energy cost of attacking/stealing.
    e_conflict_defend : float
        Energy cost of defending.
    e_trade_cost : float
        Energy cost of cooperative trade/sharing.

    Returns
    -------
    dict
        Payoff matrix with strategies 'cooperate' and 'defect'.
    """
    # Cooperate-Cooperate: split resource, pay trade cost
    cc = (e_resource / 2 - e_trade_cost, e_resource / 2 - e_trade_cost)

    # Defect-Cooperate: defector takes all, pays attack cost; cooperator loses
    dc = (e_resource - e_conflict_attack, -e_conflict_defend)

    # Cooperate-Defect: mirror
    cd = (-e_conflict_defend, e_resource - e_conflict_attack)

    # Defect-Defect: both fight, resource may be destroyed
    dd = (
        e_resource / 2 - e_conflict_attack - e_conflict_defend,
        e_resource / 2 - e_conflict_attack - e_conflict_defend,
    )

    return {
        ("cooperate", "cooperate"): cc,
        ("defect", "cooperate"): dc,
        ("cooperate", "defect"): cd,
        ("defect", "defect"): dd,
    }


# ---------------------------------------------------------------------------
# Cooperation Threshold (Theorem 11)
# ---------------------------------------------------------------------------

def cooperation_threshold(T: float, R: float, P: float) -> float:
    """Minimum discount factor for cooperation NE (Theorem 11).

    delta* = (T - R) / (T - P)

    Parameters
    ----------
    T : float  — Temptation payoff (defect vs. cooperator)
    R : float  — Reward payoff (mutual cooperation)
    P : float  — Punishment payoff (mutual defection)

    Returns
    -------
    float
        Critical discount factor delta*.
    """
    return (T - R) / (T - P)


def cooperation_threshold_detection(
    T: float, R: float, P: float, p_detect: float,
) -> float:
    """Detection-adjusted cooperation threshold.

    delta*(p) = (T - R) / (p * (T - P))

    Parameters
    ----------
    p_detect : float
        Probability of detecting defection (0, 1].

    Returns
    -------
    float
        Adjusted critical discount factor. Returns inf if p_detect ~= 0.
    """
    if p_detect <= 0:
        return float('inf')
    return (T - R) / (p_detect * (T - P))


# ---------------------------------------------------------------------------
# Long-Run Value Functions (Theorem 15)
# ---------------------------------------------------------------------------

def long_run_cooperation_value(
    R: float, delta: float, n_periods: int,
) -> float:
    """Long-run value of sustained cooperation over n periods.

    V_coop = R * (1 - delta^(n+1)) / (1 - delta)

    For delta < 1 this is a finite geometric series.
    """
    if abs(delta - 1.0) < 1e-12:
        return R * (n_periods + 1)
    return R * (1.0 - delta ** (n_periods + 1)) / (1.0 - delta)


def long_run_defection_value(
    T: float, P: float, delta: float, n_periods: int,
) -> float:
    """Long-run value of defect-then-punish strategy over n periods.

    V_defect = T + P * delta * (1 - delta^n) / (1 - delta)

    First period: temptation payoff T.
    Remaining periods: punishment payoff P discounted.
    """
    if n_periods <= 0:
        return T
    if abs(delta - 1.0) < 1e-12:
        return T + P * n_periods
    return T + P * delta * (1.0 - delta ** n_periods) / (1.0 - delta)


def cooperation_advantage_ratio(
    R: float, T: float, P: float,
    delta_coop: float, delta_defect: float,
    n_periods: int = 50,
) -> float:
    """Ratio V_coop / V_defect over n_periods."""
    v_c = long_run_cooperation_value(R, delta_coop, n_periods)
    v_d = long_run_defection_value(T, P, delta_defect, n_periods)
    if v_d == 0:
        return float('inf')
    return v_c / v_d


# ---------------------------------------------------------------------------
# Social Welfare (N-agent)
# ---------------------------------------------------------------------------

def social_welfare_cooperation(N: int, R: float) -> float:
    """Total welfare under universal cooperation: N * R."""
    return N * R


def social_welfare_autocracy(N: int, T: float, S: float) -> float:
    """Total welfare under single-defector autocracy: T + (N-1)*S."""
    return T + (N - 1) * S


# ---------------------------------------------------------------------------
# Inclusive Fitness (Hamilton's Rule)
# ---------------------------------------------------------------------------

def inclusive_fitness(
    cost: float, benefit: float,
    relatedness: float, n_beneficiaries: int = 1,
) -> float:
    """Net fitness change from altruistic act.

    ΔW = -C + r * B * n

    Parameters
    ----------
    cost : float
        Cost to the altruist.
    benefit : float
        Benefit per recipient.
    relatedness : float
        Relatedness coefficient r in [0, 1].
    n_beneficiaries : int
        Number of beneficiaries.

    Returns
    -------
    float
        Net fitness change. Positive means the act is favored.
    """
    return -cost + relatedness * benefit * n_beneficiaries

