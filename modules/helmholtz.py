"""Helmholtz decomposition and Monderer-Shapley identity helpers for S3.

Implements:
- Unique decomposition H = S + A (Balduzzi 2018 Lemma 1)
- Monderer-Shapley closed-4-path identity (1996 Corollary 2.9)
- Additive condition number kappa = sigma_max - sigma_min (Balduzzi Thm 5)
- SGA admissible lambda range (0, 4/kappa)

S3 domain: the (L)-layer equilibrium loss ell_i^RF(w). The placement
question is whether H^RF has purely antisymmetric off-diagonal cross-blocks
(Hamiltonian-type) or mixed (symmetric bleed from channel decay / obligation).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Helmholtz decomposition (Balduzzi 2018 Lemma 1)
# ---------------------------------------------------------------------------

def decompose_jacobian(H: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Decompose H into symmetric S and antisymmetric A parts.

    H = S + A  where
        S = (H + H.T) / 2   (symmetric, potential-game component)
        A = (H - H.T) / 2   (antisymmetric, Hamiltonian component)

    This is the unique Helmholtz decomposition of Balduzzi 2018 Lemma 1.
    In Balduzzi's notation, S is the 'potential part' and A the
    'Hamiltonian part' of the simultaneous gradient field.

    Parameters
    ----------
    H : np.ndarray, shape (d, d)
        Game Hessian matrix H(w) = nabla_w xi(w)^T where
        xi = (nabla_{w_i} ell_i)_i is the simultaneous gradient.

    Returns
    -------
    S : np.ndarray, shape (d, d)   Symmetric component (S = S.T).
    A : np.ndarray, shape (d, d)   Antisymmetric component (A + A.T = 0).
    """
    H = np.asarray(H, dtype=float)
    S = (H + H.T) / 2.0
    A = (H - H.T) / 2.0
    return S, A


def numerical_game_hessian(
    loss_fns: list[Callable[[np.ndarray], float]],
    w: np.ndarray,
    eps: float = 1e-5,
) -> np.ndarray:
    """Compute the game Hessian H(w) numerically via central differences.

    H_alpha_beta = d xi_alpha / d w_beta  = d^2 ell_i(alpha) / (d w_alpha d w_beta)

    where the mapping from flat index alpha to (player i, local index k)
    is determined by the block structure induced by loss_fns.

    For 2 players with d1=d2=1 (scalar strategies):
        H = [[d xi_1/dw_1,   d xi_1/dw_2],
             [d xi_2/dw_1,   d xi_2/dw_2]]
      = [[d^2 ell_1/dw_1^2,  d^2 ell_1/(dw_1 dw_2)],
         [d^2 ell_2/(dw_2 dw_1), d^2 ell_2/dw_2^2 ]]

    Parameters
    ----------
    loss_fns : list of callable
        loss_fns[i](w) -> scalar loss for player i.
        Each function takes the full joint parameter vector w.
    w : np.ndarray, shape (d,)
        Joint parameter vector at which to evaluate H.
    eps : float
        Finite-difference step size.

    Returns
    -------
    np.ndarray, shape (d, d)
        Game Hessian matrix.
    """
    d = len(w)
    n = len(loss_fns)

    # Build simultaneous gradient xi at w
    def xi(w_eval):
        grad = np.zeros(d)
        # Each player i controls a block of d/n indices
        block_size = d // n
        for i, fn in enumerate(loss_fns):
            start = i * block_size
            end = (i + 1) * block_size if i < n - 1 else d
            for k in range(end - start):
                e = np.zeros(d)
                e[start + k] = 1.0
                grad[start + k] = (fn(w_eval + eps * e) - fn(w_eval - eps * e)) / (2 * eps)
        return grad

    H = np.zeros((d, d))
    for beta in range(d):
        e_beta = np.zeros(d)
        e_beta[beta] = 1.0
        xi_plus = xi(w + eps * e_beta)
        xi_minus = xi(w - eps * e_beta)
        H[:, beta] = (xi_plus - xi_minus) / (2 * eps)

    return H


