"""Dynamic-persistence accounting primitives for S2 (energy-flow balance).

Implements the discrete-time agent-boundary and resource-channel dynamics
from S2 §2.3 and TC-VIII def-resource-flow-dynamics.

Key identity (S2 §4.1.1 — First Law, eq. 4.1.1):
    sum_i [B_i(t+1) - B_i(t)] + sum_j alpha_j [R_j(t+1) - R_j(t)]
    = -sum_i gamma_i B_i  -  sum_i D_i  -  sum_j alpha_j delta_j R_j

CRITICAL (S2 §2.3 box): output-write debit is EMBEDDED in Delta^in.
    Delta^in_i = sum_j alpha_j [x^in_ij - x^out_ij]
No separate producer-cost term is added. Anything that adds c^prod_i
on top of Delta^in_i will break First-Law closure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray
from typing import Literal


# ---------------------------------------------------------------------------
# Per-step dynamics
# ---------------------------------------------------------------------------

def compute_delta_in(
    alpha_j_vec: np.ndarray,
    x_in_vec: np.ndarray,
    x_out_vec: np.ndarray,
) -> float:
    """Compute net inflow Delta^in_i for a single agent at one timestep.

    Delta^in_i = sum_j alpha_j * (x^in_ij - x^out_ij)

    The output-write debit is embedded here (via the -x^out term).
    Do NOT add any separate cost term on top of this result.

    Parameters
    ----------
    alpha_j_vec : np.ndarray, shape (n_resources,)
        Energy density alpha_j for each resource j. All > 0.
    x_in_vec : np.ndarray, shape (n_resources,)
        Input flows x^in_ij (joules of resource j read by agent i).
    x_out_vec : np.ndarray, shape (n_resources,)
        Output flows x^out_ij (joules of resource j written by agent i).

    Returns
    -------
    float
        Net energy inflow Delta^in_i in joules.
    """
    alpha_j_vec = np.asarray(alpha_j_vec, dtype=float)
    x_in_vec = np.asarray(x_in_vec, dtype=float)
    x_out_vec = np.asarray(x_out_vec, dtype=float)
    return float(np.dot(alpha_j_vec, x_in_vec - x_out_vec))


def step_persistence(
    B_i: float,
    delta_in: float,
    gamma_i: float,
    D_i: float,
) -> float:
    """Advance agent i's boundary-integrity by one discrete step.

    B_i(t+1) = B_i(t) + Delta^in_i(t) - gamma_i * B_i(t) - D_i(t)

    (S2 eq. 2.3; TC-VIII def-resource-flow-dynamics specialized to agent stock.)

    Parameters
    ----------
    B_i : float
        Current boundary integrity B_i(t) [joules].
    delta_in : float
        Net inflow Delta^in_i(t) [joules]. From compute_delta_in().
        Encodes output-write debit; do NOT add further cost terms.
    gamma_i : float
        Maintenance drain rate. gamma_i > 0 (TC-I).
    D_i : float
        Obligatory dissipation this step. D_i >= 0 (TC-VII Second Law).

    Returns
    -------
    float
        B_i(t+1).
    """
    return B_i + delta_in - gamma_i * B_i - D_i


def step_resource(
    R_j: float,
    total_x_out: float,
    total_x_in: float,
    delta_j: float,
) -> float:
    """Advance resource channel j by one discrete step.

    R_j(t+1) = R_j(t) + sum_i x^out_ij - sum_i x^in_ij - delta_j * R_j(t)

    (TC-VIII def-resource-flow-dynamics with psi_j = 0, closed substrate.)

    Parameters
    ----------
    R_j : float
        Current resource stock R_j(t) [joule-equivalents].
    total_x_out : float
        Total output into resource j: sum_i x^out_ij(t).
    total_x_in : float
        Total input from resource j: sum_i x^in_ij(t).
    delta_j : float
        Channel decay rate. delta_j in [0, 1). 0 = persistent channels.

    Returns
    -------
    float
        R_j(t+1).
    """
    return R_j + total_x_out - total_x_in - delta_j * R_j


# ---------------------------------------------------------------------------
# First-Law residual check (S2 §4.1.1 identity 4.1.1)
# ---------------------------------------------------------------------------

def first_law_residual(
    B_agents: np.ndarray,
    R_resources: np.ndarray,
    B_agents_next: np.ndarray,
    R_resources_next: np.ndarray,
    gamma_vec: np.ndarray,
    D_vec: np.ndarray,
    alpha_vec: np.ndarray,
    delta_vec: np.ndarray,
) -> float:
    """Compute the First-Law accounting residual (should be ~0).

    Identity (S2 eq. 4.1.1):
        LHS = sum_i [B_i(t+1)-B_i(t)] + sum_j alpha_j [R_j(t+1)-R_j(t)]
        RHS = -sum_i gamma_i B_i  -  sum_i D_i  -  sum_j alpha_j delta_j R_j
        residual = LHS - RHS  (should be 0 to numerical precision)

    Parameters
    ----------
    B_agents : np.ndarray, shape (N,)
        Agent boundary stocks at time t.
    R_resources : np.ndarray, shape (n,)
        Resource channel stocks at time t.
    B_agents_next : np.ndarray, shape (N,)
        Agent boundary stocks at time t+1.
    R_resources_next : np.ndarray, shape (n,)
        Resource channel stocks at time t+1.
    gamma_vec : np.ndarray, shape (N,)
        Maintenance drain rates per agent.
    D_vec : np.ndarray, shape (N,)
        Obligatory dissipation per agent at time t.
    alpha_vec : np.ndarray, shape (n,)
        Energy density per resource.
    delta_vec : np.ndarray, shape (n,)
        Channel decay rates per resource.

    Returns
    -------
    float
        Residual = LHS - RHS. Should be ~0 for correct implementation.
        Non-zero indicates a leak or double-counting bug.
    """
    B_agents = np.asarray(B_agents, dtype=float)
    R_resources = np.asarray(R_resources, dtype=float)
    B_agents_next = np.asarray(B_agents_next, dtype=float)
    R_resources_next = np.asarray(R_resources_next, dtype=float)
    gamma_vec = np.asarray(gamma_vec, dtype=float)
    D_vec = np.asarray(D_vec, dtype=float)
    alpha_vec = np.asarray(alpha_vec, dtype=float)
    delta_vec = np.asarray(delta_vec, dtype=float)

    lhs = (np.sum(B_agents_next - B_agents)
           + np.dot(alpha_vec, R_resources_next - R_resources))
    rhs = -(np.dot(gamma_vec, B_agents)
            + np.sum(D_vec)
            + np.dot(alpha_vec * delta_vec, R_resources))
    return float(lhs - rhs)


# ---------------------------------------------------------------------------
# Topology builders
# ---------------------------------------------------------------------------

TopologyKind = Literal["1-to-1", "1-to-many", "many-to-many", "cycle", "star"]


def build_topology(kind: TopologyKind, N: int) -> dict:
    """Build an adjacency / flow-structure for a named topology.

    Returns a dict with:
        'producers':  list of producer indices
        'consumers':  list of consumer indices (may overlap with producers)
        'edges':      list of (producer_idx, consumer_idx, resource_idx) triples
        'N_agents':   total number of agents
        'N_resources': total number of resource channels

    Parameters
    ----------
    kind : str
        One of "1-to-1", "1-to-many", "many-to-many", "cycle", "star".
    N : int
        Number of agents (or leaves for star). For "1-to-1" N means
        N producer-consumer pairs; for others N is the total count.

    Returns
    -------
    dict
        Topology descriptor. Use with simulate_substrate().
    """
    if kind == "1-to-1":
        # N producer-consumer pairs: 2N agents, N resources
        n_agents = 2 * N
        n_res = N
        producers = list(range(0, N))
        consumers = list(range(N, 2 * N))
        edges = [(i, N + i, i) for i in range(N)]

    elif kind == "1-to-many":
        # 1 producer, N consumers, 1 resource
        n_agents = 1 + N
        n_res = 1
        producers = [0]
        consumers = list(range(1, 1 + N))
        edges = [(0, c, 0) for c in consumers]

    elif kind == "many-to-many":
        # N producers, N consumers, N^2 resources (fully connected)
        n_agents = 2 * N
        n_res = N * N
        producers = list(range(0, N))
        consumers = list(range(N, 2 * N))
        edges = []
        for pi, p in enumerate(producers):
            for ci, c in enumerate(consumers):
                res_idx = pi * N + ci
                edges.append((p, c, res_idx))

    elif kind == "cycle":
        # N agents in a ring: agent i -> agent (i+1)%N via resource i
        n_agents = N
        n_res = N
        producers = list(range(N))
        consumers = list(range(N))
        edges = [(i, (i + 1) % N, i) for i in range(N)]

    elif kind == "star":
        # 1 hub, N leaves; hub produces for all leaves
        n_agents = 1 + N
        n_res = N
        producers = [0]
        consumers = list(range(1, 1 + N))
        edges = [(0, c, c - 1) for c in consumers]

    else:
        raise ValueError(f"Unknown topology kind: {kind!r}")

    return {
        "kind": kind,
        "N_agents": n_agents,
        "N_resources": n_res,
        "producers": producers,
        "consumers": consumers,
        "edges": edges,  # (producer, consumer, resource) triples
    }


# ---------------------------------------------------------------------------
# Simulation driver
# ---------------------------------------------------------------------------

def simulate_substrate(
    topology: dict,
    B_init: np.ndarray,
    R_init: np.ndarray,
    alpha_vec: np.ndarray,
    gamma_vec: np.ndarray,
    D_vec: np.ndarray,
    delta_vec: np.ndarray,
    flow_schedule: callable,
    n_steps: int,
) -> dict:
    """Simulate N-agent closed-substrate dynamics for n_steps.

    Applies step_persistence() and step_resource() at each step.
    Calls flow_schedule(t, topology, B, R) -> (x_in, x_out) where
    x_in[i,j] = flow agent i reads from resource j,
    x_out[i,j] = flow agent i writes to resource j.

    Returns
    -------
    dict with arrays:
        'B'   shape (n_steps+1, N_agents)
        'R'   shape (n_steps+1, N_resources)
        'first_law_residuals'  shape (n_steps,)
    """
    N_ag = topology["N_agents"]
    N_res = topology["N_resources"]

    B_hist = np.zeros((n_steps + 1, N_ag))
    R_hist = np.zeros((n_steps + 1, N_res))
    B_hist[0] = B_init.copy()
    R_hist[0] = R_init.copy()
    residuals = np.zeros(n_steps)

    for t in range(n_steps):
        B_t = B_hist[t]
        R_t = R_hist[t]

        x_in, x_out = flow_schedule(t, topology, B_t, R_t)
        # x_in, x_out: shape (N_ag, N_res)

        B_next = np.zeros(N_ag)
        for i in range(N_ag):
            delta_in_i = compute_delta_in(alpha_vec, x_in[i], x_out[i])
            B_next[i] = step_persistence(B_t[i], delta_in_i, gamma_vec[i], D_vec[i])

        R_next = np.zeros(N_res)
        for j in range(N_res):
            total_out = float(np.sum(x_out[:, j]))
            total_in = float(np.sum(x_in[:, j]))
            R_next[j] = step_resource(R_t[j], total_out, total_in, delta_vec[j])

        residuals[t] = first_law_residual(
            B_t, R_t, B_next, R_next,
            gamma_vec, D_vec, alpha_vec, delta_vec
        )

        B_hist[t + 1] = B_next
        R_hist[t + 1] = R_next

    return {"B": B_hist, "R": R_hist, "first_law_residuals": residuals}


# ---------------------------------------------------------------------------
# Dataclass agent/network representation (used by credit-as-resource-flow
# verify scripts S2/S3).
# ---------------------------------------------------------------------------

@dataclass
class ResourceFlowAgent:
    """Single agent in the resource-flow network.

    Attributes
    ----------
    agent_idx : int
    n_resources : int
    B_i : float
        Current boundary integrity (joules).
    gamma_i : float
        Maintenance cost coefficient (TC-I).
    D_i : float
        Obligatory dissipation per step (TC-VII def-thermodynamic-admissibility).
    energy_density : (n,) float
        Energy density alpha_j per resource (TC-VII; renamed e_j in composed-pseudogradient).
    eta_i : float
        Production efficiency (TC-VII, TC-XII).
    x_in : (n,) float
        Current input vector.
    x_out : (n,) float
        Current output vector.
    pi_star : (n,) float
        Flow-dependency prices at VE (TC-VII thm-shadow-price-decomposition).
    lambda_star : (n,) float
        Shared scarcity multiplier (uniform across agents at VE).
    eta_star : float
        Admissibility multiplier at VE.
    nu_star : (n,) float
        Provision-constraint multiplier at VE.
    B_floor : float
        Persistence margin floor (M_i = B_i - B_floor >= 0 required).
    """
    agent_idx: int
    n_resources: int
    B_i: float = 1.0
    gamma_i: float = 0.1
    D_i: float = 0.05
    energy_density: NDArray = field(default_factory=lambda: np.ones(3))
    eta_i: float = 1.0
    x_in: NDArray = field(default_factory=lambda: np.ones(3) * 0.5)
    x_out: NDArray = field(default_factory=lambda: np.ones(3) * 0.3)
    pi_star: NDArray = field(default_factory=lambda: np.ones(3) * 0.5)
    lambda_star: NDArray = field(default_factory=lambda: np.ones(3) * 0.3)
    eta_star: float = 0.1
    nu_star: NDArray = field(default_factory=lambda: np.zeros(3))
    B_floor: float = 0.1

    def __post_init__(self):
        n = self.n_resources
        for attr in ['energy_density', 'x_in', 'x_out', 'pi_star', 'lambda_star', 'nu_star']:
            val = getattr(self, attr)
            if isinstance(val, np.ndarray) and val.shape != (n,):
                setattr(self, attr, np.ones(n) * 0.3)

    @property
    def persistence_margin(self) -> float:
        return self.B_i - self.B_floor


@dataclass
class ResourceFlowNetwork:
    """Complete resource-flow network with N agents and resource stocks.

    Implements the TC-VIII/TC-VII network structure for S1/S2/S3 verification.

    Attributes
    ----------
    agents : list[ResourceFlowAgent]
    R_j : (n,) float
        Resource stock vector.
    delta_j : (n,) float
        Channel-decay parameters (TC-VIII; 0 = persistent-channel regime).
    topology : str
        '1to1', '1tomany', 'manytonamy', 'cycle', 'star', 'fully_connected'
    consumer_links : dict[int, list[int]]
        consumer_links[i] = list of consumers of agent i's output.
    producer_links : dict[int, list[int]]
        producer_links[i] = list of producers supplying agent i.
    """
    agents: list[ResourceFlowAgent]
    R_j: NDArray = field(default_factory=lambda: np.ones(3) * 2.0)
    delta_j: NDArray = field(default_factory=lambda: np.zeros(3))
    topology: str = 'cycle'
    consumer_links: dict = field(default_factory=dict)
    producer_links: dict = field(default_factory=dict)

    def __post_init__(self):
        N = len(self.agents)
        n = self.agents[0].n_resources
        if not self.consumer_links:
            self._build_default_topology()

    def _build_default_topology(self):
        """Build default topology based on self.topology string."""
        N = len(self.agents)
        if self.topology == '1to1' or N == 2:
            # Agent 0 produces, agent 1 consumes
            self.consumer_links = {0: [1], 1: []}
            self.producer_links = {0: [], 1: [0]}
        elif self.topology == '1tomany':
            # Agent 0 produces, agents 1..N-1 consume
            self.consumer_links = {0: list(range(1, N))}
            for j in range(1, N):
                self.consumer_links[j] = []
            self.producer_links = {0: []}
            for j in range(1, N):
                self.producer_links[j] = [0]
        elif self.topology == 'cycle':
            # Each agent i produces for agent (i+1) % N
            self.consumer_links = {i: [(i + 1) % N] for i in range(N)}
            self.producer_links = {i: [(i - 1) % N] for i in range(N)}
        elif self.topology == 'fully_connected':
            self.consumer_links = {i: [j for j in range(N) if j != i] for i in range(N)}
            self.producer_links = {i: [j for j in range(N) if j != i] for i in range(N)}
        else:
            # Default: cycle
            self.consumer_links = {i: [(i + 1) % N] for i in range(N)}
            self.producer_links = {i: [(i - 1) % N] for i in range(N)}

    @property
    def N(self) -> int:
        return len(self.agents)

    @property
    def n(self) -> int:
        return self.agents[0].n_resources

    def consumed_throughput(self, producer_i: int) -> NDArray:
        """x_cons_ij = min(x_out_ij, sum_{k in consumers} x_in_kj).

        Computes per-resource consumed throughput for producer i (S2 §2.2).
        """
        a_i = self.agents[producer_i]
        x_out = a_i.x_out
        consumers = self.consumer_links.get(producer_i, [])
        if not consumers:
            return np.zeros(self.n)
        total_consumption = np.sum([self.agents[c].x_in for c in consumers], axis=0)
        return np.minimum(x_out, total_consumption)

    def shortfall(self, producer_i: int) -> NDArray:
        """s_ij = (x_out_ij - x_cons_ij)_+ per S2 §2.2."""
        a_i = self.agents[producer_i]
        x_cons = self.consumed_throughput(producer_i)
        return np.maximum(0.0, a_i.x_out - x_cons)


# ---------------------------------------------------------------------------
# Dataclass-form step and accounting functions (S2 §2.3)
# ---------------------------------------------------------------------------

def _delta_i_in(agent: ResourceFlowAgent) -> NDArray:
    """Inflow term Delta_i^in = sum_j alpha_j * (x_in_ij - x_out_ij).

    Per S2 §2.3: output-write debit is EMBEDDED (not additive penalty).
    alpha_j = energy_density[j] per TC-VII.
    """
    e_j = agent.energy_density
    return e_j * (agent.x_in - agent.x_out)


def persistence_step(agent: ResourceFlowAgent) -> float:
    """B_i(t+1) = B_i(t) + Delta_i^in(t) - gamma_i * B_i(t) - D_i(t).

    Per S2 §2.3, discrete-time dynamic-persistence accounting.
    Failure-to-recover: Delta_i^in already embeds output-write debit.
    """
    delta_in = float(np.sum(_delta_i_in(agent)))
    return agent.B_i + delta_in - agent.gamma_i * agent.B_i - agent.D_i


def resource_stock_step(network: ResourceFlowNetwork, j: int) -> float:
    """R_j(t+1) = R_j(t) + sum_i x_out_ij - sum_i x_in_ij - delta_j * R_j(t).

    Per TC-VIII def-resource-flow-dynamics (S2 §2.3).
    """
    total_out = float(np.sum([a.x_out[j] for a in network.agents]))
    total_in = float(np.sum([a.x_in[j] for a in network.agents]))
    return network.R_j[j] + total_out - total_in - network.delta_j[j] * network.R_j[j]


def first_law_residual_network(network: ResourceFlowNetwork) -> dict:
    """Compute First-Law closure identity residual on a ResourceFlowNetwork.

    Dataclass-form companion to ``first_law_residual`` (array-form), used by
    S2 verification (S2 §4.1, sub-claim 1).

    Identity to verify:
      sum_i (B_i(t+1) - B_i(t)) + sum_j alpha_j (R_j(t+1) - R_j(t))
      = -sum_i (gamma_i B_i + D_i) - sum_j alpha_j delta_j R_j

    (Total energy change = negative sum of three obligatory leaks.)

    Returns dict with 'lhs', 'rhs', 'residual', 'closure_holds'.
    """
    N = network.N
    n = network.n

    # Agent boundary changes
    delta_B = []
    for a in network.agents:
        B_next = persistence_step(a)
        delta_B.append(B_next - a.B_i)

    # Resource stock changes
    delta_R = []
    for j in range(n):
        R_next = resource_stock_step(network, j)
        delta_R.append(R_next - network.R_j[j])

    # Mean energy density (use first agent's as representative)
    e_j = network.agents[0].energy_density

    # LHS: sum of energy changes in all buckets
    lhs = sum(delta_B) + float(np.dot(e_j, delta_R))

    # RHS: negative sum of obligatory leaks
    maintenance = sum(a.gamma_i * a.B_i for a in network.agents)
    dissipation = sum(a.D_i for a in network.agents)
    channel_decay = float(np.dot(e_j * network.delta_j, network.R_j))
    rhs = -(maintenance + dissipation + channel_decay)

    residual = abs(lhs - rhs)
    closure_holds = residual < 1e-10

    return {
        'lhs': lhs,
        'rhs': rhs,
        'residual': residual,
        'closure_holds': closure_holds,
        'delta_B': delta_B,
        'delta_R': delta_R,
        'maintenance': maintenance,
        'dissipation': dissipation,
        'channel_decay': channel_decay,
    }


def pi_star_consistency(agent: ResourceFlowAgent,
                         network: ResourceFlowNetwork) -> dict:
    """Verify pi*-consistency at VE (S2 §4.3.3, sub-claim 3).

    At the VE, agent i's B_i inflow rate matches sum_l pi*_il * x_cons_il
    (return-on-output via downstream consumption).

    Identity: sum_l pi*_il * x_cons_il ~ B_i(t+1) - B_i(t) + gamma_i*B_i + D_i

    Returns dict with 'pi_return', 'inflow_rate', 'residual'.
    """
    i = agent.agent_idx
    x_cons = network.consumed_throughput(i)
    pi_return = float(np.dot(agent.pi_star, x_cons))

    # Inflow rate = B_next - B_i + maintenance + dissipation
    B_next = persistence_step(agent)
    inflow_rate = B_next - agent.B_i + agent.gamma_i * agent.B_i + agent.D_i

    residual = abs(pi_return - inflow_rate)

    return {
        'pi_return': pi_return,
        'inflow_rate': inflow_rate,
        'residual': residual,
        'pi_consistent': residual < 0.5,  # approximate: depends on VE accuracy
    }
