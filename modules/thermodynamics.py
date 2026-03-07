"""Thermodynamic models for identity preservation and interaction costs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Boundary Integrity Model
# ---------------------------------------------------------------------------

@dataclass
class Boundary:
    """Agent boundary with integrity, leakage rate, and resistance profile.

    Parameters
    ----------
    integrity : float
        Boundary integrity B_i in energy units (> 0).
    leakage_rate : float
        Entropy leakage rate gamma_i (> 0).
    profile : str
        Resistance profile: 'uniform', 'hardening', or 'shell'.
    """
    integrity: float
    leakage_rate: float = 0.1
    profile: str = "uniform"

    def maintenance_cost(self) -> float:
        """Baseline maintenance cost C_maintain = gamma * B."""
        return self.leakage_rate * self.integrity

    def breach_work(self, depth: float = 1.0) -> float:
        """Work to breach boundary to depth d in [0, 1].

        W_breach(d) = B * integral_0^d f(s) ds
        where f(s) is the normalized resistance profile.
        """
        if not 0 <= depth <= 1:
            raise ValueError(f"Depth must be in [0, 1], got {depth}")
        if self.profile == "uniform":
            return self.integrity * depth
        elif self.profile == "hardening":
            # f(s) = 2s, integral = s^2
            return self.integrity * depth ** 2
        elif self.profile == "shell":
            # f(s) = 2(1-s), integral = 2d - d^2
            return self.integrity * (2 * depth - depth ** 2)
        else:
            raise ValueError(f"Unknown profile: {self.profile}")


# ---------------------------------------------------------------------------
# Tullock Contest Model
# ---------------------------------------------------------------------------

@dataclass
class ContestResult:
    """Result of a Tullock contest Nash equilibrium computation."""
    N: int
    E_j: float
    r: float
    investments: list[float]
    probabilities: list[float]
    payoffs: list[float]
    total_dissipation: float
    dissipation_ratio: float


def symmetric_contest_ne(E_j: float, N: int = 2, r: float = 1.0) -> ContestResult:
    """Compute Nash equilibrium of a symmetric N-agent Tullock contest.

    Parameters
    ----------
    E_j : float
        Energy value of the contested resource.
    N : int
        Number of contestants (>= 2).
    r : float
        Decisiveness parameter (> 0).

    Returns
    -------
    ContestResult
        Nash equilibrium investments, probabilities, payoffs, and dissipation.
    """
    if N < 2:
        raise ValueError("Need at least 2 agents")
    if E_j <= 0:
        raise ValueError("Resource value must be positive")
    if r <= 0:
        raise ValueError("Decisiveness must be positive")

    e_star = r * (N - 1) / (N ** 2) * E_j
    p_i = 1.0 / N
    payoff_i = p_i * E_j - e_star  # = E_j / N^2 * (1 + (1-r)(N-1)) simplified for r=1: E_j/N^2
    D_N = N * e_star

    return ContestResult(
        N=N,
        E_j=E_j,
        r=r,
        investments=[e_star] * N,
        probabilities=[p_i] * N,
        payoffs=[payoff_i] * N,
        total_dissipation=D_N,
        dissipation_ratio=D_N / E_j,
    )


def asymmetric_contest_ne_2(V_A: float, V_B: float) -> ContestResult:
    """Compute NE of a 2-agent Tullock contest with asymmetric valuations (r=1).

    Parameters
    ----------
    V_A, V_B : float
        Each agent's valuation of the resource.

    Returns
    -------
    ContestResult
    """
    e_A = V_A ** 2 * V_B / (V_A + V_B) ** 2
    e_B = V_A * V_B ** 2 / (V_A + V_B) ** 2
    p_A = V_A / (V_A + V_B)  # at NE with equal sigma, p_A = e_A/(e_A+e_B) = V_A/(V_A+V_B)
    p_B = 1 - p_A

    payoff_A = p_A * V_A - e_A
    payoff_B = p_B * V_B - e_B
    D = e_A + e_B

    return ContestResult(
        N=2,
        E_j=(V_A + V_B) / 2,  # average valuation
        r=1.0,
        investments=[e_A, e_B],
        probabilities=[p_A, p_B],
        payoffs=[payoff_A, payoff_B],
        total_dissipation=D,
        dissipation_ratio=D / max(V_A, V_B),
    )


# ---------------------------------------------------------------------------
# Friction Multiplier and System Loss
# ---------------------------------------------------------------------------

def friction_multiplier(delta_off: float, delta_def: float, kappa: float) -> float:
    """Compute the total friction multiplier Phi.

    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    """
    return 1.0 + (1.0 + kappa) * (delta_off + delta_def)


def system_loss(E_j: float, N: int, Phi: float, r: float = 1.0) -> float:
    """Total system loss L_system^(N) = Phi * (N-1)/N * E_j * r."""
    return Phi * (N - 1) / N * E_j * r


def net_system_value(E_j: float, N: int, Phi: float, r: float = 1.0) -> float:
    """Net system value V_net = E_j - L_system."""
    return E_j - system_loss(E_j, N, Phi, r)


def is_net_negative(N: int, Phi: float, r: float = 1.0) -> bool:
    """Check if conflict is net-negative: Phi * r > N/(N-1)."""
    return Phi * r > N / (N - 1)


def critical_N(Phi: float, r: float = 1.0) -> int:
    """Minimum N for which conflict is net-negative.

    We need the smallest integer N such that Phi*r > N/(N-1),
    equivalently N > Phi*r / (Phi*r - 1).  Because of the strict
    inequality, when Phi*r / (Phi*r - 1) is exactly an integer k,
    N* = k + 1 (not k).  Floating-point tolerance handles near-integer
    values from representational error.
    """
    Phi_r = Phi * r
    if Phi_r <= 1:
        return float('inf')  # never net-negative
    val = Phi_r / (Phi_r - 1)
    n_round = round(val)
    if abs(n_round - val) < 1e-9:
        # val is (effectively) an integer → strict inequality requires +1
        return n_round + 1
    return math.ceil(val)


# ---------------------------------------------------------------------------
# Network Friction (Trust) Model
# ---------------------------------------------------------------------------

@dataclass
class NetworkFriction:
    """Network friction coefficient dynamics model.

    Parameters
    ----------
    phi : float
        Current friction coefficient (>= 0).
    eta : float
        Friction sensitivity (how strongly violations increase phi).
    epsilon : float
        Friction recovery rate per period (0, 1).
    M : int
        Number of cooperative transactions per period.
    E_bar : float
        Average energy per transaction.
    """
    phi: float = 0.0
    eta: float = 0.01
    epsilon: float = 0.05
    M: int = 1000
    E_bar: float = 10.0

    @property
    def trust(self) -> float:
        """Network trust T = 1 / (1 + phi)."""
        return 1.0 / (1.0 + self.phi)

    def friction_tax(self) -> float:
        """Per-period friction tax = phi * M * E_bar."""
        return self.phi * self.M * self.E_bar

    def inject_violation(self, severity: float) -> None:
        """Inject a boundary violation of given severity."""
        self.phi += self.eta * severity

    def decay_step(self) -> None:
        """One period of friction recovery (no violations)."""
        self.phi *= (1.0 - self.epsilon)

    def cascade_cost(self, severity: float) -> float:
        """Total cascading cost of a single violation over full recovery.

        C_cascade = eta * v * M * E_bar / epsilon
        """
        return self.eta * severity * self.M * self.E_bar / self.epsilon

    def amplification_factor(self) -> float:
        """Ratio of cascade cost to direct cost: eta * M * E_bar / epsilon."""
        return self.eta * self.M * self.E_bar / self.epsilon

    def steady_state_phi(self, violation_rate: float, severity: float) -> float:
        """Steady-state phi under recurring violations.

        phi_inf = nu * eta * v / epsilon
        """
        return violation_rate * self.eta * severity / self.epsilon

    def collapse_threshold(self, coop_surplus: float, severity: float) -> float:
        """Critical violation rate nu* above which cooperation collapses.

        nu* = epsilon / (eta * v) * E_coop_net / (M * E_bar)
        """
        return (self.epsilon / (self.eta * severity)) * (coop_surplus / (self.M * self.E_bar))

    def half_life(self) -> float:
        """Number of periods for friction to halve."""
        if self.epsilon <= 0 or self.epsilon >= 1:
            return float('inf')
        return math.log(2) / math.log(1.0 / (1.0 - self.epsilon))

    def simulate(self, n_periods: int, violations: dict[int, float] | None = None) -> list[float]:
        """Simulate friction dynamics over n_periods.

        Parameters
        ----------
        n_periods : int
            Number of periods to simulate.
        violations : dict[int, float], optional
            Mapping from period -> violation severity. If None, no violations.

        Returns
        -------
        list[float]
            Friction coefficient at each period.
        """
        violations = violations or {}
        trace = []
        for t in range(n_periods):
            if t in violations:
                self.inject_violation(violations[t])
            trace.append(self.phi)
            self.decay_step()
        return trace