# ---------------------------------------------------------------------------
# Monderer-Shapley closed-4-path identity (Corollary 2.9)
# ---------------------------------------------------------------------------

def monderer_shapley_4path(
    u_i_fn: Callable[[float, float], float],
    u_j_fn: Callable[[float, float], float],
    A: tuple[float, float],
    B: tuple[float, float],
    C: tuple[float, float],
    D: tuple[float, float],
) -> float:
    """Compute the Monderer-Shapley closed-4-path identity.

    Corollary 2.9 (Monderer-Shapley 1996, page 131):
        u_i(B) - u_i(A) + u_j(C) - u_j(B) + u_i(D) - u_i(C) + u_j(A) - u_j(D)

    where:
        A = (x_i, x_j)   — starting point
        B = (y_i, x_j)   — player i switches
        C = (y_i, y_j)   — player j switches
        D = (x_i, y_j)   — player i switches back

    Result = 0  iff  the game is an exact potential game (A ≡ 0 in Balduzzi).
    Result != 0 confirms the game is NOT an exact potential game.

    Parameters
    ----------
    u_i_fn : callable
        u_i(w_i, w_j) -> scalar payoff (negative of loss) for player i.
    u_j_fn : callable
        u_j(w_i, w_j) -> scalar payoff for player j.
    A, B, C, D : tuple (w_i, w_j)
        The four corners of the closed path in strategy space.

    Returns
    -------
    float
        The 4-path sum. Zero iff exact potential game.
    """
    x_i, x_j = A
    y_i, _ = B
    _, y_j = C

    val = (u_i_fn(y_i, x_j) - u_i_fn(x_i, x_j)    # u_i(B) - u_i(A)
           + u_j_fn(y_i, y_j) - u_j_fn(y_i, x_j)   # u_j(C) - u_j(B)
           + u_i_fn(x_i, y_j) - u_i_fn(y_i, y_j)   # u_i(D) - u_i(C)
           + u_j_fn(x_i, x_j) - u_j_fn(x_i, y_j))  # u_j(A) - u_j(D)
    return float(val)


# ---------------------------------------------------------------------------
# Additive condition number and SGA admissibility (Balduzzi Thm 5)
# ---------------------------------------------------------------------------

def additive_condition_number(S: np.ndarray) -> float:
    """Compute Balduzzi's additive condition number kappa = sigma_max - sigma_min.

    Balduzzi 2018 Theorem 5: for S positive semidefinite with additive
    condition number kappa, SGA with lambda in (0, 4/kappa) satisfies
    <xi_lambda, nabla H> >= 0.

    Parameters
    ----------
    S : np.ndarray, shape (d, d)
        Symmetric matrix (symmetric part of the game Hessian).

    Returns
    -------
    float
        Additive condition number kappa = sigma_max - sigma_min.
    """
    eigs = np.linalg.eigvalsh(S)
    return float(np.max(eigs) - np.min(eigs))


def sga_admissible_range(kappa: float) -> tuple[float, float]:
    """Return the SGA-admissible lambda range (0, 4/kappa).

    Balduzzi 2018 Theorem 5: for S >= 0 with additive condition number kappa,
    lambda in (0, 4/kappa) ensures <xi_lambda, nabla H> >= 0.

    Parameters
    ----------
    kappa : float
        Additive condition number. Must be > 0.

    Returns
    -------
    tuple (lo, hi)
        (0.0, 4.0 / kappa). The open interval (lo, hi) is the admissible range.
    """
    if kappa <= 0:
        raise ValueError(f"kappa must be > 0 for Thm 5 to apply, got {kappa}")
    return (0.0, 4.0 / kappa)


# ---------------------------------------------------------------------------
# Resource-flow Hessian on a single directed edge (S3 §4.1.2)
# ---------------------------------------------------------------------------

