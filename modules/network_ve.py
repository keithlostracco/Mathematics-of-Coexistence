"""TC-VII KKT network variational-equilibrium solver.

Solves the social-planner welfare problem on a producer–consumer resource-flow
network and extracts the KKT multipliers (lambda*, eta*, pi*) per
TC-VII `thm-shadow-price-decomposition`.

This solver is used by the credit-as-resource-flow verification scripts (S1, S2,
S3) to obtain *genuine* multipliers at VE — rather than synthetic multipliers
constructed to make a formula balance — for cross-check tests where the same
quantity must be computable two independent ways.

Optimisation form
-----------------
We maximise the additive welfare

    W(x_in, x_out) = sum_i [ U_i(x_in_i, x_out_i) - cost_prod_i(x_out_i) ]
                   - sum_i gamma_i * B_i

subject to
    flow balance:    sum_i x_in[i, ell] - sum_i x_out[i, ell] = psi[ell]
                     for each resource ell
    production:      x_out[i, ell] <= f_i(B_i, x_in_i, ell)
    bounds:          x_in, x_out in [eps, x_max]

The dual variables of the equality constraints are TC-I's shared scarcity
shadow prices `lambda*[ell]`. The production-constraint multipliers are the
flow-dependency prices `pi*[i, ell]` per TC-VII `thm-shadow-price-decomposition`.
The admissibility-budget multiplier (TC-VII admissibility constraint
sum_ell alpha_ell * (x_out - x_in) <= 0) becomes `eta*[i]`.

Then, by TC-VII Theorem 3 stationarity,
    pi*[i, ell] = dU_i / dx_out[i, ell] |_*
which is the alignment-coefficient numerator after the lambda-eta-alpha
correction (S1 c-def).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Default Cobb–Douglas / quadratic-utility scenario
# ---------------------------------------------------------------------------

def cobb_douglas_production(
    B_i: float, x_in: NDArray, eta_i: float, beta: float = 0.0
) -> NDArray:
    """Cobb–Douglas production f_i(B, x_in) = eta * B^beta * x_in^(1-beta).

    Per S1 V8: residual is bounded and proportional to (1-beta).
    beta = 0 collapses to a Leontief-like proportional production.

    Returns per-resource production capacity (n,)."""
    eps = 1e-9
    if beta <= 0.0:
        return eta_i * np.maximum(x_in, eps)
    return eta_i * (max(B_i, eps) ** beta) * np.maximum(x_in, eps) ** (1.0 - beta)


# ---------------------------------------------------------------------------
# Network VE solver
# ---------------------------------------------------------------------------

def solve_network_ve(
    topology: dict,
    agent_params: list[dict],
    psi: Optional[NDArray] = None,
    cobb_douglas_beta: float = 0.0,
    x_bounds: tuple[float, float] = (0.01, 5.0),
    verbose: bool = False,
) -> dict:
    """Solve the TC-VII network VE via SLSQP and extract KKT multipliers.

    Parameters
    ----------
    topology : dict
        - 'N' : int — number of agents
        - 'n' : int — number of resources
        - 'produces' : list[int] (length N) — which resource each agent produces
        - 'consumes_mask' : (N, n) bool — which resources each agent consumes
    agent_params : list[dict] (length N)
        Each entry contains:
        - 'alpha_U' : (n,) marginal utility coefficient on input ell
        - 'beta_U'  : (n,) quadratic curvature on input ell
        - 'eta_i'   : production efficiency
        - 'energy_density' : (n,) alpha_ell (joules per unit resource)
        - 'B_i'     : current persistence margin
        - 'gamma_i' : maintenance cost
        - 'prod_cost' : per-unit output production cost (small).
    psi : (n,) optional exogenous inflow per resource (default zeros — closed).
    cobb_douglas_beta : float
        Cobb–Douglas mixing parameter for production. 0 = Leontief-like.

    Returns
    -------
    dict with keys
        - 'x_in_star'   : (N, n) optimal inputs
        - 'x_out_star'  : (N, n) optimal outputs (only produced index is nontrivial)
        - 'lambda_star' : (n,) scarcity shadow prices
        - 'eta_star'    : (N,) admissibility multipliers
        - 'pi_star'     : (N, n) flow-dependency prices = dU_i / dx_out at VE
        - 'success'     : bool
        - 'kkt_residual': max KKT stationarity residual
    """
    N = topology['N']
    n = topology['n']
    produces = topology['produces']
    consumes_mask = np.asarray(topology['consumes_mask'], dtype=bool)
    if psi is None:
        psi = np.zeros(n)

    # Variable layout: z = [x_in[0,0..n-1], ..., x_in[N-1,0..n-1],
    #                       x_out[0,0..n-1], ..., x_out[N-1,0..n-1]]
    n_vars_in = N * n
    n_vars_out = N * n
    n_vars = n_vars_in + n_vars_out

    def unpack(z: NDArray) -> tuple[NDArray, NDArray]:
        x_in = z[:n_vars_in].reshape(N, n)
        x_out = z[n_vars_in:].reshape(N, n)
        return x_in, x_out

    # --- Welfare objective ---
    def neg_welfare(z: NDArray) -> float:
        x_in, x_out = unpack(z)
        W = 0.0
        for i, p in enumerate(agent_params):
            alpha_U = p['alpha_U']
            beta_U = p['beta_U']
            mask = consumes_mask[i]
            # Quadratic utility on consumed inputs
            for ell in range(n):
                if mask[ell]:
                    W += (alpha_U[ell] * x_in[i, ell]
                          - 0.5 * beta_U[ell] * x_in[i, ell] ** 2)
            # Production cost: small linear cost on output produced
            W -= p.get('prod_cost', 0.05) * x_out[i, produces[i]]
            # Maintenance (constant, doesn't affect optimisation but kept for closure)
            W -= p['gamma_i'] * p['B_i']
        return -W

    # --- Flow-balance equality constraints (one per resource) ---
    def flow_balance(z: NDArray) -> NDArray:
        x_in, x_out = unpack(z)
        # sum_i x_in[i, ell] - sum_i x_out[i, ell] = psi[ell]
        s = np.zeros(n)
        for ell in range(n):
            total_in = x_in[:, ell].sum()
            total_out = x_out[:, ell].sum()
            s[ell] = total_in - total_out - psi[ell]
        return s

    # --- Production capacity inequalities: x_out_produced <= eta * B^beta * sum_in^(1-beta) ---
    def production_caps(z: NDArray) -> NDArray:
        x_in, x_out = unpack(z)
        caps = np.zeros(N)
        for i, p in enumerate(agent_params):
            ell_out = produces[i]
            # Per-input production share weighted by consumption mask
            mask = consumes_mask[i]
            x_in_total = x_in[i, mask].sum() if mask.any() else 0.0
            if cobb_douglas_beta <= 0.0:
                capacity = p['eta_i'] * x_in_total
            else:
                capacity = p['eta_i'] * (
                    max(p['B_i'], 1e-9) ** cobb_douglas_beta
                ) * (max(x_in_total, 1e-9) ** (1.0 - cobb_douglas_beta))
            # Constraint: capacity - x_out[i, ell_out] >= 0
            caps[i] = capacity - x_out[i, ell_out]
        return caps

    # --- Admissibility (TC-VII): sum_ell alpha_ell * (x_out - x_in) <= 0 per agent ---
    def admissibility(z: NDArray) -> NDArray:
        x_in, x_out = unpack(z)
        adm = np.zeros(N)
        for i, p in enumerate(agent_params):
            alpha_ell = p['energy_density']
            # adm_i = sum_ell alpha_ell * (x_in - x_out) >= 0  (input energy >= output)
            adm[i] = float(np.dot(alpha_ell, x_in[i] - x_out[i]))
        return adm

    # --- Force non-consumed inputs to zero (sparsity per consumes_mask) ---
    # We achieve this with tight bounds on those variables.
    bounds = []
    eps_b, x_max = x_bounds
    for i in range(N):
        for ell in range(n):
            if consumes_mask[i, ell]:
                bounds.append((eps_b, x_max))
            else:
                bounds.append((0.0, 1e-6))  # essentially zero
    # x_out: only produced index can be > 0
    for i in range(N):
        for ell in range(n):
            if ell == produces[i]:
                bounds.append((eps_b, x_max))
            else:
                bounds.append((0.0, 1e-6))

    # --- Initial guess ---
    z0 = np.ones(n_vars) * 0.3
    for i in range(N):
        for ell in range(n):
            if not consumes_mask[i, ell]:
                z0[i * n + ell] = 0.0
            if ell != produces[i]:
                z0[n_vars_in + i * n + ell] = 0.0

    constraints = [
        {'type': 'eq', 'fun': flow_balance},
        {'type': 'ineq', 'fun': production_caps},
        {'type': 'ineq', 'fun': admissibility},
    ]

    result = minimize(
        neg_welfare, z0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'ftol': 1e-10, 'maxiter': 500, 'disp': verbose},
    )

    x_in_star, x_out_star = unpack(result.x)

    # --- Extract dual variables from KKT stationarity ---
    # For each agent i and consumed resource ell:
    #     dU_i/dx_in[i, ell] = alpha_U[ell] - beta_U[ell] * x_in[i, ell]
    # KKT input stationarity (per TC-VII Theorem 3):
    #     dU_i/dx_in = lambda*[ell] - eta*[i] * alpha_ell
    #               + pi*[i, ell] * df_i/dx_in[ell]
    # KKT output stationarity:
    #     pi*[i, ell_out] = dU_i/dx_out + lambda*[ell_out] - eta*[i] * alpha_ell
    #                     - prod_cost
    # Under our problem, dU_i/dx_out[ell_out] = 0 directly (no self-utility on
    # own output); we therefore solve the linear system for (lambda, eta, pi).
    #
    # The cleanest extraction: solve for lambda*, eta* from input KKT, then
    # read pi*[i, ell_out] = dU_i/dx_out[i, ell_out]|_* from output KKT
    # (which is the alignment-coefficient numerator in S1's c-def).

    # Build the linear system for (lambda[0..n-1], eta[0..N-1]) using
    # input-KKT rows for every (i, ell) with consumes_mask[i, ell]:
    #     alpha_U[ell] - beta_U[ell] * x_in[i, ell] - prod_partial * pi[i]
    #     = lambda[ell] - eta[i] * alpha_ell
    # Treat pi[i] as the production-constraint multiplier (assumed equal to
    # dU_i/dx_out for now — refined in the post-solve loop below).

    # Marginal utilities at the solution
    marg_U_in = np.zeros((N, n))
    for i, p in enumerate(agent_params):
        for ell in range(n):
            if consumes_mask[i, ell]:
                marg_U_in[i, ell] = (
                    p['alpha_U'][ell] - p['beta_U'][ell] * x_in_star[i, ell]
                )

    # Production partial: dx_out[i, ell_out] / dx_in[i, ell] for consumed ell
    prod_partial = np.zeros((N, n))
    for i, p in enumerate(agent_params):
        mask = consumes_mask[i]
        x_in_total = x_in_star[i, mask].sum() if mask.any() else 0.0
        for ell in range(n):
            if not consumes_mask[i, ell]:
                continue
            if cobb_douglas_beta <= 0.0:
                prod_partial[i, ell] = p['eta_i']
            else:
                # df/dx_in[ell] = eta * B^beta * (1-beta) * x_in_total^(-beta)
                prod_partial[i, ell] = (
                    p['eta_i']
                    * (max(p['B_i'], 1e-9) ** cobb_douglas_beta)
                    * (1.0 - cobb_douglas_beta)
                    * max(x_in_total, 1e-9) ** (-cobb_douglas_beta)
                )

    # Stage 1: solve for (lambda, eta, pi_per_agent) jointly via least squares.
    # Unknowns: lambda[0..n-1], eta[0..N-1], pi[0..N-1] (one pi per agent,
    #           indexed by produced resource).
    n_unknowns = n + N + N
    # Check which constraints are binding via primal slacks.
    cap_slack = production_caps(result.x)             # capacity - x_out  (>=0)
    adm_slack = admissibility(result.x)               # adm (>=0)
    prod_binding = cap_slack < 1e-4
    adm_binding = adm_slack < 1e-4

    # ---------------------------------------------------------------------
    # Multiplier extraction strategy (per TC-VII Thm 3 + complementary slackness)
    # ---------------------------------------------------------------------
    # Step 1: lambda*[ell] - the scarcity shadow price, uniform across agents
    #         consuming resource ell (TC-I cor-symmetry-scarcity). Extract
    #         from input-KKT of the consuming agent with the slackest
    #         non-trivial constraints. We solve for (lambda, eta, mu) jointly
    #         with eta=0 where adm is slack, mu=0 where prod is slack.
    # Step 2: pi*_iell = TC-VII Thm 3 dual on production constraint = mu_i.
    #         When prod is binding, mu_i is determined by output-KKT:
    #           dU_i/dx_out_iell = lambda_ell - eta_i * alpha_ell - mu_i
    # ---------------------------------------------------------------------

    # Marginal utility on the produced output (no self-utility in our scenarios,
    # so dU/dx_out = -prod_cost).
    marg_U_out = np.zeros(N)
    for i, p in enumerate(agent_params):
        marg_U_out[i] = -p.get('prod_cost', 0.05)

    # Determine which multipliers are zero by complementary slackness.
    free_eta = adm_binding         # eta_i unknown only if adm binding
    free_mu = prod_binding         # mu_i unknown only if prod binding

    # Build the linear system using all available KKT rows.
    # Unknowns laid out as: [lambda (n), eta_free (sum of binding), mu_free (sum of binding)]
    eta_idx = {i: k for k, i in enumerate(np.where(free_eta)[0])}
    mu_idx = {i: k for k, i in enumerate(np.where(free_mu)[0])}
    n_eta_free = len(eta_idx)
    n_mu_free = len(mu_idx)
    n_unknowns = n + n_eta_free + n_mu_free

    def coef_row(coef_lambda, agent_eta, val_eta, agent_mu, val_mu):
        row = np.zeros(n_unknowns)
        for ell_k, v in coef_lambda.items():
            row[ell_k] = v
        if agent_eta is not None and agent_eta in eta_idx:
            row[n + eta_idx[agent_eta]] = val_eta
        if agent_mu is not None and agent_mu in mu_idx:
            row[n + n_eta_free + mu_idx[agent_mu]] = val_mu
        return row

    rows, rhs = [], []
    # Input stationarity: dU/dx_in[i,ell] = lambda_ell - eta_i*alpha - mu_i*prod_partial
    for i in range(N):
        for ell in range(n):
            if not consumes_mask[i, ell]:
                continue
            row = coef_row(
                coef_lambda={ell: 1.0},
                agent_eta=i, val_eta=-agent_params[i]['energy_density'][ell],
                agent_mu=i, val_mu=-prod_partial[i, ell],
            )
            rows.append(row)
            rhs.append(marg_U_in[i, ell])
    # Output stationarity: dU/dx_out = lambda_ell_out - eta_i*alpha - mu_i
    for i, p in enumerate(agent_params):
        ell_out = produces[i]
        row = coef_row(
            coef_lambda={ell_out: 1.0},
            agent_eta=i, val_eta=-p['energy_density'][ell_out],
            agent_mu=i, val_mu=-1.0,
        )
        rows.append(row)
        rhs.append(marg_U_out[i])

    A = np.asarray(rows)
    b = np.asarray(rhs)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)

    lambda_star = sol[:n]
    eta_star = np.zeros(N)
    for i, k in eta_idx.items():
        eta_star[i] = max(sol[n + k], 0.0)  # eta >= 0
    pi_per_agent = np.zeros(N)
    for i, k in mu_idx.items():
        pi_per_agent[i] = max(sol[n + n_eta_free + k], 0.0)  # mu >= 0

    # Build pi*[i, ell]: only the produced index carries pi
    pi_star = np.zeros((N, n))
    for i in range(N):
        pi_star[i, produces[i]] = pi_per_agent[i]

    # KKT residual on the constructed solution
    final_sol = np.zeros(n_unknowns)
    final_sol[:n] = lambda_star
    for i, k in eta_idx.items():
        final_sol[n + k] = eta_star[i]
    for i, k in mu_idx.items():
        final_sol[n + n_eta_free + k] = pi_per_agent[i]
    kkt_residual = float(np.max(np.abs(A @ final_sol - b))) if len(b) > 0 else 0.0

    return {
        'x_in_star': x_in_star,
        'x_out_star': x_out_star,
        'lambda_star': lambda_star,
        'eta_star': eta_star,
        'pi_star': pi_star,
        'pi_per_agent': pi_per_agent,
        'prod_partial': prod_partial,
        'success': bool(result.success),
        'kkt_residual': kkt_residual,
        'objective': float(-result.fun),
        'optimisation_message': str(result.message),
    }


# ---------------------------------------------------------------------------
# Convenience builders for the TC-class scenarios used by S1/S2/S3
# ---------------------------------------------------------------------------

def make_producer_verifier_scenario(
    N: int = 3, n: int = 3, scarce: bool = True, rng_seed: int = 0,
    psi_inflow: float = 1.0,
) -> tuple[dict, list[dict], np.ndarray]:
    """Construct a TC-class producer-verifier topology.

    Layout (N=3 default):
        agent 0 = upstream producer of resource 0 (consumes psi-injected res 2)
        agent 1 = mid producer of resource 1 (consumes res 0)
        agent 2 = downstream verifier (consumes res 1, produces res 2 which loops back)

    'scarce=True' (canonical S1 regime): high downstream demand makes
        production binding => pi* > 0 throughout.
    'scarce=False' (ample-resource regime): low demand, slack production =>
        pi* near zero, lambda* < eta* alpha possible.

    Returns
    -------
    topology, agent_params, psi
    """
    rng = np.random.default_rng(rng_seed)
    produces = [i % n for i in range(N)]
    consumes_mask = np.zeros((N, n), dtype=bool)
    for i in range(N):
        upstream = (i - 1) % n
        consumes_mask[i, upstream] = True

    topology = {
        'N': N,
        'n': n,
        'produces': produces,
        'consumes_mask': consumes_mask,
    }

    psi = np.zeros(n)
    psi[(0 - 1) % n] = psi_inflow  # inflow into resource agent 0 consumes

    # Scarce: high alpha_U + low eta_i (low production efficiency)
    # so the planner runs production at capacity => pi* > 0.
    if scarce:
        base_alpha = 5.0
        base_beta = 0.3
        base_eta = 0.5
    else:
        base_alpha = 0.4
        base_beta = 1.5
        base_eta = 3.0

    agent_params = []
    for i in range(N):
        alpha_U = np.zeros(n)
        beta_U = np.zeros(n)
        mask = consumes_mask[i]
        for ell in range(n):
            if mask[ell]:
                alpha_U[ell] = base_alpha + 0.1 * rng.standard_normal()
                beta_U[ell] = base_beta
        agent_params.append({
            'alpha_U': alpha_U,
            'beta_U': beta_U,
            'eta_i': base_eta + 0.02 * rng.standard_normal(),
            'energy_density': np.ones(n),
            'B_i': 1.5,
            'gamma_i': 0.1,
            'prod_cost': 0.05,
        })
    return topology, agent_params, psi


def make_two_agent_dyad(
    b_1: float = 0.5, b_2: float = 0.3, alpha_U: float = 2.0
) -> tuple[dict, list[dict]]:
    """Two-agent producer–consumer dyad with distinct utility curvatures.

    Used by S3 Check 2 to obtain b_1 != b_2 so the symmetric Hessian
    S = diag(2 b_1, 2 b_2) has sigma_min = 2 min(b_1, b_2),
    sigma_max = 2 max(b_1, b_2), kappa = 2 |b_1 - b_2|.

    Agent 0 produces resource 0, agent 1 consumes it. (n=1 collapsed)
    """
    # We embed n=1 (a single resource) using n=2 with agent 1 consuming r=0.
    N, n = 2, 2
    produces = [0, 1]
    consumes_mask = np.zeros((N, n), dtype=bool)
    consumes_mask[1, 0] = True  # agent 1 consumes resource 0
    consumes_mask[0, 1] = True  # agent 0 consumes resource 1 (closing the loop)

    topology = {'N': N, 'n': n, 'produces': produces, 'consumes_mask': consumes_mask}
    agent_params = [
        {
            'alpha_U': np.array([0.0, alpha_U]),
            'beta_U': np.array([0.0, 2.0 * b_1]),
            'eta_i': 1.0,
            'energy_density': np.ones(n),
            'B_i': 1.5,
            'gamma_i': 0.1,
            'prod_cost': 0.05,
        },
        {
            'alpha_U': np.array([alpha_U, 0.0]),
            'beta_U': np.array([2.0 * b_2, 0.0]),
            'eta_i': 1.0,
            'energy_density': np.ones(n),
            'B_i': 1.5,
            'gamma_i': 0.1,
            'prod_cost': 0.05,
        },
    ]
    return topology, agent_params