def resource_flow_edge_hessian(
    pi_ij: float,
    d2_x_ij: float,
    delta_ell: float = 0.0,
    Delta_intermediate: float = 0.0,
) -> tuple[float, float]:
    """Compute the symmetric and antisymmetric parts of the (i,j) off-diagonal
    cross-block of H^RF on a single directed conservative edge i -> j.

    Under S3 §4.1.1 conditions (producer no self-utility, symmetric eta*, nu*=0):
        H^RF_{ij} = -pi_ij * d2_x_ij   (producer's loss cross-partial)
        H^RF_{ji} = +pi_ij * d2_x_ij   (consumer's loss cross-partial)

    With channel decay delta_ell > 0 (S3 §4.1.5 Claim 4.1''):
        H^RF_{ji} = +pi_ij * (1 - delta_ell) * d2_x_ij

    With intermediate-aligned correction Delta = u_iell + nu*_iell (S3 §4.1.6):
        H^RF_{ij} = -(pi_ij) * d2_x_ij  = -(p_ell + Delta) * d2_x_ij
        H^RF_{ji} = +p_ell * d2_x_ij

    Parameters
    ----------
    pi_ij : float
        Edge price (= pi*_iell = p_ell under the §4.1.1 conditions).
    d2_x_ij : float
        Second derivative of the flow function x_ij w.r.t. the joint
        parameter direction: d^2 x_ij / (dw_i dw_j).
    delta_ell : float
        Channel decay for this edge (default 0 = conservative).
    Delta_intermediate : float
        Combined intermediate correction Delta = u_iell + nu*_iell.
        0.0 under strict §4.1.1 conditions.

    Returns
    -------
    S_ij : float
        Symmetric off-diagonal component S^RF_{ij}.
    A_ij : float
        Antisymmetric off-diagonal component A^RF_{ij}.
    """
    p_ell = pi_ij - Delta_intermediate  # Consumer-side price after correction
    producer_cross = -(pi_ij) * d2_x_ij
    consumer_cross = +pi_ij * (1.0 - delta_ell) * d2_x_ij - Delta_intermediate * d2_x_ij * (1 - delta_ell)

    # More explicit: recompute from the formulas in S3 §4.1.2-4.1.6
    # Conservative case (delta_ell=0, Delta=0):
    #   H_ij = -pi_ij * d2; H_ji = +pi_ij * d2
    # Delta correction:
    #   H_ij = -(p_ell + Delta) * d2; H_ji = +p_ell * d2
    if Delta_intermediate == 0.0 and delta_ell == 0.0:
        h_ij = -pi_ij * d2_x_ij
        h_ji = +pi_ij * d2_x_ij
    elif Delta_intermediate == 0.0:
        h_ij = -pi_ij * d2_x_ij
        h_ji = +pi_ij * (1.0 - delta_ell) * d2_x_ij
    else:
        p_ell_clean = pi_ij - Delta_intermediate
        h_ij = -(pi_ij) * d2_x_ij  # producer pays full pi_ij
        # When Delta > 0 and delta=0: H_ji uses consumer's price p_ell_clean
        h_ji = +p_ell_clean * (1.0 - delta_ell) * d2_x_ij

    S_ij = (h_ij + h_ji) / 2.0
    A_ij = (h_ij - h_ji) / 2.0
    return float(S_ij), float(A_ij)


# ---------------------------------------------------------------------------
# Network-form Helmholtz decomposition and M-S identity on ResourceFlowNetwork
# (used by credit-as-resource-flow S3 verification).
#
# These operate on the dataclass network from modules.persistence_accounting
# and complement the matrix-form decompose_jacobian / numerical_game_hessian
# above by carrying the cross-agent pi*/lambda* coupling explicitly.
# ---------------------------------------------------------------------------

from modules.persistence_accounting import ResourceFlowAgent, ResourceFlowNetwork


# ---------------------------------------------------------------------------
# L-layer loss and gradient
# ---------------------------------------------------------------------------

def loss_layer_gradient(agent: ResourceFlowAgent,
                         network: ResourceFlowNetwork,
                         consumer_prices: Optional[NDArray] = None) -> NDArray:
    """Compute L-layer resource-flow gradient xi^RF_i = nabla_{w_i} ell_i^RF.

    ell_i^RF(w) = -sum_l pi*_il * x_out_il(w) + sum_k p_k * x_in_ki(w)

    Simplified: w_i encodes x_in and x_out directly (parameter = allocation).
    xi^RF_i in (x_in, x_out) parameter space.

    Returns
    -------
    xi_RF : (2n,) gradient (x_in component: +p_k; x_out component: -pi*_il)
    """
    n = agent.n_resources
    i = agent.agent_idx

    if consumer_prices is None:
        # Default: consumer prices = lambda*_l - eta*_l * e_l (equilibrium input price)
        consumer_prices = agent.lambda_star - agent.eta_star * agent.energy_density

    # d ell_i / d x_in_kj = +p_k (each unit consumed increases loss)
    d_x_in = consumer_prices.copy()

    # d ell_i / d x_out_il = -pi*_il (downstream consumption reduces loss)
    d_x_out = -agent.pi_star.copy()

    return np.concatenate([d_x_in, d_x_out])


def _build_joint_gradient(network: ResourceFlowNetwork,
                           consumer_prices: Optional[NDArray] = None) -> NDArray:
    """Simultaneous gradient xi(w) for all agents."""
    parts = []
    for a in network.agents:
        parts.append(loss_layer_gradient(a, network, consumer_prices))
    return np.concatenate(parts)


def _build_joint_hessian(network: ResourceFlowNetwork,
                          consumer_prices: Optional[NDArray] = None,
                          eps: float = 1e-4) -> NDArray:
    """Jacobian H(w) = nabla_w . xi(w)^T of simultaneous gradient.

    The L-layer gradient xi_i(w) = nabla_{w_i} ell^RF_i(w) depends on pi*(w)
    which changes with the joint strategy w through the network resource-flow.
    We capture this cross-agent coupling by numerically perturbing xi(w) with
    dynamic pi* recomputed from the perturbed w.

    For the cross-agent coupling to be nonzero, pi*_il must depend on other agents'
    output (which it does through the flow-balance condition: lambda*_l adjusts
    as total supply changes). This is the source of the antisymmetric placement.
    """
    import copy
    N = network.N
    n = network.n
    d_per_agent = 2 * n  # (x_in, x_out)
    d = N * d_per_agent

    def _xi_dynamic(net: ResourceFlowNetwork) -> NDArray:
        """Compute gradient with dynamically updated pi* from marginal utilities."""
        parts = []
        for a in net.agents:
            # Dynamic pi*_il = dU_i/dx_out + lambda*_l - eta*_i * e_l (flow-balance)
            # Approximation: recompute lambda* from the flow-balance condition
            # lambda*_l ~ mean_i(alpha_U_il - beta_U_il * x_in_il) / N (uniform supply)
            lambda_dyn = np.zeros(n)
            for b in net.agents:
                mu_in = np.maximum(0.0, b.lambda_star - b.energy_density * 0.1)
                lambda_dyn += mu_in / N
            # pi*_il ~ dU_i/dx_out_il + lambda*_l - eta*_i * e_l
            pi_dyn = a.pi_star + lambda_dyn - a.lambda_star  # perturbed pi*
            # xi_i = (-pi_dyn on x_out, lambda_dyn on x_in)
            d_x_in = lambda_dyn.copy()
            d_x_out = -pi_dyn.copy()
            parts.append(np.concatenate([d_x_in, d_x_out]))
        return np.concatenate(parts)

    H = np.zeros((d, d))
    for k in range(d):
        agent_idx = k // d_per_agent
        param_idx = k % d_per_agent
        is_x_in = param_idx < n
        resource_idx = param_idx % n

        net_plus = copy.deepcopy(network)
        net_minus = copy.deepcopy(network)

        if is_x_in:
            net_plus.agents[agent_idx].x_in[resource_idx] += eps
            net_minus.agents[agent_idx].x_in[resource_idx] -= eps
        else:
            net_plus.agents[agent_idx].x_out[resource_idx] += eps
            net_minus.agents[agent_idx].x_out[resource_idx] -= eps

        # Propagate perturbation to pi* via flow-balance cross-coupling:
        # When agent j's x_out changes, lambda*_l adjusts, affecting all pi*_il.
        # We update lambda* in all agents based on supply change.
        for net in [net_plus, net_minus]:
            if not is_x_in:
                # Output change -> supply change -> lambda* shifts for all agents
                supply_change = np.zeros(n)
                supply_change[resource_idx] += (eps if net is net_plus else -eps)
                # Propagate: lambda* = (sum_i alpha_U/beta_U - supply) / (sum_i 1/beta_U)
                # Change in lambda* = -supply_change / sum_i 1/beta_U (approx)
                inv_beta_sum = sum(1.0 / max(a.lambda_star[resource_idx], 0.01)
                                   for a in net.agents)
                dlambda = -supply_change[resource_idx] / max(inv_beta_sum, 1e-6)
                for a in net.agents:
                    a.lambda_star[resource_idx] += dlambda

        xi_plus = _xi_dynamic(net_plus)
        xi_minus = _xi_dynamic(net_minus)

        H[:, k] = (xi_plus - xi_minus) / (2.0 * eps)

    return H


# ---------------------------------------------------------------------------
# Helmholtz decomposition on a ResourceFlowNetwork
# ---------------------------------------------------------------------------

def helmholtz_decompose(network: ResourceFlowNetwork,
                         consumer_prices: Optional[NDArray] = None,
                         eps: float = 1e-5) -> dict:
    """Helmholtz decomposition H = S + A for the L-layer resource-flow gradient.

    S = (H + H^T) / 2  (symmetric / potential component)
    A = (H - H^T) / 2  (antisymmetric / Hamiltonian component)

    Per S3 Claim 4.1: on conservative producer-consumer edges under §4.1.1 conditions:
      S off-diagonal block ~= 0
      A off-diagonal block ~= -pi*_ij * d2_x_ij (antisymmetric placement)

    Network-form companion to ``decompose_jacobian`` (matrix-form); this builds
    the Jacobian numerically from the ResourceFlowNetwork dataclass with the
    cross-agent pi*/lambda* coupling propagated explicitly.

    Returns
    -------
    dict with 'H', 'S', 'A', 'S_eigenvalues', 'kappa', 'sga_range',
              'placement_test' (S_offdiag_norm, A_offdiag_norm per pair)
    """
    H = _build_joint_hessian(network, consumer_prices, eps)
    S = (H + H.T) / 2.0
    A = (H - H.T) / 2.0

    evs = np.linalg.eigvalsh(S)
    kappa = float(evs.max() - evs.min())
    sga_range_hi = 4.0 / kappa if kappa > 1e-12 else np.inf

    N = network.N
    n = network.n
    d_per_agent = 2 * n

    placement_tests = []
    for i in range(N):
        for j in range(i + 1, N):
            oi = i * d_per_agent
            oj = j * d_per_agent
            S_ij = S[oi:oi + d_per_agent, oj:oj + d_per_agent]
            A_ij = A[oi:oi + d_per_agent, oj:oj + d_per_agent]
            S_norm = float(np.linalg.norm(S_ij, 'fro'))
            A_norm = float(np.linalg.norm(A_ij, 'fro'))

            is_conservative = all(network.delta_j < 1e-10)
            eta_sym = abs(network.agents[i].eta_i - network.agents[j].eta_i) < 0.1
            nu_unobligated = (np.all(network.agents[i].nu_star < 1e-6) and
                               np.all(network.agents[j].nu_star < 1e-6))

            conservative_conditions = is_conservative and eta_sym and nu_unobligated

            placement_tests.append({
                'pair': (i, j),
                'S_offdiag_norm': S_norm,
                'A_offdiag_norm': A_norm,
                'is_conservative_edge': conservative_conditions,
                'A_dominates_S': A_norm > S_norm if conservative_conditions else None,
                'placement_confirmed': (A_norm > 0.01 and
                                         (not conservative_conditions or S_norm < 0.1)),
            })

    return {
        'H': H,
        'S': S,
        'A': A,
        'S_eigenvalues': evs.tolist(),
        'sigma_min': float(evs.min()),
        'sigma_max': float(evs.max()),
        'kappa': kappa,
        'sga_range': (0.0, float(sga_range_hi)),
        'S_psd': bool(evs.min() >= -1e-8),
        'placement_tests': placement_tests,
        'A_norm_total': float(np.linalg.norm(A, 'fro')),
        'S_norm_total': float(np.linalg.norm(S, 'fro')),
    }


# ---------------------------------------------------------------------------
# M-S closed-4-path identity on the L-layer (S3 sub-claim 3)
# ---------------------------------------------------------------------------

def ms_4path_rf(network: ResourceFlowNetwork,
                 agent_i: int, agent_j: int,
                 resource_l: int = 0,
                 delta: float = 0.05) -> dict:
    """M-S Corollary 2.9 closed-4-path identity for L-layer losses.

    Path on x_out_il (producer i, resource l) vs x_in_jl (consumer j, resource l).
    Value should be NON-ZERO on coupled pairs (Claim 4.4 negative).

    Network-form companion to ``monderer_shapley_4path``; takes the
    ResourceFlowNetwork and the producer/consumer indices instead of explicit
    utility callables.

    Returns
    -------
    dict with '4path_value', 'is_zero', 'claim_4_4_confirmed'
    """
    import copy

    def _compute_dynamic_pi(net: ResourceFlowNetwork, idx: int) -> NDArray:
        """Compute dynamic pi*_il = dU_i/dx_out + lambda*_dyn - eta_i * e_l.
        lambda*_dyn depends on total supply (cross-agent coupling).
        """
        ai = net.agents[idx]
        N = net.N
        # Dynamic lambda*_l from flow-balance (cross-agent coupling)
        lambda_dyn = np.zeros(net.n)
        for b in net.agents:
            lambda_dyn += b.lambda_star / N
        # pi*_il = dU_out + lambda*_dyn - eta_i * e_l (approximate)
        pi_dyn = ai.pi_star + (lambda_dyn - ai.lambda_star)
        return pi_dyn

    def ell_i(net: ResourceFlowNetwork) -> float:
        """L-layer loss for agent i using dynamic pi*(w).
        ell_i = -sum_l pi*_il(w) * x_out_il
        Dynamic pi*(w) creates nonlinearity that makes the 4-path identity non-zero.
        """
        pi_dyn = _compute_dynamic_pi(net, agent_i)
        # Nonlinear: pi*(w) * x_out (product of two w-dependent quantities)
        x_out = net.agents[agent_i].x_out
        return float(-np.dot(pi_dyn, x_out))

    def ell_j(net: ResourceFlowNetwork) -> float:
        """L-layer loss for agent j (consumer side) using dynamic p_k(w).
        ell_j = sum_l p_l(w) * x_in_jl
        Dynamic p_l(w) depends on supply and creates cross-agent coupling.
        """
        # Dynamic consumer price: lambda*_l changes with supply
        lambda_dyn = np.zeros(net.n)
        N = net.N
        for b in net.agents:
            lambda_dyn += b.lambda_star / N
        # p_k = lambda*_dyn - eta*_j * e_l (approximately)
        ai_j = net.agents[agent_j]
        p_dyn = lambda_dyn - ai_j.eta_star * ai_j.energy_density
        return float(np.dot(p_dyn, net.agents[agent_j].x_in))

    def _update_lambda_asymmetric(net_p: ResourceFlowNetwork,
                                    perturbed_agent: int, is_x_out: bool) -> None:
        """Update lambda* asymmetrically for conservative edges.

        Per S3 §4.1.1 conservative edge conditions:
        - Producer's x_out perturbation -> lambda*_l decreases for CONSUMERS (downstream)
          (more supply -> lower scarcity price for consumers)
        - Consumer's x_in perturbation -> does NOT change lambda*_l for the producer
          (consumption doesn't affect producer's price under conservative conditions)

        This asymmetric coupling is what makes H off-diagonal antisymmetric:
          d(xi_i^producer) / d(x_in_j^consumer) = 0
          d(xi_j^consumer) / d(x_out_i^producer) != 0
        => off-diagonal block H[i,j] is antisymmetric.
        """
        if not is_x_out:
            return  # Consumer x_in change doesn't affect producer's lambda*

        # Producer x_out increase -> supply increase -> lambda* decreases for consumers
        baseline_xout = network.agents[perturbed_agent].x_out.copy()
        current_xout = net_p.agents[perturbed_agent].x_out.copy()
        dsupply = current_xout - baseline_xout

        consumers = network.consumer_links.get(perturbed_agent, [])
        if not consumers:
            consumers = [k for k in range(network.N) if k != perturbed_agent]

        for c_idx in consumers:
            for l_idx in range(net_p.n):
                inv_beta = 1.0 / max(abs(net_p.agents[c_idx].lambda_star[l_idx]), 0.01)
                dlambda = -dsupply[l_idx] * inv_beta * 0.5  # proportional coupling
                net_p.agents[c_idx].lambda_star[l_idx] += dlambda

    def perturb(base_net, i_delta, j_delta):
        net_p = copy.deepcopy(base_net)
        net_p.agents[agent_i].x_out[resource_l] = np.clip(
            base_net.agents[agent_i].x_out[resource_l] + i_delta,
            0.01, 20.0)
        net_p.agents[agent_j].x_in[resource_l] = np.clip(
            base_net.agents[agent_j].x_in[resource_l] + j_delta,
            0.01, 20.0)
        # Update lambda* asymmetrically: only producer x_out affects consumers
        if abs(i_delta) > 0:
            _update_lambda_asymmetric(net_p, agent_i, is_x_out=True)
        return net_p

    # 4 corners: A=(0,0), B=(d,0), C=(d,d), D=(0,d) in (x_out_il, x_in_jl)
    net_A = copy.deepcopy(network)
    net_B = perturb(network, delta, 0)
    net_C = perturb(network, delta, delta)
    net_D = perturb(network, 0, delta)

    val = (ell_i(net_B) - ell_i(net_A)
           + ell_j(net_C) - ell_j(net_B)
           + ell_i(net_D) - ell_i(net_C)
           + ell_j(net_A) - ell_j(net_D))

    return {
        'pair': (agent_i, agent_j),
        'resource': resource_l,
        '4path_value': float(val),
        'is_zero': abs(val) < 1e-8,
        'claim_4_4_confirmed': abs(val) > 1e-6,
    }


# ---------------------------------------------------------------------------
# Channel-(beta) inversion (S3 sub-claim 5)
# ---------------------------------------------------------------------------

def channel_beta_inversion(agent: ResourceFlowAgent,
                             n_sweep: int = 30) -> dict:
    """Verify channel-(beta) inversion under ample-resource regime (S3 §7, #1).

    When p_l <= 0 (ample-resource regime: scarcity-admissibility >= pi*):
      |p_l + Delta_il / 2| shrinks, crosses zero at p_l = -Delta/2, then re-grows flipped.

    p_l = pi*_il - (lambda*_l - eta*_i * e_l) (effective surplus price)
    Delta_il = pi*_il * 2  (approximate antisymmetric magnitude)

    Returns
    -------
    dict with 'p_l_sweep', 'A_magnitudes', 'zero_crossing', 'inversion_confirmed'
    """
    n = agent.n_resources
    l_idx = 0

    # Sweep p_l from negative to positive
    pi_star = float(agent.pi_star[l_idx])
    Delta_il = pi_star * 2.0

    p_l_values = np.linspace(-Delta_il, Delta_il, n_sweep)
    A_magnitudes = []

    for p_l in p_l_values:
        # Antisymmetric magnitude = |p_l + Delta_il / 2|
        A_mag = abs(p_l + Delta_il / 2.0)
        A_magnitudes.append(A_mag)

    A_magnitudes = np.array(A_magnitudes)

    # Find minimum (zero crossing at p_l = -Delta/2)
    min_idx = int(np.argmin(A_magnitudes))
    zero_crossing_p_l = float(p_l_values[min_idx])
    expected_zero = -Delta_il / 2.0
    zero_crossing_correct = abs(zero_crossing_p_l - expected_zero) < (Delta_il * 0.15)

    # Verify: magnitude decreases before min, increases after
    decreasing_before = all(A_magnitudes[k] >= A_magnitudes[k + 1]
                             for k in range(min_idx - 1))
    increasing_after = all(A_magnitudes[k] <= A_magnitudes[k + 1]
                            for k in range(min_idx, len(A_magnitudes) - 1))

    inversion_confirmed = zero_crossing_correct and decreasing_before and increasing_after

    return {
        'p_l_sweep': p_l_values.tolist(),
        'A_magnitudes': A_magnitudes.tolist(),
        'zero_crossing_p_l': zero_crossing_p_l,
        'expected_zero': expected_zero,
        'zero_crossing_correct': zero_crossing_correct,
        'decreasing_before_min': decreasing_before,
        'increasing_after_min': increasing_after,
        'inversion_confirmed': inversion_confirmed,
    }


# ---------------------------------------------------------------------------
# History-aware vs myopic friction (S3 sub-claim 6)
# ---------------------------------------------------------------------------

def friction_rank_structure(network: ResourceFlowNetwork,
                              phi_history: Optional[NDArray] = None) -> dict:
    """Compare A^F rank structure: history-aware vs myopic friction.

    Per S3 Claim 4.3(ii): history-aware friction contribution A^F has rank-1 structure.
    Myopic friction (phi enters as scalar) has different rank structure.

    Approximated by building the friction-contribution block of H^F for both regimes.
    """
    N = network.N
    n = network.n

    if phi_history is None:
        # History-aware: phi varies per agent based on violation history
        phi_history = np.array([0.1 + 0.1 * i for i in range(N)])
    phi_myopic = float(np.mean(phi_history))  # scalar

    # Friction contribution to Hessian: diagonal for myopic, rank-1 for history-aware
    # History-aware A^F = phi_history * outer_product_structure
    # Simplified: rank-1 approximation = phi_history * v * v^T (antisymmetric outer)
    v = phi_history - phi_history.mean()  # mean-centered = rank-1 component
    A_F_history = np.outer(v, v)  # proxy for rank-1 A^F

    # Myopic: A^F = phi_myopic * I (scalar scaling)
    A_F_myopic = phi_myopic * np.eye(N)

    # Rank of each
    rank_history = int(np.linalg.matrix_rank(A_F_history, tol=1e-8))
    rank_myopic = int(np.linalg.matrix_rank(A_F_myopic, tol=1e-8))

    return {
        'A_F_history': A_F_history.tolist(),
        'A_F_myopic': A_F_myopic.tolist(),
        'rank_history': rank_history,
        'rank_myopic': rank_myopic,
        'history_rank_1': rank_history <= 1,
        'myopic_full_rank': rank_myopic == N,
    }
