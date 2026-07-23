"""
composed_pseudogradient.py
==========================
Reusable primitives for the composed-pseudogradient surface derivation
verification scripts.

All TC-class scenario construction, pseudogradient computation, and structural
checks used by verify_01 through verify_07 live here. Scripts stay thin.

Reading-split references:
  Q1-Q4, Q6-Q7:  §6.1 factored-multiplier (phi common scalar, phi_mode="scalar")
  Q5:            §6.2 joint-violation-history (phi asymmetric, phi_mode="history")

Conservative-edge flow model (S3 §4.1, Claim 4.1)
-------------------------------------------------
The Lagrangian contribution from the resource-flow constraint on each
conservative producer-consumer edge (i, j) takes the form

    L_RF_ij_k = - pi*_ij_k * x_ij_k(w_i_k, w_j_k)

where x_ij_k is the *bilinear* edge-flow function

    x_ij_k(w_i_k, w_j_k) = 0.5 * w_i_k**2 * w_j_k**2     (1)

with w_*_k = x_in_*_k.  The simplest nonlinear bilinear form whose mixed
partial is genuinely a function of the state z:

    d2 x_ij_k / d w_i_k d w_j_k = 2 * w_i_k * w_j_k       (2)

Per S3 Claim 4.1 the off-diagonal Hessian block of the Lagrangian then
satisfies

    A_ij_k = - pi*_ij_k * d2 x_ij_k / d w_i_k d w_j_k     (3)

which is z-dependent (eq. 2), antisymmetric across the directed edge
(producer side carries -pi*, consumer side +pi*), and zero when
symmetrized -- placing the rotational coupling entirely in the
Helmholtz/Hamiltonian (antisymmetric) block.  The earlier linear model
x_ij_k = w_j_k gave d2 x_ij_k = 0, which is incompatible with eq. (3).
"""
from __future__ import annotations

import numpy as np
from typing import Callable, Optional, Tuple, Dict, Any


# ---------------------------------------------------------------------------
# Scenario construction
# ---------------------------------------------------------------------------

def build_tc_scenario(N: int, seed: int, n_resources: int = 3,
                      phi_low: float = 0.1, phi_high: float = 2.0,
                      Phi_override: Optional[float] = None) -> Dict[str, Any]:
    """Build a random TC-class parameter dict for N agents, n_resources resources.

    Returns a dict containing all TC primitives needed by compute_g / compute_G_L.

    Parameters
    ----------
    N : int           Number of agents.
    seed : int        RNG seed for reproducibility.
    n_resources : int Number of resource types.
    phi_low : float   Min value for friction scalar phi.
    phi_high : float  Max value for friction scalar phi.
    Phi_override :    If given, fix the friction multiplier Phi to this value
                      (useful for sweeping Phi in Q2 tests).

    TC-primitive mapping
    --------------------
    beta_ij_U  : (N, n) array — utility curvature (TC-I quadratic coeff beta)
    alpha_ij_U : (N, n) array — utility linear coeff alpha^U
    e_ij       : (N, N) array — pairwise contest-energy mixed partial E_ij
                 (>=0 under supermodular assumption 3.2')
    Phi        : scalar friction multiplier 1+kappa*(psi_off+psi_def)
    kappa      : scalar repair multiplier (TC-IV)
    psi_def    : scalar defensive-damage fraction (TC-IV)
    psi_off    : population-mean offensive-damage fraction (TC-XII aggregated)
    phi        : scalar network friction state (TC-IV law-of-motion freeze)
    omega      : (N,) weight vector for ambient-tax share (sum=1)
    M          : scalar number of transactions
    E_bar      : scalar mean energy
    alpha_floor: (N,) compliance floors alpha_i_min
    alpha_coop : (N, N) off-diag — cooperative utility curvature in compliance
    alpha_expl : (N, N) off-diag — exploitation utility curvature in compliance
    pi_star    : (N, n) flow-dependency prices at approximate VE
    f_jac      : (N, n, n) production Jacobians J_f_i (input->output)
    r_weights  : (N,) Rosen weight vector (uniform 1.0 for VE)
    theta      : list of per-agent type dicts
    """
    rng = np.random.default_rng(seed)

    # Utility curvature (TC-I quadratic: strictly positive -> concave)
    beta_ij_U = rng.uniform(0.5, 3.0, size=(N, n_resources))
    alpha_ij_U = rng.uniform(1.0, 5.0, size=(N, n_resources))

    # Pairwise contest-energy mixed partial E_ij (supermodular: >= 0)
    e_ij_raw = rng.uniform(0.0, 1.0, size=(N, N))
    e_ij = (e_ij_raw + e_ij_raw.T) / 2.0  # symmetrize
    np.fill_diagonal(e_ij, 0.0)

    # Friction multiplier: Phi = 1 + kappa*(psi_off + psi_def)
    # (v4: double-count removed; damage fractions delta -> psi. Repair term
    #  kappa*dB already re-supplies the destroyed dB, so the standalone dB is
    #  not charged again. See TC-IV def-repair-multiplier.)
    kappa = rng.uniform(0.2, 0.8)
    psi_def = rng.uniform(0.1, 0.4)
    psi_off = rng.uniform(0.1, 0.5)
    if Phi_override is None:
        Phi = 1.0 + kappa * (psi_off + psi_def)
    else:
        Phi = float(Phi_override)

    phi = rng.uniform(phi_low, phi_high)
    omega = rng.dirichlet(np.ones(N))  # sum-to-1 ambient-tax shares
    M = rng.uniform(5.0, 20.0)
    E_bar = rng.uniform(1.0, 5.0)

    # Compliance floors (alpha_i_min) in (0, 0.3)
    alpha_floor = rng.uniform(0.05, 0.3, size=N)

    # Cooperative / exploitation utility curvature in compliance (N x N off-diag)
    # Delta_ij = |d2 U_coop/d alpha_ij^2| + |d2 U_expl/d(1-alpha_ij)^2|
    alpha_coop = rng.uniform(0.5, 3.0, size=(N, N))  # diagonal irrelevant
    alpha_expl = rng.uniform(0.5, 3.0, size=(N, N))
    np.fill_diagonal(alpha_coop, 0.0)
    np.fill_diagonal(alpha_expl, 0.0)

    # Flow-dependency prices pi*_il (TC-VII shadow price decomposition)
    pi_star = rng.uniform(0.1, 2.0, size=(N, n_resources))

    # Production Jacobians J_f_i: (n_out x n_in) -> simplified to square (n x n)
    # concave production: eigenvalues of J_f_i negative (input -> output concave)
    f_jac = np.zeros((N, n_resources, n_resources))
    for i in range(N):
        A = rng.uniform(0.0, 0.5, size=(n_resources, n_resources))
        f_jac[i] = A + A.T + 0.1 * np.eye(n_resources)

    # Rosen weight vector (uniform = VE)
    r_weights = np.ones(N)

    # Per-agent type dicts (TC-XII theta_i)
    theta = []
    for i in range(N):
        theta.append({
            "beta_U": beta_ij_U[i],
            "alpha_U": alpha_ij_U[i],
            "alpha_floor": alpha_floor[i],
            "eta_i": rng.uniform(0.5, 2.0),
            "gamma_i": rng.uniform(0.1, 0.5),
            "psi_off_i": rng.uniform(0.1, 0.5),
            "omega_i": omega[i],
        })

    return {
        "N": N,
        "n": n_resources,
        "beta_ij_U": beta_ij_U,
        "alpha_ij_U": alpha_ij_U,
        "e_ij": e_ij,
        "Phi": Phi,
        "kappa": kappa,
        "psi_def": psi_def,
        "psi_off": psi_off,
        "phi": phi,
        "omega": omega,
        "M": M,
        "E_bar": E_bar,
        "alpha_floor": alpha_floor,
        "alpha_coop": alpha_coop,
        "alpha_expl": alpha_expl,
        "pi_star": pi_star,
        "f_jac": f_jac,
        "r_weights": r_weights,
        "theta": theta,
    }


# ---------------------------------------------------------------------------
# Per-agent payoff and gradient
# ---------------------------------------------------------------------------

def _utility_i(x_in: np.ndarray, alpha_ij_U: np.ndarray,
               beta_ij_U: np.ndarray) -> float:
    """TC-I quadratic utility U_i(x_in) = sum_j (alpha_U_j * x_j - beta_U_j/2 * x_j^2)."""
    return float(np.sum(alpha_ij_U * x_in - 0.5 * beta_ij_U * x_in**2))


def _grad_utility_i(x_in: np.ndarray, alpha_ij_U: np.ndarray,
                    beta_ij_U: np.ndarray) -> np.ndarray:
    """Gradient of TC-I quadratic utility w.r.t. x_in.

    The gradient alpha_U - beta_U * x_in goes to zero at x_in* = alpha_U/beta_U,
    which is the unconstrained optimum. The VE occurs at the shared-constraint-
    binding point determined by the welfare maximization equilibrium.
    """
    return alpha_ij_U - beta_ij_U * x_in


def _compliance_utility_grad(alpha_ij: np.ndarray, i: int, N: int,
                              alpha_coop: np.ndarray,
                              alpha_expl: np.ndarray) -> np.ndarray:
    """Gradient of cooperative+exploitation utility w.r.t. alpha_ij (pairwise).

    Per derivation 01 §3.3 boxed result:
      d phi_i / d alpha_ij = d U_coop/d alpha_ij - d U_expl/d(1-alpha_ij)

    Quadratic model:
      U_coop(alpha_ij) = c_ij * alpha_ij - c_ij/2 * alpha_ij^2
        d U_coop/d alpha = c_ij * (1 - alpha_ij)  >=0 (concave, peaks at alpha=1)

      U_expl(s) = e_ij * s - e_ij/2 * s^2  where s = 1-alpha_ij
        d U_expl/ds = e_ij * (1-s) = e_ij * alpha_ij
        d U_expl/d(1-alpha) = e_ij * alpha_ij  >=0 (concave in s)

    So: grad = c_ij*(1-alpha_ij) - e_ij*alpha_ij

    Diagonal Hessian: d^2 phi_i / d alpha^2 = -c_ij - e_ij < 0 (negative-definite
    as required by Assumption 2.3 of derivation 02; both terms strictly negative).
    """
    partners = [j for j in range(N) if j != i]
    grad = np.zeros(len(partners))
    for idx, j in enumerate(partners):
        c_ij = alpha_coop[i, j]
        e_ij_val = alpha_expl[i, j]
        a_ij = alpha_ij[idx]
        # d/d alpha_ij: c_ij*(1-alpha_ij) - e_ij*alpha_ij
        grad[idx] = c_ij * (1.0 - a_ij) - e_ij_val * a_ij
    return grad


def _contest_energy_grad_alpha_i(alpha_ij: np.ndarray, i: int, N: int,
                                  e_ij_matrix: np.ndarray,
                                  alpha_ji_vec: Optional[np.ndarray] = None) -> np.ndarray:
    """Gradient of contest energy e_i w.r.t. agent i's compliance alpha_ij.

    Pairwise model: e_ij = E_ij * (1-alpha_ij) * (1-alpha_ji)
    d e_ij / d alpha_ij = -E_ij * (1-alpha_ji)

    This creates the cross-agent Jacobian entry:
      d g_alpha_ij / d alpha_ji = -Phi * d^2 e_ij / d alpha_ij d alpha_ji
                                 = -Phi * E_ij   (per derivation 02 §3.2)
    which is the load-bearing off-diagonal source (ii) for the DSC check.

    alpha_ji_vec: array of alpha_ji values (j's compliance toward i) for each partner.
                  If None, uses symmetric assumption alpha_ji = alpha_ij.
    """
    partners = [j for j in range(N) if j != i]
    grad = np.zeros(len(partners))
    for idx, j in enumerate(partners):
        E_ij = e_ij_matrix[i, j]
        a_ij = alpha_ij[idx]
        if alpha_ji_vec is not None:
            a_ji = alpha_ji_vec[idx]
        else:
            # Symmetric assumption: alpha_ji ≈ alpha_ij (frozen cross-agent compliance)
            a_ji = a_ij
        # d e_ij / d alpha_ij = -E_ij * (1-alpha_ji)
        grad[idx] = -E_ij * (1.0 - a_ji)
    return grad


def per_agent_gradient(z_i: np.ndarray, scenario: Dict[str, Any],
                       i: int, z_full: Optional[np.ndarray] = None,
                       phi_mode: str = "scalar") -> np.ndarray:
    """Compute gradient nabla_i phi_i per Q1 §3.5.

    z_i layout: [x_in (n), x_out (n), alpha_ij (N-1), c_i (1)]
    z_full: full joint strategy (if provided, extracts actual alpha_ji from agent j)
    phi_mode: "scalar" (Q1 §6.1 factored-multiplier, default) or
              "history" (Q1 §6.2 joint-violation-history per-agent phi_i).
              In "history" mode the friction state phi_i couples back into the
              compliance gradient via -phi_i * omega_bar * E_bar (per §6.2
              consequence: nabla_i varphi_i not phi-independent at dynamic level).

    Returns gradient of same dimension.
    """
    N = scenario["N"]
    n = scenario["n"]
    beta_U = scenario["beta_ij_U"][i]
    alpha_U = scenario["alpha_ij_U"][i]
    Phi = scenario["Phi"]
    e_ij = scenario["e_ij"]
    alpha_coop = scenario["alpha_coop"]
    alpha_expl = scenario["alpha_expl"]
    d_i = _per_agent_dim(scenario)

    x_in = z_i[:n]
    alpha_ij = z_i[2*n:2*n + (N-1)]

    grad_x_in = _grad_utility_i(x_in, alpha_U, beta_U)
    x_out = z_i[n:2*n]
    grad_x_out = alpha_U * 0.5 - beta_U * 0.5 * x_out

    # Extract actual alpha_ji from full joint strategy if available
    alpha_ji_vec = None
    if z_full is not None:
        partners = [j for j in range(N) if j != i]
        alpha_ji_vec = np.zeros(N - 1)
        for idx, j in enumerate(partners):
            z_j = z_full[j * d_i:(j + 1) * d_i]
            alpha_j_toward_i = z_j[2*n:2*n + (N-1)]
            # Find i's index in j's partner list
            j_partners = [k for k in range(N) if k != j]
            i_idx = j_partners.index(i)
            alpha_ji_vec[idx] = alpha_j_toward_i[i_idx]

    # Compliance gradient: d U_coop/d alpha_ij - d U_expl/d(1-alpha_ij) - Phi * d e_i/d alpha_ij
    grad_coop_expl = _compliance_utility_grad(alpha_ij, i, N, alpha_coop, alpha_expl)
    grad_contest = _contest_energy_grad_alpha_i(alpha_ij, i, N, e_ij, alpha_ji_vec)
    grad_alpha = grad_coop_expl - Phi * grad_contest

    # §6.2 friction-coupling: per-agent phi_i couples into the compliance gradient
    # via the joint-violation-history ambient-tax term. This term has zero
    # contribution under §6.1 (frozen scalar) and a non-zero contribution under
    # §6.2 (phi_i = friction state depending on per-agent violation history).
    if phi_mode == "history":
        phi_i = scenario.get("phi_i_vec", None)
        if phi_i is None:
            phi_i_val = scenario.get("phi", 0.0)
        else:
            phi_i_val = float(phi_i[i])
        omega_bar = scenario["theta"][i]["omega_i"]
        E_bar = scenario["E_bar"]
        # d phi_i / d alpha_ij : phi_i affects ambient tax through omega_i which
        # depends on i's compliance history; here we model the dynamic-level
        # coupling as a constant negative drag on compliance gradient
        # (per §6.2 consequence: cross-agent coupling injected by joint-history).
        grad_alpha = grad_alpha - phi_i_val * omega_bar * E_bar

    grad_c = np.array([-1.0])

    return np.concatenate([grad_x_in, grad_x_out, grad_alpha, grad_c])


def _per_agent_dim(scenario: Dict[str, Any]) -> int:
    """Dimension of per-agent strategy vector."""
    return 2 * scenario["n"] + (scenario["N"] - 1) + 1


def compute_g(z: np.ndarray, scenario: Dict[str, Any],
              phi_mode: Optional[str] = None) -> np.ndarray:
    """Composed joint pseudogradient g(z, r; theta, phi) per Q1 §7.1.

    z: stacked strategy vector [z_1, z_2, ..., z_N] (total dim = N * d_i)
    phi_mode: "scalar" (§6.1, default) or "history" (§6.2). If None,
              read from scenario["phi_mode"] if present, else default to "scalar".
    Passes full z to per_agent_gradient so alpha_ji (j's compliance toward i)
    is correctly extracted from the joint strategy, creating the cross-agent
    Jacobian structure required for Q2/Q4 DSC checks.
    Returns g of same dimension.
    """
    N = scenario["N"]
    r_weights = scenario["r_weights"]
    d_i = _per_agent_dim(scenario)
    if phi_mode is None:
        phi_mode = scenario.get("phi_mode", "scalar")

    g_blocks = []
    for i in range(N):
        z_i = z[i * d_i:(i + 1) * d_i]
        grad_i = per_agent_gradient(z_i, scenario, i, z_full=z, phi_mode=phi_mode)
        g_blocks.append(r_weights[i] * grad_i)
    return np.concatenate(g_blocks)


# ---------------------------------------------------------------------------
# Lagrangian-gradient pseudogradient G_L (for Q2 DSC check)
# ---------------------------------------------------------------------------

def compute_G_L(z: np.ndarray, scenario: Dict[str, Any],
                pi_star: Optional[np.ndarray] = None,
                phi_mode: Optional[str] = None) -> np.ndarray:
    """Lagrangian-gradient G_L per Q1 §5.2 / derivation 02.

    At the VE, G_L differs from g by the resource-flow contribution
    R_i = J_f_i^T pi*_i which enters via dualized production constraint.
    Under multipliers-held-fixed reading (Rosen Thm 6 standard form),
    the multipliers pi*, lambda*, eta* are frozen at equilibrium values.

    Per Q1 §5.2 the Lagrangian gradient picks up:
      1. nabla_{x_in} L_i += J_f_i^T pi*_i  (constant-pi_star piece)
      2. The antisymmetric resource-flow edge coupling from S3 §4.1:
         on conservative producer-consumer edges, the off-diagonal cross-block
         of the G_L Jacobian carries a z-dependent contribution that maps to
         A_ij = -pi*_ij * d2 x_ij / dw_i dw_j  (S3 Claim 4.1).
         We realize this via the BILINEAR edge-flow x_ij_k = 0.5*w_i_k^2*w_j_k^2
         (see module docstring), giving Lagrangian contribution
             L_RF_ij_k = -pi*_ij_k * 0.5 * w_i_k^2 * w_j_k^2
         per directed conservative edge (i,j) on resource k.  The gradient
         delivered to agent i's x_in block is then
             d L_RF / d w_i_k = -pi*_ij_k * w_i_k * w_j_k^2     (z-dependent)
         and the cross-partial picks up the load-bearing edge-Hessian
             d2 L_RF / d w_i_k d w_j_k = -pi*_ij_k * 2 * w_i_k * w_j_k
         which is itself a function of z, as required by S3 Claim 4.1
         (cf. module docstring eq. 2-3).  Producer side carries -pi*,
         consumer side +pi*, exactly the directed-edge sign-flip placing
         the rotational coupling in the antisymmetric (Hamiltonian) block.
         Symmetrization kills it — so Q2/Q4 [G_L+G_L^T] is antisymmetric-
         invariant per S3 §4.4 — while the bare G_L Jacobian carries the
         rotational coupling Q3 and Q5 §4.4 need.

    The pi_star-weighted production Hessian term is included explicitly
    for non-Leontief future scenarios; under Leontief production f(x_in)=x_in
    its second derivative is zero so the contribution is structural.
    """
    N = scenario["N"]
    n = scenario["n"]
    r_weights = scenario["r_weights"]
    f_jac = scenario["f_jac"]
    d_i = _per_agent_dim(scenario)

    if pi_star is None:
        pi_star = scenario["pi_star"]
    if phi_mode is None:
        phi_mode = scenario.get("phi_mode", "scalar")

    g_L_blocks = []
    for i in range(N):
        z_i = z[i * d_i:(i + 1) * d_i]
        grad_i = per_agent_gradient(z_i, scenario, i, z_full=z, phi_mode=phi_mode).copy()

        # (1) Constant resource-flow contribution R_i = J_f_i^T pi*_i to input block
        R_i = f_jac[i].T @ pi_star[i]  # shape (n,)
        grad_i[:n] = grad_i[:n] + R_i

        # (2) S3 §4.1 antisymmetric edge coupling on conservative edges.
        # On each directed conservative edge (i,j) with i!=j the Lagrangian
        # carries
        #    L_RF_ij_k = - pi*_ij_k * x_ij_k(w_i_k, w_j_k)
        # with the BILINEAR flow x_ij_k = 0.5 * w_i_k^2 * w_j_k^2 chosen so
        # that the cross-partial d2 x_ij / d w_i d w_j is itself a function
        # of z (= 2*w_i_k*w_j_k), matching S3 Claim 4.1.  The directed
        # edge price is
        #    pi*_ij_k = pi*_i,k - pi*_j,k
        # so producer-i sees -pi* and consumer-j sees +pi* (antisymmetric
        # placement).  The gradient delivered to agent i's x_in block from
        # edge (i,j) is then
        #    d L_RF / d w_i_k = - pi*_ij_k * w_i_k * w_j_k^2
        # and to agent j's x_in block by mirror
        #    d L_RF / d w_j_k = - pi*_ij_k * w_i_k^2 * w_j_k.
        # The cross-partial Jacobian off-diagonal is
        #    J[i-w_k, j-w_k] = - pi*_ij_k * 2 * w_i_k * w_j_k
        # which is z-dependent (key audit requirement) and antisymmetric in
        # the i<->j swap: J[j-w_k, i-w_k] = -pi*_ji_k * 2 w_j_k w_i_k =
        # +pi*_ij_k * 2 w_i_k w_j_k = - J[i-w_k, j-w_k].  Symmetrization
        # therefore zeros this block (S3 §4.4 antisymmetric-invariance);
        # the bare G_L Jacobian retains the rotational coupling.
        flow_coupling = np.zeros(n)
        w_i = z_i[:n]
        for j in range(N):
            if j == i:
                continue
            z_j = z[j * d_i:(j + 1) * d_i]
            w_j = z_j[:n]
            # Directed edge price pi*_ij_k = pi*_i - pi*_j (producer minus consumer)
            edge_price = pi_star[i] - pi_star[j]
            # Bilinear flow x_ij_k = 0.5 * w_i_k^2 * w_j_k^2
            # => d L_RF / d w_i_k = -pi*_ij_k * w_i_k * w_j_k^2
            flow_coupling -= edge_price * w_i * (w_j ** 2)
        grad_i[:n] = grad_i[:n] + flow_coupling

        g_L_blocks.append(r_weights[i] * grad_i)
    return np.concatenate(g_L_blocks)


# ---------------------------------------------------------------------------
# Symmetrized Jacobian [G_L + G_L^T]
# ---------------------------------------------------------------------------

def symmetrized_jacobian(G_L_fn: Callable, z: np.ndarray, scenario: Dict[str, Any],
                         eps: float = 1e-5) -> np.ndarray:
    """Numerical [G_L + G_L^T] via central finite differences.

    G_L_fn: callable z -> G_L vector (shape d_total)
    Returns (d_total, d_total) symmetric matrix.
    """
    d = len(z)
    J = np.zeros((d, d))
    g0 = G_L_fn(z, scenario)
    for k in range(d):
        z_plus = z.copy(); z_plus[k] += eps
        z_minus = z.copy(); z_minus[k] -= eps
        J[:, k] = (G_L_fn(z_plus, scenario) - G_L_fn(z_minus, scenario)) / (2 * eps)
    return J + J.T


# ---------------------------------------------------------------------------
# Balduzzi decomposition
# ---------------------------------------------------------------------------

def balduzzi_decompose(J: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Symmetric / antisymmetric split S = (J+J^T)/2, A = (J-J^T)/2.

    Returns (S, A) where S = S^T, A = -A^T, J = S + A.
    """
    S = (J + J.T) / 2.0
    A = (J - J.T) / 2.0
    return S, A


# ---------------------------------------------------------------------------
# Monotonicity inner product
# ---------------------------------------------------------------------------

def monotonicity_inner_product(g_fn: Callable, x: np.ndarray, y: np.ndarray,
                                scenario: Dict[str, Any]) -> float:
    """Compute <-g(x) - (-g(y)), x - y> for Q4 monotonicity test.

    Positive => monotone at (x, y); negative => non-monotone.
    """
    neg_gx = -g_fn(x, scenario)
    neg_gy = -g_fn(y, scenario)
    return float(np.dot(neg_gx - neg_gy, x - y))


# ---------------------------------------------------------------------------
# Multi-start VE solver (Rosen-style gradient projection)
# ---------------------------------------------------------------------------

def projected_residual(g: np.ndarray, z: np.ndarray, scenario: Dict[str, Any],
                       R_budget: Optional[np.ndarray] = None) -> float:
    """Compute VE projected residual at z.

    The VE condition is g(z*) in N_R(z*). This means:
    - At interior points: g = 0
    - At box lower bound (e.g. x_in = 0): gradient can be negative (wants less, blocked)
    - At box upper bound (e.g. alpha = 1): gradient can be positive (wants more, blocked)
    - At shared constraint active boundary: gradient component in shared direction zeroed

    Per Assumption 2.4 (derivation 02): commitment direction treated as boundary.
    The compliance direction at alpha=1 (full cooperation): g_alpha = 0 is expected.
    The x_in direction: at the shared resource constraint, g_x_in = lambda* (uniform).
    The VE residual measures how far the compliance / x_out blocks are from stationarity
    and how much the x_in block deviates from the uniform-multiplier condition.
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    alpha_floor = scenario["alpha_floor"]

    g_proj = g.copy()
    for i in range(N):
        start = i * d_i
        # x_in: if at upper bound AND gradient positive, zero out
        # if at lower bound AND gradient negative, zero out
        for k in range(n):
            if z[start + k] <= 1e-5 and g[start + k] < 0:
                g_proj[start + k] = 0.0
            if R_budget is not None and z[start + k] >= R_budget[k] / N - 1e-4 and g[start + k] > 0:
                g_proj[start + k] = 0.0
        # x_out: at lower bound
        for k in range(n):
            if z[start + n + k] <= 1e-5 and g[start + n + k] < 0:
                g_proj[start + n + k] = 0.0
        # alpha in [alpha_floor, 1]: zero out at boundaries
        for jj in range(N - 1):
            idx = start + 2*n + jj
            af = alpha_floor[i]
            if z[idx] <= af + 1e-5 and g[idx] < 0:
                g_proj[idx] = 0.0
            if z[idx] >= 1.0 - 1e-5 and g[idx] > 0:
                g_proj[idx] = 0.0
        # c_i: at lower bound 0 gradient is -1 (wants less), zero out
        c_idx = start + 2*n + (N-1)
        if z[c_idx] <= 1e-5 and g[c_idx] < 0:
            g_proj[c_idx] = 0.0
        if z[c_idx] >= 1.0 - 1e-5 and g[c_idx] > 0:
            g_proj[c_idx] = 0.0
    return float(np.linalg.norm(g_proj))


def flow_balance(z: np.ndarray, scenario: Dict[str, Any]) -> np.ndarray:
    """Compute shared flow-balance vector s_j = sum_i x_in_ij - sum_i x_out_ij.

    Returns (n,) array. At VE the flow-balance constraint enforces s_j = 0
    (modulo exogenous psi_j and delta_j*R_j* terms, treated as constants).
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    s = np.zeros(n)
    for i in range(N):
        start = i * d_i
        s += z[start:start + n]            # x_in_i
        s -= z[start + n:start + 2*n]      # x_out_i
    return s


def estimate_lambda_star(z: np.ndarray, scenario: Dict[str, Any]) -> np.ndarray:
    """Estimate the shared-constraint multiplier lambda*_j from KKT.

    At the VE, the input-stationarity condition gives g_x_in_ij = lambda*_j
    uniform across agents i (TC-I `thm-variational-equilibrium`(a)).
    We take the average of grad_x_in across agents on each resource j.
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    g = compute_g(z, scenario)
    lam = np.zeros(n)
    for j in range(n):
        vals = []
        for i in range(N):
            start = i * d_i
            vals.append(g[start + j])
        lam[j] = float(np.mean(vals))
    return lam


def solve_ve_constrained(scenario: Dict[str, Any],
                         rng: Optional[np.random.Generator] = None,
                         n_starts: int = 20, max_iter: int = 5000,
                         lr: float = 0.05,
                         tol: float = 1e-6) -> Dict[str, Any]:
    """Solve VE with the shared flow-balance equality constraint enforced.

    Implementation: augmented-Lagrangian outer loop on projected gradient
    ascent. The shared constraint is s_j(z) = 0 for each resource j.

    L_aug(z; lam, mu) = phi(z) + lam^T s(z) - (mu/2) * ||s(z)||^2  (max)

    Returns dict with keys:
      z_star          : (d_total,) joint strategy at VE
      lambda_star     : (n,) shared-constraint multiplier estimates from KKT
      residual        : float projected-residual at z_star
      flow_violation  : float ||s(z_star)||
    """
    if rng is None:
        rng = np.random.default_rng(0)

    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    d_total = N * d_i
    alpha_floor = scenario["alpha_floor"]

    def project(z):
        z_proj = z.copy()
        for i in range(N):
            start = i * d_i
            z_proj[start:start + n] = np.maximum(z_proj[start:start + n], 1e-6)
            z_proj[start + n:start + 2*n] = np.maximum(
                z_proj[start + n:start + 2*n], 1e-6)
            alpha_start = start + 2*n
            alpha_end = alpha_start + (N - 1)
            z_proj[alpha_start:alpha_end] = np.clip(
                z_proj[alpha_start:alpha_end], alpha_floor[i], 1.0)
            z_proj[alpha_end] = np.clip(z_proj[alpha_end], 0.0, 1.0)
        return z_proj

    def constraint_grad_on_z(lam, mu, z):
        """Gradient of -lam^T s(z) + (mu/2)||s(z)||^2 acting on each x_in / x_out."""
        s = flow_balance(z, scenario)
        # d s_k / d x_in_ij = delta_jk ; d s_k / d x_out_ij = -delta_jk
        # so the gradient of lam^T s w.r.t. x_in_ij = lam_j ; w.r.t. x_out_ij = -lam_j
        # Penalty: gradient of (mu/2)||s||^2 = mu * s_j * (d s_j / d ...).
        d_pen_in_per_resource = -lam - mu * s   # subtract from grad_x_in (we max)
        d_pen_out_per_resource = +lam + mu * s
        grad_adj = np.zeros(d_total)
        for i in range(N):
            start = i * d_i
            grad_adj[start:start + n] += d_pen_in_per_resource
            grad_adj[start + n:start + 2*n] += d_pen_out_per_resource
        return grad_adj

    # Multi-start outer loop
    best_z = None
    best_obj = np.inf  # combined residual + constraint violation
    best_lam = np.zeros(n)
    best_res = np.inf
    best_flow_viol = np.inf

    for start_idx in range(n_starts):
        z = np.zeros(d_total)
        for i in range(N):
            s = i * d_i
            opt_xin = scenario["alpha_ij_U"][i] / scenario["beta_ij_U"][i]
            z[s:s + n] = rng.uniform(0.5 * opt_xin, 1.5 * opt_xin, n)
            z[s + n:s + 2*n] = z[s:s + n].copy()  # x_out = x_in for flow-balance
            z[s + 2*n:s + 2*n + (N-1)] = rng.uniform(
                alpha_floor[i] + 0.01, 1.0, N - 1)
            z[s + 2*n + (N-1)] = 0.0
        z = project(z)

        # Augmented Lagrangian outer iterations
        lam = np.zeros(n)
        mu = 1.0
        for outer in range(8):
            lr_cur = lr
            for it in range(max_iter // 8):
                g_raw = compute_g(z, scenario)
                g_adj = g_raw + constraint_grad_on_z(lam, mu, z)
                res = projected_residual(g_adj, z, scenario)
                if res < tol * 0.5:
                    break
                z = project(z + lr_cur * g_adj)
                if it % 200 == 199:
                    lr_cur *= 0.8
            # Update lambda from current flow-balance
            s_cur = flow_balance(z, scenario)
            lam = lam + mu * s_cur
            mu *= 1.5
            if np.linalg.norm(s_cur) < tol * 10:
                break

        # Final assessment
        g_final = compute_g(z, scenario)
        res_final = projected_residual(g_final, z, scenario)
        s_final = flow_balance(z, scenario)
        flow_viol = float(np.linalg.norm(s_final))
        obj = res_final + 10.0 * flow_viol

        if obj < best_obj:
            best_obj = obj
            best_z = z.copy()
            best_lam = lam.copy()
            best_res = res_final
            best_flow_viol = flow_viol

    return {
        "z_star": best_z,
        "lambda_star": best_lam,
        "residual": best_res,
        "flow_violation": best_flow_viol,
    }


def solve_ve_multistart(scenario: Dict[str, Any], n_starts: int = 20,
                        rng: Optional[np.random.Generator] = None,
                        lr: float = 0.05, max_iter: int = 5000,
                        tol: float = 1e-6,
                        skip_warm_start: bool = False) -> Tuple[np.ndarray, float]:
    """Multi-start projected gradient ascent on g to find VE z*.

    The VE is characterised by g(z*,r) in N_R(z*).  For box-constrained R
    this means the *projected* gradient residual ||P_{T_R(z*)}(g)|| < tol.
    Commitment directions (g_c = -1 at c=0) are boundary-active and do NOT
    contribute to the projected residual.

    Args:
        skip_warm_start: If True, skip the deterministic analytical warm-start
            (x_in = alpha_U / beta_U, alpha = 1, c = 0).  Useful when calling
            this routine in a multi-VE search loop where the same warm-start
            on every outer iteration would trivially short-circuit dedup.

    Returns (z_best, projected_residual_best).
    """
    if rng is None:
        rng = np.random.default_rng(0)

    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    d_total = N * d_i
    alpha_floor = scenario["alpha_floor"]

    def project(z):
        z_proj = z.copy()
        for i in range(N):
            start = i * d_i
            z_proj[start:start + n] = np.maximum(z_proj[start:start + n], 1e-6)
            z_proj[start + n:start + 2*n] = np.maximum(
                z_proj[start + n:start + 2*n], 1e-6)
            alpha_start = start + 2*n
            alpha_end = alpha_start + (N - 1)
            z_proj[alpha_start:alpha_end] = np.clip(
                z_proj[alpha_start:alpha_end], alpha_floor[i], 1.0)
            z_proj[alpha_end] = np.clip(z_proj[alpha_end], 0.0, 1.0)
        return z_proj

    best_z = None
    best_res = np.inf

    if not skip_warm_start:
        # Always include the analytical warm-start: x_in=alpha_U/beta_U, alpha=1, c=0
        # This is the unconstrained optimum and often a good VE candidate.
        z_warm = np.zeros(d_total)
        for i in range(N):
            s = i * d_i
            opt_xin = scenario["alpha_ij_U"][i] / scenario["beta_ij_U"][i]
            z_warm[s:s + n] = opt_xin
            z_warm[s + n:s + 2*n] = opt_xin
            z_warm[s + 2*n:s + 2*n + (N-1)] = 1.0
            z_warm[s + 2*n + (N-1)] = 0.0
        z_warm = project(z_warm)
        g_warm = compute_g(z_warm, scenario)
        res_warm = projected_residual(g_warm, z_warm, scenario)
        if res_warm < best_res:
            best_res = res_warm
            best_z = z_warm.copy()
        if best_res < tol:
            return best_z, best_res

    for start_idx in range(n_starts):
        z = np.zeros(d_total)
        # When skip_warm_start=True, broaden the random init range so the
        # search can reach equilibria outside the basin of the analytical
        # warm-start.  Otherwise keep the existing narrow init that's tuned
        # for fast convergence on cooperative scenarios.
        # c_init draws are per-start (not per-call) so that multiple random
        # restarts in the same call each get a distinct commitment seed.
        # Benign at n_random_per_call=1 but defensive against larger n_starts.
        if skip_warm_start:
            x_lo, x_hi = 0.05, 4.0
            alpha_lo_extra, alpha_hi = 0.0, 1.0
            c_init = rng.uniform(0.0, 1.0)
        else:
            x_lo, x_hi = None, None  # use opt-xin-relative below
            alpha_lo_extra, alpha_hi = 0.01, 1.0
            c_init = 0.0
        for i in range(N):
            s = i * d_i
            opt_xin = scenario["alpha_ij_U"][i] / scenario["beta_ij_U"][i]
            if skip_warm_start:
                z[s:s + n] = rng.uniform(x_lo, x_hi, n)
                z[s + n:s + 2*n] = rng.uniform(x_lo, x_hi, n)
                z[s + 2*n:s + 2*n + (N-1)] = rng.uniform(
                    alpha_floor[i] + alpha_lo_extra, alpha_hi, N - 1)
                z[s + 2*n + (N-1)] = c_init
            else:
                z[s:s + n] = rng.uniform(0.5 * opt_xin, 1.5 * opt_xin, n)
                z[s + n:s + 2*n] = rng.uniform(0.1, 1.0, n)
                z[s + 2*n:s + 2*n + (N-1)] = rng.uniform(
                    alpha_floor[i] + alpha_lo_extra, alpha_hi, N - 1)
                z[s + 2*n + (N-1)] = 0.0  # commitment starts at lower bound
        z = project(z)

        lr_cur = lr
        prev_res = np.inf

        for it in range(max_iter):
            g = compute_g(z, scenario)
            res = projected_residual(g, z, scenario)
            if res < tol:
                break
            # Armijo-like step: reduce if oscillating
            if it > 0 and res > prev_res * 1.5 and lr_cur > 1e-6:
                lr_cur *= 0.5
            prev_res = res
            z = project(z + lr_cur * g)
            if it % 1000 == 999:
                lr_cur *= 0.7

        g_final = compute_g(z, scenario)
        res_final = projected_residual(g_final, z, scenario)
        if res_final < best_res:
            best_res = res_final
            best_z = z.copy()
        if best_res < tol:
            break

    if best_z is None:
        # No start (warm or random) yielded a candidate; return last seen z so
        # callers can detect failure via best_res = inf.
        best_z = project(np.zeros(d_total))
    return best_z, best_res


# ---------------------------------------------------------------------------
# Monderer-Shapley identity ratio
# ---------------------------------------------------------------------------

def ms_identity_ratio(phi_i_fn: Callable, P_fn: Callable,
                      z: np.ndarray, z_prime: np.ndarray, i: int,
                      scenario: Dict[str, Any]) -> float:
    """M-S ratio [phi_i(z_{-i}, z_i) - phi_i(z_{-i}, z_i')] / [P(z) - P(z')].

    phi_i_fn: callable (z, scenario, i) -> scalar payoff
    P_fn:     callable (z, scenario) -> scalar potential
    z_prime:  strategy profile where agent i has deviated (z_i' instead of z_i)

    Returns ratio (or np.nan if denominator near zero).
    """
    num = phi_i_fn(z, scenario, i) - phi_i_fn(z_prime, scenario, i)
    den = P_fn(z, scenario) - P_fn(z_prime, scenario)
    if abs(den) < 1e-14:
        return np.nan
    return num / den


def payoff_i(z: np.ndarray, scenario: Dict[str, Any], i: int) -> float:
    """Per-agent payoff phi_i(z) using TC-I quadratic utility.

    phi_i = U_i - C_i - c_i - sum_{j!=i} F_ij(1-alpha_ji)
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    Phi = scenario["Phi"]
    e_ij = scenario["e_ij"]
    alpha_coop = scenario["alpha_coop"]
    alpha_expl = scenario["alpha_expl"]

    z_i = z[i * d_i:(i + 1) * d_i]
    x_in = z_i[:n]
    alpha_ij = z_i[2*n:2*n + (N-1)]
    c_i = z_i[-1]

    beta_U = scenario["beta_ij_U"][i]
    alpha_U = scenario["alpha_ij_U"][i]

    # Utility U_i
    U_i = _utility_i(x_in, alpha_U, beta_U)

    # Contest energy C_i = sum_{j!=i} Phi * e_ij * (1-alpha_ij) * (1-alpha_ji)
    partners = [j for j in range(N) if j != i]
    C_i = 0.0
    for idx, j in enumerate(partners):
        E_ij = e_ij[i, j]
        a_ij = alpha_ij[idx]
        # alpha_ji: agent j's compliance toward i
        z_j = z[j * d_i:(j + 1) * d_i]
        alpha_ji_vec = z_j[2*n:2*n + (N-1)]
        # find index of i in j's partner list
        j_partners = [k for k in range(N) if k != j]
        i_idx_in_j = j_partners.index(i)
        a_ji = alpha_ji_vec[i_idx_in_j]
        C_i += Phi * E_ij * (1.0 - a_ij) * (1.0 - a_ji)

    # F_ij term: friction i suffers from j's non-compliance toward i
    # F_ij(1-alpha_ji) = e_ij * (1-alpha_ji)^2 / 2 (quadratic model)
    F_i = 0.0
    for idx, j in enumerate(partners):
        z_j = z[j * d_i:(j + 1) * d_i]
        alpha_ji_vec = z_j[2*n:2*n + (N-1)]
        j_partners = [k for k in range(N) if k != j]
        i_idx_in_j = j_partners.index(i)
        a_ji = alpha_ji_vec[i_idx_in_j]
        F_i += e_ij[j, i] * (1.0 - a_ji)**2 / 2.0

    return U_i - C_i - c_i - F_i


def potential_P0(z: np.ndarray, scenario: Dict[str, Any]) -> float:
    """Candidate exact potential P_0(z) = sum_i U_i - C_total - sum c_i - sum F_ij.

    Under M-S Def 2.2 exact-potential: phi_i(z) - phi_i(z') = P_0(z) - P_0(z')
    for all unilateral deviations.
    """
    return sum(payoff_i(z, scenario, i) for i in range(scenario["N"]))


def potential_Pw(z: np.ndarray, scenario: Dict[str, Any],
                 w: Optional[np.ndarray] = None) -> float:
    """Negishi-weighted candidate potential P_w(z) = sum_i w_i * phi_i."""
    N = scenario["N"]
    if w is None:
        # Default: uniform Negishi weights (heterogeneous not specified)
        w = np.ones(N) / N
    return sum(w[i] * payoff_i(z, scenario, i) for i in range(N))


# ---------------------------------------------------------------------------
# Friction-state recursion (Q5, §6.2 reading)
# ---------------------------------------------------------------------------

def friction_state_recursion(phi_prev: float, v_t: float,
                              epsilon: float, eta: float) -> float:
    """phi_{t+1} = (1-eps)*phi_t + eta*v_t per TC-IV rmk-friction-law-of-motion."""
    return (1.0 - epsilon) * phi_prev + eta * v_t


def violation_rate(z: np.ndarray, scenario: Dict[str, Any]) -> float:
    """Smooth violation rate v(z) = sum_{i,j,i!=j} D_ij(1-alpha_ji).

    Uses D_ij(1-a) = beta_ij*(1-a)^2/2 per TC-IX def-boundary-evolution.
    beta_ij from e_ij matrix as proxy.
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    e_ij = scenario["e_ij"]

    v = 0.0
    for i in range(N):
        partners = [j for j in range(N) if j != i]
        z_i = z[i * d_i:(i + 1) * d_i]
        alpha_ij = z_i[2*n:2*n + (N-1)]
        for idx, j in enumerate(partners):
            a_ij = alpha_ij[idx]
            beta_ij = e_ij[i, j]
            v += beta_ij * (1.0 - a_ij)**2 / 2.0
    return v


def compute_L_phi(eta: float, L_v: float, epsilon: float) -> float:
    """Steady-state phi Lipschitz sensitivity: L_phi = eta * L_v / epsilon."""
    return eta * L_v / epsilon


def sigma_D24_formula(L_BR_z_max: float, L_BR_phi_max: float,
                      M: float, E_bar: float, L_omega_max: float,
                      mu_min: float, eta: float, L_v: float,
                      epsilon: float) -> float:
    """sigma_D24 >= 1 / (L_BR_z_max + (M*E_bar*L_omega_max/mu_min)*(eta*L_v/epsilon)).

    Per derivation 05 eq (4.2).
    """
    L_phi = compute_L_phi(eta, L_v, epsilon)
    denom = L_BR_z_max + (M * E_bar * L_omega_max / mu_min) * L_phi
    if denom < 1e-15:
        return np.inf
    return 1.0 / denom


# ---------------------------------------------------------------------------
# P-B equilibrium scaling
# ---------------------------------------------------------------------------

def pb_scaling(lambda_star: np.ndarray, A_i: np.ndarray) -> np.ndarray:
    """P-B effective multiplier lambda_tilde*_{i,j} = (A_i)_{jj} * lambda*_j.

    lambda_star : (n,) shared constraint multiplier vector
    A_i         : (n, n) diagonal positive matrix
    Returns     : (n,) effective per-agent multiplier
    """
    return np.diag(A_i) * lambda_star


# ---------------------------------------------------------------------------
# SGA correction
# ---------------------------------------------------------------------------

def sga_correction(g: np.ndarray, J_a: np.ndarray, lam: float) -> np.ndarray:
    """SGA-corrected gradient: g_SGA = g - lam * J_a^T @ g.

    g   : joint pseudogradient vector (d,)
    J_a : antisymmetric Jacobian A (d, d)
    lam : SGA step-size parameter lambda (sign matters per Balduzzi Thm 5)
    """
    return g - lam * J_a.T @ g


# ---------------------------------------------------------------------------
# Alpha-rank stationary distribution
# ---------------------------------------------------------------------------

def alpha_rank_transition(payoff_tensor: np.ndarray, alpha: float = 1e-3,
                          N: int = 3) -> np.ndarray:
    """Build alpha-Rank Markov transition matrix for N agents on a coarse grid.

    payoff_tensor: (S, S, ..., S, N) array (S strategies per agent, N payoffs)
                   shape (S,)*N + (N,)
    alpha         : mutation rate parameter
    Returns       : (S^N, S^N) row-stochastic transition matrix
    """
    S = payoff_tensor.shape[0]
    n_states = S ** N

    # Enumerate all joint strategy profiles
    from itertools import product
    states = list(product(range(S), repeat=N))
    state_idx = {s: i for i, s in enumerate(states)}

    T = np.zeros((n_states, n_states))

    for si, s in enumerate(states):
        for player in range(N):
            for new_action in range(S):
                if new_action == s[player]:
                    continue
                # Create new state where player deviates
                s_prime = list(s)
                s_prime[player] = new_action
                s_prime = tuple(s_prime)
                sj = state_idx[s_prime]

                # Fitness of current vs new action for this player
                u_current = payoff_tensor[s][player]
                u_new = payoff_tensor[s_prime][player]

                # Alpha-rank fitness: rho = alpha * (u_new - u_current)
                delta_u = u_new - u_current
                # Transition probability using alpha-rank formula
                if abs(delta_u) < 1e-15:
                    rho = alpha / (alpha + alpha)  # 0.5
                else:
                    rho = (alpha * delta_u) / (np.exp(alpha * delta_u) - 1.0 + 1e-300)
                    rho = max(0.0, min(1.0, rho / (S * N)))

                T[si, sj] += rho

    # Self-transitions
    for si in range(n_states):
        T[si, si] = max(0.0, 1.0 - np.sum(T[si]))

    return T


def alpha_rank_stationary(payoff_tensor: np.ndarray, alpha: float = 1e-3) -> np.ndarray:
    """Compute alpha-Rank stationary distribution via power iteration.

    Returns (n_states,) stationary distribution.
    """
    T = alpha_rank_transition(payoff_tensor, alpha)
    n = T.shape[0]
    pi = np.ones(n) / n
    for _ in range(1000):
        pi_new = pi @ T
        if np.linalg.norm(pi_new - pi) < 1e-12:
            break
        pi = pi_new
    return pi / pi.sum()


# ---------------------------------------------------------------------------
# Winston-Kolter monDEQ forward-backward iteration
# ---------------------------------------------------------------------------

def mondeq_forward_backward(g_fn: Callable, z0: np.ndarray, scenario: Dict[str, Any],
                             alpha_step: float = 0.01, max_iter: int = 500,
                             tol: float = 1e-8) -> Tuple[np.ndarray, list]:
    """Forward-backward splitting iteration for monotone operator -g.

    Equivalent to projected gradient step: z_{k+1} = proj_R(z_k + alpha * g(z_k))
    Converges linearly when -g is strongly monotone (Q2 DSC closed).

    Returns (z_converged, residual_history).
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    d_total = N * d_i
    alpha_floor = scenario["alpha_floor"]

    def project(z):
        z_proj = z.copy()
        for i in range(N):
            start = i * d_i
            z_proj[start:start + n] = np.maximum(z_proj[start:start + n], 1e-6)
            z_proj[start + n:start + 2*n] = np.maximum(z_proj[start + n:start + 2*n], 1e-6)
            alpha_start = start + 2*n
            alpha_end = alpha_start + (N - 1)
            z_proj[alpha_start:alpha_end] = np.clip(
                z_proj[alpha_start:alpha_end], alpha_floor[i], 1.0)
            z_proj[alpha_end] = np.clip(z_proj[alpha_end], 0.0, 1.0)
        return z_proj

    z = project(z0.copy())
    residuals = []
    for _ in range(max_iter):
        g = g_fn(z, scenario)
        # Use projected residual: x_in gradients at unconstrained optima are
        # in N_R(z), so project them out for the convergence check.
        res = projected_residual(g, z, scenario)
        residuals.append(res)
        if res < tol:
            break
        z = project(z + alpha_step * g)

    return z, residuals


# ---------------------------------------------------------------------------
# Sylvester criterion helper
# ---------------------------------------------------------------------------

def sylvester_slack(scenario: Dict[str, Any]) -> np.ndarray:
    """Compute per-pair Sylvester slack: sqrt(Delta_ij * Delta_ji) - Phi * E_ij.

    From derivation 02 §3.2 / §4.1:
        Delta_ij = |d^2 varphi_i / d alpha_ij^2| (diagonal curvature magnitude)

    In the compliance gradient model:
        d^2 varphi_i / d alpha_ij^2 = -(alpha_coop[i,j] - alpha_expl[i,j])

    This is negative (DSC-favorable) when alpha_coop > alpha_expl.
    Delta_ij = max(0, alpha_coop[i,j] - alpha_expl[i,j]).

    The off-diagonal coupling magnitude:
        E_ij = |d^2 e_ij / d alpha_ij d alpha_ji| = e_ij[i,j] (contest energy mixed partial)

    Returns (N, N) matrix with off-diagonal entries = slack.
    Positive => DSC outcome (a); negative => outcome (c).
    """
    N = scenario["N"]
    Phi = scenario["Phi"]
    e_ij = scenario["e_ij"]
    alpha_coop = scenario["alpha_coop"]
    alpha_expl = scenario["alpha_expl"]

    # Delta_ij = alpha_coop[i,j] + alpha_expl[i,j]
    # Per updated model: d^2 phi_i/d alpha_ij^2 = -(c_ij + e_ij) < 0 always.
    # Delta_ij = c_ij + e_ij (always positive, always negative diagonal curvature).
    Delta = alpha_coop + alpha_expl

    slack = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            D_ij = Delta[i, j]
            D_ji = Delta[j, i]
            E_ij = e_ij[i, j]
            slack[i, j] = np.sqrt(D_ij * D_ji) - Phi * E_ij
    return slack


# ---------------------------------------------------------------------------
# Perturbation-based L_BR estimation (Q5)
# ---------------------------------------------------------------------------

def estimate_L_BR_z(scenario: Dict[str, Any], n_samples: int = 50,
                    delta: float = 0.01) -> float:
    """Estimate L_BR_z_max via perturbation analysis.

    Compute max_i || dBR_i/dz_{-i} || empirically at the approximate VE.
    """
    rng = np.random.default_rng(42)
    z_star, _ = solve_ve_multistart(scenario, n_starts=5, rng=rng, max_iter=1000)

    N = scenario["N"]
    d_i = _per_agent_dim(scenario)
    d_total = N * d_i

    L_max = 0.0
    for i in range(N):
        ratios = []
        for _ in range(n_samples):
            dz = rng.standard_normal(d_total) * delta
            # Zero out agent i's own perturbation
            dz[i * d_i:(i + 1) * d_i] = 0.0
            z_pert = z_star + dz
            g0 = compute_g(z_star, scenario)
            g1 = compute_g(z_pert, scenario)
            # BR shift approximation: agent i component change
            dg_i_norm = np.linalg.norm(g1[i*d_i:(i+1)*d_i] - g0[i*d_i:(i+1)*d_i])
            dz_norm = np.linalg.norm(dz)
            if dz_norm > 1e-14:
                ratios.append(dg_i_norm / dz_norm)
        if ratios:
            L_max = max(L_max, np.mean(ratios))
    return L_max


# ---------------------------------------------------------------------------
# Output utilities
# ---------------------------------------------------------------------------

def safe_mkdir(path: str) -> bool:
    """Create directory; return True if succeeded, False otherwise."""
    import os
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def _resolve_drive_output_base() -> str:
    """Pick the Drive output base appropriate for the current platform.

    Windows: G:\\Shared drives\\... (drive letter).
    WSL/Linux: /mnt/g/Shared drives/... (DrvFs mount).
    Returns the Linux mount if it exists, otherwise the Windows-style path.
    On Linux without the mount, the Windows path is returned anyway so
    callers' `safe_mkdir(path)` returns False rather than the function
    silently swallowing the error — but emit a stderr warning so the
    misconfiguration is visible.
    """
    import os, sys
    linux_path = "/mnt/g/Shared drives/Codynamics/TMAN/flux/composed-pseudogradient-verification"
    windows_path = r"G:\Shared drives\Codynamics\TMAN\flux\composed-pseudogradient-verification"
    if sys.platform.startswith("linux"):
        if os.path.isdir(linux_path):
            return linux_path
        # On Linux but mount not present — likely the Drive mount isn't
        # set up.  Return a clearly-Linux-style placeholder so the path is
        # still recognizable as bad.
        print(f"WARN: _resolve_drive_output_base on Linux but mount "
              f"{linux_path} is not present; using placeholder.  "
              f"safe_mkdir will fail and CSV writes will be skipped.",
              file=sys.stderr)
        return linux_path  # caller's safe_mkdir handles failure
    return windows_path


DRIVE_OUTPUT_BASE = _resolve_drive_output_base()


# ---------------------------------------------------------------------------
# Q8-Q11 primitives (Minty probe, Potentialness P_B, divergence diagnostic,
# cycle-vs-saturation classifier).  See `tman-docs/handoffs/
# 2026-05-13-cowork-to-code-minty-probe-and-diagnostics.md` for the surface
# motivation; derivation 07 §4.1 and credit-as-resource-flow/S3 §4.1 for the
# theoretical formulas.
# ---------------------------------------------------------------------------


def compute_jacobian_GL(z: np.ndarray, scenario: Dict[str, Any],
                        eps: float = 1e-5,
                        pi_star: Optional[np.ndarray] = None,
                        phi_mode: Optional[str] = None) -> np.ndarray:
    """Numerical Jacobian J = dG_L/dz at z via central finite differences."""
    d = len(z)
    J = np.zeros((d, d))
    for k in range(d):
        zp = z.copy(); zp[k] += eps
        zm = z.copy(); zm[k] -= eps
        J[:, k] = (compute_G_L(zp, scenario, pi_star=pi_star, phi_mode=phi_mode) -
                   compute_G_L(zm, scenario, pi_star=pi_star, phi_mode=phi_mode)) / (2 * eps)
    return J


def compute_flow_coupling(z: np.ndarray, scenario: Dict[str, Any],
                          pi_star: Optional[np.ndarray] = None) -> np.ndarray:
    """The z-dependent FlowCoupling component of G_L — NOT the canonical
    Balduzzi g_A.

    Decomposition:
        g_L(z) = compute_g(z) + R + FlowCoupling(z),    R constant.

    The CANONICAL Balduzzi g_A is the vector field whose Jacobian equals
    A = (J - J^T)/2, which has zero diagonal contribution from second
    derivatives.  This implementation's FlowCoupling has both the cross-
    agent off-diagonal piece (matching S3 §4.1.2 antisymmetric placement)
    AND the per-agent diagonal Hessian piece d^2 L_RF / dw_i^2 (which is
    symmetric and belongs to g_S in the canonical splitting).

    Two flow_form regimes:

    - "biquadratic" (case (b), generic for TC): x_ij = 0.5 w_i^2 w_j^2.
      d L_RF / d w_i = -pi*_ij * w_i * w_j^2 (z-dependent).
      Diagonal d^2 L_RF / dw_i^2 = -pi*_ij * w_j^2 != 0, so this
      FlowCoupling deviates from canonical g_A by the symmetric diagonal
      piece.  div(FlowCoupling) != 0 generically.

    - "bilinear" (case (a), Asm 3.2): x_ij = w_i * w_j.
      d L_RF / d w_i = -pi*_ij * w_j (linear in w_j only).
      Diagonal d^2 L_RF / dw_i^2 = 0, so FlowCoupling matches canonical
      g_A exactly: T_A = 0, J(FlowCoupling) is constant antisymmetric,
      and div(FlowCoupling) = 0 exactly.

    Usage notes:
    - Q8/Q11 use this to evaluate ||T_A||_op via second-order FD; under
      bilinear it gives the correct zero; under biquadratic it gives a
      meaningful (non-zero) bound on the operator norm of the second
      derivative.
    - Q10's div(FlowCoupling) and skew checks are STRICT validation of
      S3 Claim 4.1 only under bilinear case (a); under biquadratic case
      (b) they are informational (they pick up the diagonal Hessian piece
      which is part of g_S, not g_A, in the canonical splitting).
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    if pi_star is None:
        pi_star = scenario["pi_star"]
    flow_form = scenario.get("flow_form", "biquadratic")

    result = np.zeros(N * d_i)
    for i in range(N):
        z_i = z[i * d_i:(i + 1) * d_i]
        w_i = z_i[:n]
        flow_coupling = np.zeros(n)
        for j in range(N):
            if j == i:
                continue
            z_j = z[j * d_i:(j + 1) * d_i]
            w_j = z_j[:n]
            edge_price = pi_star[i] - pi_star[j]
            if flow_form == "bilinear":
                flow_coupling -= edge_price * w_j
            else:
                flow_coupling -= edge_price * w_i * (w_j ** 2)
        s = i * d_i
        result[s:s+n] = flow_coupling
    return result


def minty_residual(z_prime: np.ndarray, z_star: np.ndarray,
                   scenario: Dict[str, Any]) -> float:
    """Minty inner product in Anagnostides convention (F := -g):
        <F(z'), z' - z*> = -<g(z'), z' - z*>
    where g is the gradient-of-utility composed pseudogradient (compute_g).

    Per derivation 07 §2.4 the sign-convention bridge: g_L (Lagrangian
    gradient) is used theoretically with the dualized multipliers making
    g_L(z*) = 0 at the interior cooperative VE.  In the implemented module,
    `compute_g` is the agent-level gradient-of-utility that solve_ve_*
    drives to zero; the additional Lagrangian terms in compute_G_L do not
    dualize the multipliers and so g_L(z*) is offset by a constant.  We
    therefore test Minty on the same vector field the dynamics integrate:
    compute_g.  The antisymmetric coupling required for the case (b) T_A
    bound is still extracted from compute_G_L (via compute_flow_coupling)
    when forming the per-equilibrium radius.

    Sign: Minty holds at z* on a neighborhood when this residual is
    >= -epsilon (numerical tolerance) for all z' in the ball.  Positive
    values away from z* indicate the residual is moving into the Minty-
    affirmative region; negative values indicate failure.
    """
    g = compute_g(z_prime, scenario)
    return float(-np.dot(g, z_prime - z_star))


def per_equilibrium_minty_radius_theoretical(
    z_star: np.ndarray, scenario: Dict[str, Any],
    eps_fd: float = 1e-4,
    n_dirs_T_A: int = 32,
    h_T_A: float = 0.05,
    rng: Optional[np.random.Generator] = None) -> Dict[str, float]:
    """Theoretical per-equilibrium Minty ball radius from derivation 07 §4.1:

      rho^(k) = min( mu_S^- / (2*C_3),  mu_S^- / ||T_A||_op )

    where mu_S^- = lambda_min(-J_S(z*)) is the symmetric-Jacobian curvature
    floor, C_3 is the third-derivative bound on g_S, and ||T_A||_op is the
    operator norm of the antisymmetric second-derivative tensor.

    Approximations used here:
      - J_S(z*) via balduzzi-decomposition of FD Jacobian of compute_G_L.
      - mu_S^- = max(0, lambda_min(-J_S)).
      - ||T_A||_op estimated as max over random unit directions v of
            || compute_flow_coupling(z* + h v)
             + compute_flow_coupling(z* - h v)
             - 2 * compute_flow_coupling(z*) || / h^2
        (second-order central difference; absorbs Taylor 1/2 factor per
        derivation 07 §3.3 Taylor-coefficient convention).
      - C_3 estimated analogously on compute_g (the canonical symmetric
        component), using the third-order one-sided residual after
        subtracting the first-order Jacobian Taylor term.  This is a
        loose upper bound — for the cleanest comparison we report both
        radii and the binding one.

    Returns dict with keys: mu_S_minus, T_A_op, C_3, rho_S, rho_A, rho.
    """
    if rng is None:
        rng = np.random.default_rng(0)

    J = compute_jacobian_GL(z_star, scenario, eps=eps_fd)
    S_J = (J + J.T) / 2.0
    eigs = np.linalg.eigvalsh(-S_J)
    mu_S_minus = float(max(eigs.min(), 0.0))
    # Tangent-space mu_S^-: smallest positive eigenvalue ignoring near-zero
    # ones.  At projected VEs (boundary-active components), -J_S has near-zero
    # eigenvalues in the directions where the constraint is binding; the
    # relative-interior curvature is the smallest STRICTLY positive eigenvalue.
    # Per derivation 07 §7.2 ASSUMPTION 2.2 (interior VE) being open, we
    # report both: mu_S_minus_full (matches the formula literally) and
    # mu_S_minus_tangent (the formula evaluated on the unconstrained subspace).
    eig_tol = max(eps_fd * float(np.max(np.abs(eigs))), 1e-8)
    positive_eigs = eigs[eigs > eig_tol]
    mu_S_minus_tangent = float(positive_eigs.min()) if len(positive_eigs) > 0 else 0.0

    g_A_star = compute_flow_coupling(z_star, scenario)
    g_star = compute_g(z_star, scenario)
    d = len(z_star)
    h = h_T_A

    # ||T_A||_op via second-order central difference on flow coupling
    T_A_op = 0.0
    # Compute J_A linear part for symmetric-difference-based estimator
    JA_at = np.zeros((d, d))
    for k in range(d):
        zp = z_star.copy(); zp[k] += eps_fd
        zm = z_star.copy(); zm[k] -= eps_fd
        JA_at[:, k] = (compute_flow_coupling(zp, scenario) -
                       compute_flow_coupling(zm, scenario)) / (2 * eps_fd)

    # C_3 via third-derivative norm on compute_g
    Jg_at = np.zeros((d, d))
    for k in range(d):
        zp = z_star.copy(); zp[k] += eps_fd
        zm = z_star.copy(); zm[k] -= eps_fd
        Jg_at[:, k] = (compute_g(zp, scenario) -
                       compute_g(zm, scenario)) / (2 * eps_fd)

    C_3 = 0.0
    for _ in range(n_dirs_T_A):
        v = rng.standard_normal(d)
        nv = np.linalg.norm(v)
        if nv < 1e-12:
            continue
        v_unit = v / nv
        # T_A via 2nd-order central difference on flow_coupling (Hessian-like)
        zp = z_star + h * v_unit
        zm = z_star - h * v_unit
        second = (compute_flow_coupling(zp, scenario) +
                  compute_flow_coupling(zm, scenario) -
                  2 * g_A_star) / (h ** 2)
        T_A_op = max(T_A_op, float(np.linalg.norm(second)))
        # C_3 third-derivative on compute_g via 3rd-order one-sided residual.
        # g_S(z*+hv) ~ g_S(z*) + h Jg v + (h^2/2) Hess vv + (h^3/6) Third vvv
        # Hessian piece we already get via 2nd-order central diff:
        hess_vv = (compute_g(zp, scenario) + compute_g(zm, scenario) -
                   2 * g_star) / (h ** 2)
        # Now eval at 2h to isolate cubic
        zp2 = z_star + 2 * h * v_unit
        zm2 = z_star - 2 * h * v_unit
        cubic_vvv = (compute_g(zp2, scenario) - compute_g(zm2, scenario) -
                     4 * h * (Jg_at @ v_unit) -
                     4 * h * (compute_g(zp, scenario) - compute_g(zm, scenario) -
                              2 * h * (Jg_at @ v_unit))) / (2 * h ** 3)
        # Take norm; C_3 absorbs factorial per derivation 07 §3.3 convention
        C_3 = max(C_3, float(np.linalg.norm(cubic_vvv)))

    rho_S = mu_S_minus / (2 * C_3) if C_3 > 1e-12 else np.inf
    rho_A = mu_S_minus / T_A_op if T_A_op > 1e-12 else np.inf
    rho = min(rho_S, rho_A)
    # Tangent-space variant: formula evaluated with the strictly-positive
    # curvature floor.  Operational under projected-VE conditions where the
    # full-space mu_S^- is exactly zero on boundary-active directions.
    rho_S_tangent = mu_S_minus_tangent / (2 * C_3) if C_3 > 1e-12 else np.inf
    rho_A_tangent = mu_S_minus_tangent / T_A_op if T_A_op > 1e-12 else np.inf
    rho_tangent = min(rho_S_tangent, rho_A_tangent)
    return {
        "mu_S_minus": mu_S_minus,
        "mu_S_minus_tangent": mu_S_minus_tangent,
        "T_A_op": float(T_A_op),
        "C_3": float(C_3),
        "rho_S": float(rho_S),
        "rho_A": float(rho_A),
        "rho": float(rho),
        "rho_S_tangent": float(rho_S_tangent),
        "rho_A_tangent": float(rho_A_tangent),
        "rho_tangent": float(rho_tangent),
    }


def project_to_feasible_box(z: np.ndarray, scenario: Dict[str, Any],
                             x_max: float = 10.0) -> np.ndarray:
    """Project z onto the box-defined feasible set (per-agent boxes from Q1 §1):
      x_in, x_out >= 1e-6 (positivity); alpha in [alpha_floor, 1]; c in [0, 1].

    This is the same simple projection verify_07's project_cyc uses.  Used
    by empirical_minty_radius to keep sampled z' inside R.
    """
    zp = z.copy()
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    alpha_floor = scenario["alpha_floor"]
    for i in range(N):
        s = i * d_i
        zp[s:s+n] = np.clip(zp[s:s+n], 1e-6, x_max)
        zp[s+n:s+2*n] = np.clip(zp[s+n:s+2*n], 1e-6, x_max)
        zp[s+2*n:s+2*n+(N-1)] = np.clip(
            zp[s+2*n:s+2*n+(N-1)], alpha_floor[i], 1.0)
        zp[s+2*n+(N-1)] = np.clip(zp[s+2*n+(N-1)], 0.0, 1.0)
    return zp


def empirical_minty_radius(z_star: np.ndarray, scenario: Dict[str, Any],
                           n_dirs: int = 40, n_levels: int = 30,
                           r_max: float = 1.0, tol: float = -1e-3,
                           frac_pass_threshold: float = 0.8,
                           project: bool = True,
                           rng: Optional[np.random.Generator] = None,
                           effective_displacement_floor: float = 1e-6) -> Dict[str, Any]:
    """Largest intended r such that AT LEAST `frac_pass_threshold` of
    sampled directions satisfy Minty (residual >= tol) at radius r, AND
    largest *effective* displacement at which Minty empirically holds.

    The distinction matters at boundary-active VEs (which is what the
    projection-based VE solver typically finds — see derivation 07 §7.2
    ASSUMPTION 2.2).  For such VEs many sampled `z' = z* + r*v` at large
    intended `r` are clipped back to the box boundary by
    `project_to_feasible_box`, so the *effective* displacement
    ||z'_projected - z*|| is much smaller than `r`.  Reporting only
    the intended `r` overstates the radius at which Minty has been
    tested — `minty_residual(z'_projected, z*)` is evaluated at a
    barely-displaced point and is trivially >= 0.

    Reports BOTH:
      - intended-radius statistics (the historical "empirical_radius",
        contiguous-pass on intended r)
      - effective-displacement statistics (per-level mean / median /
        max ||z'_projected - z*||, and the largest effective displacement
        at which the threshold is met)

    Note on tolerance/threshold:  Derivation 07's per-equilibrium ball is
    a strict-interior local property; in practice the implemented VE
    solver finds *projected* equilibria with boundary-active components,
    so directions tangent to active boundaries will fail Minty trivially.
    `frac_pass_threshold` ≥ 0.8 isolates the directions where Minty is
    structurally informative from the boundary-tangent failures.

    project=True projects sampled z' back onto the feasible box (Q1 §1
    constraints) — matches the dynamics integrators.

    `effective_displacement_floor`: filter out directions whose effective
    displacement is below this floor when computing pass fractions (those
    are projection-clipped to z* itself and don't actually probe Minty).
    """
    if rng is None:
        rng = np.random.default_rng(0)
    d = len(z_star)
    dirs = []
    for _ in range(n_dirs):
        v = rng.standard_normal(d)
        nv = np.linalg.norm(v)
        if nv > 1e-12:
            dirs.append(v / nv)
    levels = np.linspace(r_max / n_levels, r_max, n_levels)
    contiguous_radius = 0.0
    contiguous_broken = False
    last_passing_radius = 0.0
    eff_contiguous_radius = 0.0
    eff_contiguous_broken = False
    eff_last_passing_radius = 0.0
    per_level_stats = []
    # Track max effective displacement on which a Minty-pass was observed
    max_eff_displacement_passing = 0.0
    for r in levels:
        residuals = []
        eff_displacements = []
        eff_residuals_filtered = []
        for v in dirs:
            zp = z_star + r * v
            if project:
                zp = project_to_feasible_box(zp, scenario)
            eff = float(np.linalg.norm(zp - z_star))
            res = minty_residual(zp, z_star, scenario)
            residuals.append(res)
            eff_displacements.append(eff)
            if eff >= effective_displacement_floor:
                eff_residuals_filtered.append((eff, res))
        residuals = np.array(residuals)
        eff_displacements = np.array(eff_displacements)
        n_pass = int(np.sum(residuals >= tol))
        frac_pass = n_pass / len(residuals)
        # Filtered pass-frac: only directions whose effective displacement
        # is meaningfully > 0 (i.e. not clipped back to z*).
        if eff_residuals_filtered:
            eff_pass = sum(1 for (_, rr) in eff_residuals_filtered
                            if rr >= tol)
            frac_pass_eff = eff_pass / len(eff_residuals_filtered)
            mean_eff = float(np.mean([e for (e, _) in eff_residuals_filtered]))
            median_eff = float(np.median([e for (e, _) in eff_residuals_filtered]))
            max_eff = float(np.max([e for (e, _) in eff_residuals_filtered]))
            min_eff = float(np.min([e for (e, _) in eff_residuals_filtered]))
            # Effective displacements of the directions that PASSED Minty
            # at this level.  Used to derive the ball-radius statistic
            # below (option (b): quantile aligned with frac_pass_threshold).
            passing_effs = np.array([e for (e, rr) in eff_residuals_filtered
                                       if rr >= tol], dtype=float)
        else:
            frac_pass_eff = 0.0
            mean_eff = float(np.mean(eff_displacements))
            median_eff = float(np.median(eff_displacements))
            max_eff = float(np.max(eff_displacements)) if len(eff_displacements) else 0.0
            min_eff = float(np.min(eff_displacements)) if len(eff_displacements) else 0.0
            passing_effs = np.empty(0, dtype=float)
        # Ball-radius statistic per derivation 07 §4.1: rho^(k) is an
        # upper bound on ||z' - z*|| within which Minty holds at every
        # direction.  Median of all effective displacements is NOT a
        # ball-radius (with heterogeneous projection-clipping it returns
        # ~r/2, conflating "typical sample displacement" with "ball where
        # Minty holds").  Use the (1 - frac_pass_threshold)-quantile of
        # the PASSING directions' effective displacements:
        #   - frac_pass_threshold=0.8 -> 20th-percentile of passing
        #     directions' effective displacements at this level.
        #   - Interpretation: at least 80% of the directions that
        #     empirically passed Minty did so at an effective
        #     displacement >= this quantile.  This is the smallest
        #     "passing-direction effective displacement" up to a tail
        #     of (1 - frac_pass_threshold), aligning the ball-radius
        #     reading with the existing pass-fraction threshold.
        # The full-min (`passing_effs.min()`) is the strictest
        # ball-radius interpretation; we report it as a conservative
        # secondary statistic (`min_eff_disp_passing`).
        if passing_effs.size > 0:
            q = float(np.quantile(passing_effs,
                                   1.0 - frac_pass_threshold))
            ball_radius_eff = q
            min_eff_passing = float(passing_effs.min())
            max_eff_passing = float(passing_effs.max())
        else:
            ball_radius_eff = 0.0
            min_eff_passing = 0.0
            max_eff_passing = 0.0
        per_level_stats.append({
            "r": float(r), "frac_pass": frac_pass,
            "frac_pass_eff_only": frac_pass_eff,
            "min_res": float(residuals.min()),
            "median_res": float(np.median(residuals)),
            "max_res": float(residuals.max()),
            "mean_eff_disp": mean_eff,
            "median_eff_disp": median_eff,
            "max_eff_disp": max_eff,
            "min_eff_disp": min_eff,
            "n_eff_nontrivial": len(eff_residuals_filtered),
            # Ball-radius-aligned statistics (option (b), per Issue 2 fix):
            "ball_radius_eff_quantile": ball_radius_eff,
            "min_eff_disp_passing": min_eff_passing,
            "max_eff_disp_passing": max_eff_passing,
        })
        # Intended-r contiguous radius (historical interpretation)
        if frac_pass >= frac_pass_threshold:
            last_passing_radius = r
            if not contiguous_broken:
                contiguous_radius = r
        else:
            contiguous_broken = True
        # Effective-displacement contiguous radius (honest interpretation):
        # require the directions with non-trivial effective displacement to
        # meet the threshold.  This is the radius the formula in derivation
        # 07 §4 should be compared against.
        #
        # Use the ball-radius-aligned quantile (option (b)) as the
        # effective-displacement reading at this level.  Previously this
        # path used `median_eff`, which conflated "typical sample
        # displacement" with "ball radius"; see comment above.
        if (len(eff_residuals_filtered) > 0 and
                frac_pass_eff >= frac_pass_threshold):
            level_radius = ball_radius_eff
            eff_last_passing_radius = level_radius
            max_eff_displacement_passing = max(max_eff_displacement_passing,
                                                level_radius)
            if not eff_contiguous_broken:
                eff_contiguous_radius = max(eff_contiguous_radius, level_radius)
        else:
            eff_contiguous_broken = True
        # Continue scanning past first failure to give a full profile
    return {
        # Largest INTENDED r such that EVERY level <= r met the threshold
        # (historical interpretation; can be inflated by projection clipping).
        "empirical_radius": float(contiguous_radius),
        # Largest INTENDED r at which the threshold was met (may be non-contiguous).
        "last_passing_radius": float(last_passing_radius),
        # Effective-displacement variant: the (1 - frac_pass_threshold)-
        # quantile of PASSING directions' effective displacements at the
        # largest level whose nontrivially-displaced directions met the
        # threshold contiguously.  This is a ball-radius-aligned statistic
        # per derivation 07 §4.1's `rho^(k)` semantics; comparable to
        # the theoretical `rho_tangent` reported alongside.
        "empirical_radius_effective": float(eff_contiguous_radius),
        # Largest such quantile at which the threshold was met at any
        # scanned level (non-contiguous).
        "last_passing_radius_effective": float(eff_last_passing_radius),
        "max_eff_displacement_passing": float(max_eff_displacement_passing),
        "per_level_stats": per_level_stats,
        "n_dirs": len(dirs),
        "frac_pass_threshold": frac_pass_threshold,
        "tol": tol,
    }


def sylvester_region_slack(z: np.ndarray, scenario: Dict[str, Any]) -> float:
    """Sylvester-region slack: min over (i,j), i!=j, of
        sqrt(Delta_ij * Delta_ji) - Phi * E_ij
    evaluated at z's compliance entries.  Positive => z in R'.

    Per derivation 07 §5.1 / Q2 §5.2.  Uses scenario constants alpha_coop,
    alpha_expl as the Delta coefficients (TC-I quadratic curvatures), Phi
    as scalar friction multiplier, e_ij as contest-energy coefficient.
    """
    N = scenario["N"]
    e_ij = scenario["e_ij"]
    Phi = scenario["Phi"]
    delta = (np.asarray(scenario["alpha_coop"]) +
             np.asarray(scenario["alpha_expl"]))
    slack = np.inf
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            d_ij = delta[i, j]
            d_ji = delta[j, i]
            E_ij = e_ij[i, j]
            sl = np.sqrt(max(d_ij * d_ji, 0.0)) - Phi * E_ij
            if sl < slack:
                slack = sl
    return float(slack)


# ---------------------------------------------------------------------------
# Q9 -- Potentialness P_B
# ---------------------------------------------------------------------------


def pb_frobenius_exact(J: np.ndarray) -> Dict[str, float]:
    """Exact P_B = ||S||_F^2 / (||S||_F^2 + ||A||_F^2) from full Jacobian.

    Per handoff 2026-05-13 §2(a); Balduzzi 2018 §2 potentialness scalar.
    Returns norms and P_B; with full Jacobian it is exact up to FD error.
    """
    S, A = balduzzi_decompose(J)
    norm_S2 = float(np.sum(S * S))
    norm_A2 = float(np.sum(A * A))
    pb = norm_S2 / (norm_S2 + norm_A2 + 1e-30)
    return {"P_B": pb, "norm_S2": norm_S2, "norm_A2": norm_A2}


def pb_hutchinson(g_fn: Callable, z: np.ndarray, scenario: Dict[str, Any],
                  n_samples: int = 30, eps: float = 1e-4,
                  rng: Optional[np.random.Generator] = None) -> Dict[str, float]:
    """Hutchinson trace estimator for P_B without forming the full Jacobian.

    Uses two Hadamard-style identities:
      tr(J^T J) = ||S||_F^2 + ||A||_F^2,  estimable via E_v[||J v||^2].
      tr(J^2)   = ||S||_F^2 - ||A||_F^2,  estimable via E_v[v^T J (J v)].

    Both expectations under Rademacher v (entries +/-1 i.i.d.).
    JVPs implemented as central FD on g_fn.

    Per handoff 2026-05-13 §2(b).  Validate against exact pb_frobenius_exact
    on small N=3 instances before trusting on larger.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    d = len(z)
    sum_JtJ = 0.0
    sum_J2 = 0.0
    for _ in range(n_samples):
        v = rng.choice([-1.0, 1.0], size=d)
        zp = z + eps * v
        zm = z - eps * v
        Jv = (g_fn(zp, scenario) - g_fn(zm, scenario)) / (2 * eps)
        sum_JtJ += float(np.dot(Jv, Jv))
        nJv = float(np.linalg.norm(Jv))
        if nJv > 1e-12:
            u = Jv / nJv
            zp2 = z + eps * u
            zm2 = z - eps * u
            JJv = nJv * (g_fn(zp2, scenario) - g_fn(zm2, scenario)) / (2 * eps)
            sum_J2 += float(np.dot(v, JJv))
    avg_JtJ = sum_JtJ / n_samples
    avg_J2 = sum_J2 / n_samples
    norm_S2 = max((avg_JtJ + avg_J2) / 2.0, 0.0)
    norm_A2 = max((avg_JtJ - avg_J2) / 2.0, 0.0)
    pb = norm_S2 / (norm_S2 + norm_A2 + 1e-30)
    return {"P_B": pb, "norm_S2": norm_S2, "norm_A2": norm_A2,
            "tr_JtJ": float(avg_JtJ), "tr_J2": float(avg_J2)}


# ---------------------------------------------------------------------------
# Q10 -- divergence diagnostic on g_A
# ---------------------------------------------------------------------------


def divergence_on_antisymmetric(z: np.ndarray, scenario: Dict[str, Any],
                                eps: float = 1e-4) -> float:
    """Divergence of g_A = compute_flow_coupling at z:  div = sum_i d g_A_i / d z_i.

    Per handoff 2026-05-13 §3(a):  div(Du) ~ 0 inside Sylvester/Minty region
    is cross-validation of S3's "antisymmetric on conservative edges" claim
    (the Zhou-Dong-Li-Wang 2411.03802 Helmholtz/Hodge decomposition class).
    """
    d = len(z)
    div = 0.0
    for k in range(d):
        zp = z.copy(); zp[k] += eps
        zm = z.copy(); zm[k] -= eps
        gp = compute_flow_coupling(zp, scenario)
        gm = compute_flow_coupling(zm, scenario)
        div += (gp[k] - gm[k]) / (2 * eps)
    return float(div)


def jacobian_skew_residual(z: np.ndarray, scenario: Dict[str, Any],
                           eps: float = 1e-4) -> Tuple[float, np.ndarray]:
    """Residual of J(g_A) + J(g_A)^T at z (Frobenius norm + the matrix).

    Per handoff 2026-05-13 §3(b):  if J_A + J_A^T = 0 within numerical
    tolerance, g_A is genuinely Hamiltonian.
    """
    d = len(z)
    J = np.zeros((d, d))
    for k in range(d):
        zp = z.copy(); zp[k] += eps
        zm = z.copy(); zm[k] -= eps
        J[:, k] = (compute_flow_coupling(zp, scenario) -
                   compute_flow_coupling(zm, scenario)) / (2 * eps)
    skew_res = J + J.T
    return float(np.linalg.norm(skew_res)), skew_res


# ---------------------------------------------------------------------------
# Q11 -- cycle vs saturation outcome classifier
# ---------------------------------------------------------------------------


def classify_trajectory(traj: np.ndarray, alpha_idx_arr: np.ndarray,
                        late_frac: float = 0.5,
                        var_cycle_thresh: float = 1e-4,
                        var_fixed_thresh: float = 1e-5,
                        diverged: bool = False,
                        box_lo: float = 0.0, box_hi: float = 1.0,
                        boundary_eps: float = 1e-3,
                        boundary_frac: float = 0.5,
                        spectral_peak_ratio: float = 4.0,
                        spectral_min_amp: float = 5e-3) -> Dict[str, Any]:
    """Classify a trajectory into one of four outcomes per handoff 2026-05-13 §4.

    Detection has two channels:
      - Variance channel: late-window variance on the alpha block exceeds
        `var_cycle_thresh`.  Default lowered to 1e-4 (was 5e-3); for
        alpha in [0,1] over 800 steps at lr=0.001 a small bounded cycle
        of amplitude ~0.03 has variance ~5e-4 — well within the genuine-
        cycle regime but below the historical threshold.
      - Spectral channel: peak-to-broadband ratio of the late-window FFT
        of mean-alpha exceeds `spectral_peak_ratio` AND the peak amplitude
        exceeds `spectral_min_amp`.  This catches narrow-spectrum cycles
        whose variance is small but whose dominant frequency has
        significant power.  Both conditions matter — a sharp peak with
        tiny amplitude is FD noise, not a cycle.

        Caveat: the spectral channel takes `late[:, alpha_idx_arr].mean(axis=1)`
        as its signal.  If multiple agents cycle at the same frequency but
        with phases ~pi apart, their mean can phase-cancel and the spectral
        peak collapses to noise — the variance channel still picks up such
        multi-agent rotation modes because per-agent variance is unaffected
        by inter-agent phase.  When suspected, inspect per-agent traces
        directly rather than relying on the spectral channel alone.

    Outcomes:
      - divergence: caller flags `diverged=True`.
      - limit_cycle: variance OR spectral channel triggers.
      - corner_saturation: late variance below var_fixed_thresh AND
        >= boundary_frac of alpha entries within boundary_eps of box.
      - fixed_point_interior: late variance below var_fixed_thresh, NOT
        at boundary.

    Returns dict with `outcome`, `late_var`, `boundary_frac_observed`,
    plus spectral diagnostics (`spectral_peak_amp`, `spectral_peak_ratio`).
    """
    if diverged:
        return {"outcome": "divergence", "late_var": float("nan"),
                "boundary_frac_observed": float("nan"),
                "spectral_peak_amp": float("nan"),
                "spectral_peak_ratio": float("nan"),
                "cycle_channel": "n/a"}
    n_steps = len(traj)
    late_start = max(0, int(n_steps * (1.0 - late_frac)))
    late = traj[late_start:]
    if len(alpha_idx_arr) == 0:
        late_var = float(np.mean(np.var(late, axis=0)))
        signal = late.mean(axis=1)
    else:
        late_var = float(np.mean(np.var(late[:, alpha_idx_arr], axis=0)))
        signal = late[:, alpha_idx_arr].mean(axis=1)
    final = traj[-1]
    if len(alpha_idx_arr) == 0:
        at_boundary = (np.abs(final - box_lo) < boundary_eps) | \
                      (np.abs(final - box_hi) < boundary_eps)
        bfrac = float(np.mean(at_boundary))
    else:
        f_alpha = final[alpha_idx_arr]
        at_boundary = (np.abs(f_alpha - box_lo) < boundary_eps) | \
                      (np.abs(f_alpha - box_hi) < boundary_eps)
        bfrac = float(np.mean(at_boundary))

    # Spectral analysis on the late-window mean-alpha signal.  Real periodic
    # cycles have a sharp peak at a frequency well above DC; slow drifts
    # produce a peak at index 1 (the lowest non-DC bin) and aren't cycles.
    # We require the dominant peak to sit at index >= 2 (period < N/2) AND
    # to dominate the broadband floor.
    spec_peak_amp = 0.0
    spec_peak_ratio = 0.0
    spec_peak_period = 0.0
    if len(signal) > 16:
        sig_c = signal - signal.mean()
        # Detrend linearly to suppress slow drifts before FFT
        t_idx = np.arange(len(sig_c), dtype=float)
        slope, intercept = np.polyfit(t_idx, sig_c, 1)
        sig_detrended = sig_c - (slope * t_idx + intercept)
        spec = np.abs(np.fft.rfft(sig_detrended))
        if len(spec) > 4:
            spec[0] = 0.0  # DC
            spec[1] = 0.0  # Lowest non-zero bin (still drift-like)
            broadband_floor = float(np.median(spec[2:]))
            peak_idx = int(np.argmax(spec))
            spec_peak_amp = float(spec[peak_idx]) / len(sig_detrended)
            spec_peak_ratio = (float(spec[peak_idx]) /
                                max(broadband_floor, 1e-12))
            spec_peak_period = (float(len(sig_detrended)) /
                                 max(peak_idx, 1))

    # Cycle detection requires BOTH non-trivial motion AND a clean
    # interior-frequency spectral peak.  Mere variance does not separate
    # drift from cycles — a slow monotone drift over the late window
    # contributes variance that grows with window length.  We detect
    # cycles by:
    #   (i) late-window variance above `var_cycle_thresh` (real motion);
    #  (ii) a spectral peak at a period in the interior (period < N/2,
    #       i.e. peak_idx >= 2 in the rfft after DC/near-DC removal); and
    # (iii) the spectral peak amplitude must exceed `spectral_min_amp` and
    #       its peak-to-broadband ratio must exceed `spectral_peak_ratio`.
    # All three conditions must hold (AND, not OR) — a slow drift in
    # alpha registers as variance but fails (ii)/(iii).
    cycle_var = late_var >= var_cycle_thresh
    cycle_spec = (spec_peak_ratio >= spectral_peak_ratio and
                   spec_peak_amp >= spectral_min_amp and
                   spec_peak_period < len(signal) / 2.0)
    is_cycle = cycle_var and cycle_spec
    cycle_channel = "n/a"
    if is_cycle:
        cycle_channel = "variance+spectral"
    elif cycle_var and not cycle_spec:
        cycle_channel = "variance_only(rejected)"
    elif cycle_spec and not cycle_var:
        cycle_channel = "spectral_only(rejected)"

    if is_cycle:
        outcome = "limit_cycle"
    elif bfrac >= boundary_frac:
        # Substantial fraction at the box boundary — saturation.  This
        # covers both static corners (var <= var_fixed_thresh) and slow
        # drift onto a corner (var_fixed_thresh < var < var_cycle_thresh
        # with no spectral peak).
        outcome = "corner_saturation"
    elif late_var <= var_fixed_thresh:
        outcome = "fixed_point_interior"
    else:
        # Non-trivial motion (var > var_fixed_thresh) that isn't a cycle
        # and isn't pinned at the boundary — slow drift toward an
        # interior basin.  Treat as fixed_point_interior since the
        # trajectory is bounded and converging (just not converged in the
        # finite integration window).
        outcome = "fixed_point_interior"
    return {"outcome": outcome, "late_var": late_var,
            "boundary_frac_observed": bfrac,
            "spectral_peak_amp": spec_peak_amp,
            "spectral_peak_ratio": spec_peak_ratio,
            "spectral_peak_period": spec_peak_period,
            "cycle_channel": cycle_channel}


def cycle_characterization(traj: np.ndarray, alpha_idx_arr: np.ndarray,
                           late_frac: float = 0.5,
                           dt: float = 1.0) -> Dict[str, float]:
    """For limit_cycle outcomes, characterize amplitude / period / basin estimate.

    Amplitude: peak-to-peak range of late trajectory mean-alpha.
    Period: peak-detection on late trajectory; otherwise FFT dominant frequency.
    Basin estimate: |mean late alpha| - center of box (proxy for how far in basin).
    """
    n_steps = len(traj)
    late_start = max(0, int(n_steps * (1.0 - late_frac)))
    late = traj[late_start:]
    if len(alpha_idx_arr) == 0:
        signal = late.mean(axis=1)
    else:
        signal = late[:, alpha_idx_arr].mean(axis=1)
    amp = float(np.ptp(signal))
    # FFT dominant period
    sig_c = signal - signal.mean()
    spec = np.abs(np.fft.rfft(sig_c))
    if len(spec) > 2:
        spec[0] = 0.0
        idx = int(np.argmax(spec))
        period = float(len(sig_c) * dt / max(idx, 1))
    else:
        period = float("nan")
    basin_proxy = float(abs(signal.mean() - 0.5))
    return {"amplitude": amp, "period": period, "basin_proxy": basin_proxy}


# ---------------------------------------------------------------------------
# Q8 / Q11 scenario builders
# ---------------------------------------------------------------------------


def build_bilinear_flow_scenario(N: int = 3, seed: int = 1234,
                                  Phi_override: Optional[float] = 1.2,
                                  **kw) -> Dict[str, Any]:
    """TC-class scenario with bilinear flow form (Asm 3.2 case (a), T_A = 0).

    Per derivation 07 §3.2 / 4.1: when x_ij = w_i * w_j (truly bilinear in
    producer/consumer inputs separately), the cross-second-derivative is
    constant, the antisymmetric block of G_L is z-independent, and T_A
    vanishes identically.  This scenario is the special-regime check
    against case (b) (the biquadratic default).
    """
    sc = build_tc_scenario(N=N, seed=seed, Phi_override=Phi_override, **kw)
    sc["flow_form"] = "bilinear"
    return sc


def build_tc_xii_heterogeneous_scenario(N: int = 3, n_types: int = 2,
                                         seed: int = 4321,
                                         heterogeneity_strength: float = 1.5,
                                         **kw) -> Dict[str, Any]:
    """TC-XII heterogeneous-type scenario (Q8b) admitting multiple equilibria.

    Per TC-XII (R1)-(R3) the type distribution makes the cooperative VE set
    multi-component generically when type heterogeneity is non-trivial.
    This builder constructs a scenario with n_types distinct type clusters
    in agent space; the multistart VE solver should find multiple equilibria.

    heterogeneity_strength scales the per-type curvature spread.
    """
    sc = build_tc_scenario(N=N, seed=seed, **kw)
    rng = np.random.default_rng(seed + 7)
    sc = dict(sc)
    # Inject per-type curvature spread by perturbing per-agent beta_U / alpha_U.
    # Each agent assigned to a type; types differ in utility-curvature scale.
    type_assign = rng.integers(0, n_types, size=N)
    type_scales = 1.0 + heterogeneity_strength * (rng.uniform(-0.5, 0.5, size=n_types))
    for i in range(N):
        s = type_scales[type_assign[i]]
        sc["beta_ij_U"][i] = sc["beta_ij_U"][i] * s
        sc["alpha_ij_U"][i] = sc["alpha_ij_U"][i] * s
        sc["theta"][i]["beta_U"] = sc["beta_ij_U"][i]
        sc["theta"][i]["alpha_U"] = sc["alpha_ij_U"][i]
    # Increase pairwise contest-energy spread to disrupt symmetric coupling
    sc["e_ij"] = sc["e_ij"] * (1.0 + 0.5 * heterogeneity_strength)
    sc["type_assign"] = type_assign
    sc["type_scales"] = type_scales
    return sc


def build_tc_xi_hopf_scenario(N: int = 3, seed: int = 555,
                              Phi_override: float = 8.0,
                              hopf_beta: float = 1.0,
                              e_sym_base: float = 5.0,
                              **kw) -> Dict[str, Any]:
    """Scenario tuned toward TC-XI thm-endogenous-bifurcations Hopf-territory.

    TC-XI's Hopf is in the augmented (r, G, tau, I) macro coexistence
    dynamics; the composed-pseudogradient analog is whether the cross-agent
    coupling in compute_g's Jacobian produces complex-conjugate eigenvalues
    near the imaginary axis at the cooperative VE.

    compute_g doesn't carry the resource-flow coupling (that's in
    compute_G_L only), so the analog cycle-producing coupling must come
    through the supermodular-contest term e_ij — specifically an
    asymmetric e_ij with rotational structure (e_{ij} - e_{ji} != 0 in
    a directed cycle pattern).

    Parameterization (rev: decoupled magnitude / asymmetry):
        e_ij = e_sym + hopf_beta * rotation_pattern,
    where `rotation_pattern[i,j] = +1 for j = (i+1) mod N, -1 for the
    reverse`, and `e_sym` is a symmetric base whose floor `e_sym_base`
    is chosen large enough that for hopf_beta in the swept range
    `e_sym >= hopf_beta * rotation_magnitude` element-wise — i.e. the
    full e_ij stays strictly positive without any np.maximum clamp.
    This preserves antisymmetry (e_ij - e_ji = 2 * hopf_beta exactly on
    forward cycle edges) so the rotational structure scales linearly
    with hopf_beta as intended.

    hopf_beta = 1.0 is the nominal transversal-crossing point per the
    TC-XI example at line 142.  e_sym_base = 5.0 supports hopf_beta up
    to ~4 without clamping.
    """
    sc = build_tc_scenario(N=N, seed=seed, Phi_override=Phi_override, **kw)
    sc = dict(sc)
    rng = np.random.default_rng(seed)
    # Symmetric base with sufficient floor to absorb hopf_beta scale.
    e_sym = rng.uniform(e_sym_base, e_sym_base * 1.5, size=(N, N))
    e_sym = (e_sym + e_sym.T) / 2.0
    np.fill_diagonal(e_sym, 0.0)
    # Directed-cycle rotation: i preferentially pressures (i+1)
    e_rot = np.zeros((N, N))
    for i in range(N):
        e_rot[i, (i + 1) % N] = 1.0
        e_rot[(i + 1) % N, i] = -1.0
    # Build full e_ij; with e_sym_base = 5.0 and |hopf_beta| <= 4, all
    # entries stay positive without clamping (preserves antisymmetric
    # signal cleanly).
    e_full = e_sym + hopf_beta * e_rot
    np.fill_diagonal(e_full, 0.0)
    # Sanity check (off-diagonal only): if user pushes hopf_beta beyond the
    # safe range, fall back to a positivity floor with an explicit warning
    # record so callers can see it.  Diagonal entries are zero by convention
    # (no self-contest) and excluded from the check.
    off_diag_mask = ~np.eye(N, dtype=bool)
    if ((e_full < 0.05) & off_diag_mask).any():
        clamped_mask = (e_full < 0.05) & off_diag_mask
        e_full = np.where(clamped_mask, 0.05, e_full)
        sc["e_ij_clamp_warning"] = (
            f"hopf_beta={hopf_beta} exceeds e_sym_base={e_sym_base} safe range; "
            f"{int(clamped_mask.sum())} off-diagonal entries clamped to 0.05.")
    np.fill_diagonal(e_full, 0.0)
    sc["e_ij"] = e_full
    # Moderate symmetric coupling — keep some curvature so a VE exists
    sc["alpha_coop"] = sc["alpha_coop"] * 0.3
    sc["alpha_expl"] = sc["alpha_expl"] * 0.3
    # Also scale pi_star for completeness (affects compute_G_L Jacobian only)
    sc["pi_star"] = sc["pi_star"] * hopf_beta
    sc["hopf_beta"] = hopf_beta
    sc["e_sym_base"] = e_sym_base
    return sc


def build_tc_viii_production_cycle_scenario(
    N: int = 3, seed: int = 333,
    Phi_override: float = 3.0,
    cycle_rho: float = 0.85,
    **kw) -> Dict[str, Any]:
    """Scenario tuned toward TC-VIII prop-production-cycles (damped oscillation).

    TC-VIII's production cycles arise from dominant Jacobian eigenvalue
    lambda_1 with |lambda_1| = cycle_rho < 1 and Im(lambda_1) != 0.  Three
    agents in a directed cycle with weak coupling produces complex
    dominant eigenvalues; the cycle period is 2 pi / |Im log lambda_1|.

    To affect compute_g dynamics we shape e_ij (the cross-agent contest
    coupling) into a rotational pattern; cycle_rho scales the magnitude
    of the rotational off-diagonal so larger cycle_rho => closer to
    Hopf threshold.
    """
    sc = build_tc_scenario(N=N, seed=seed, Phi_override=Phi_override, **kw)
    sc = dict(sc)
    rng = np.random.default_rng(seed)
    # Cyclic e_ij pattern matching trophic triangle example (TC-VIII line 250)
    e_cyc = np.zeros((N, N))
    for i in range(N):
        e_cyc[i, (i + 1) % N] = cycle_rho
        e_cyc[i, (i - 1) % N] = cycle_rho * 0.3  # asymmetric backward
    np.fill_diagonal(e_cyc, 0.0)
    sc["e_ij"] = e_cyc
    # Weak symmetric compliance coupling (damping)
    sc["alpha_coop"] = sc["alpha_coop"] * (1.0 - cycle_rho * 0.5)
    sc["alpha_expl"] = sc["alpha_expl"] * (1.0 - cycle_rho * 0.5)
    sc["cycle_rho"] = cycle_rho
    return sc


# ---------------------------------------------------------------------------
# Q12 -- compute_G_L primal-dual dynamics
# ---------------------------------------------------------------------------
#
# Q11 integrated compute_g (the agent-level gradient-of-utility pseudogradient)
# under projected gradient ascent and classified 26 parameter points.  Verdict
# was `interpretation_i` (no cycles) -- but compute_g does NOT carry the
# resource-flow Lagrangian coupling, which lives in compute_G_L.  The
# antisymmetric Jacobian structure produced by the conservative-edge flow term
# (S3 §4.1) is structurally absent from compute_g.
#
# Q12 closes the scope caveat by integrating compute_G_L with the flow-balance
# equality constraint dualized into a multiplier vector m in R^n.  The
# Lagrangian for the flow-balance equality is
#
#     L(z, m) = phi(z) - m^T s(z)
#
# where phi(z) is the implicit potential whose gradient is compute_G_L(z)
# (modulo the constant resource-flow piece R = J_f^T pi*).  The primal-dual
# saddle-point dynamics are
#
#     dz/dt =  d/dz L = compute_G_L(z) - J_s(z)^T m
#     dm/dt = -d/dm L = s(z)
#
# Since J_s(z) is the constant +/-1 incidence matrix of the flow-balance
# constraint (s_j = sum_i x_in_ij - sum_i x_out_ij), J_s^T m is simply m
# delivered to the x_in block (positive) and -m delivered to the x_out block
# (negative) on each resource.  No matrix needs to be built.
#
# The box constraints (x_in >= eps, x_out >= eps, alpha in [floor, 1],
# c in [0, 1]) are enforced by projection on the primal step (matches Q11's
# `project_to_feasible_box`).  The flow-balance multiplier m is unrestricted
# (equality constraint).
#
# Outcome question for Q12a: does this primal-dual flow produce limit cycles
# in TC-class regimes where Q11 saw only saturation?  Outcome (a) per the
# handoff: cycles emerge => operator choice matters; outcome (b) saturation
# also => operator choice less consequential.


def _flow_balance_jacobian_T_m(m: np.ndarray, scenario: Dict[str, Any]) -> np.ndarray:
    """Compute J_s(z)^T @ m where s(z) is the flow-balance constraint.

    s_j(z) = sum_i x_in_ij - sum_i x_out_ij  is LINEAR in z, so J_s is a
    constant +/-1 incidence matrix.  J_s^T m delivers +m_j to the x_in_ij
    slot of every agent i and -m_j to the x_out_ij slot.

    Returns a vector of the same dimension as z.
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    out = np.zeros(N * d_i)
    for i in range(N):
        s = i * d_i
        out[s:s+n] = m              # +m on x_in
        out[s+n:s+2*n] = -m         # -m on x_out
    return out


def primal_dual_step(z: np.ndarray, m: np.ndarray,
                     scenario: Dict[str, Any],
                     lr_primal: float, lr_dual: float,
                     scheme: str = "forward_euler") -> Tuple[np.ndarray, np.ndarray]:
    """One step of primal-dual integration on
        L(z, m) = phi(z) - m^T s(z)
    with compute_G_L as d phi / dz, ascending in z, descending in m on L
    (equivalently ascending the saddle: dz/dt = d_z L, dm/dt = -d_m L = s).

    scheme:
      - "forward_euler": straight Euler step on both primal and dual.
      - "extragradient": Korpelevich extragradient — predict then correct.
        More stable on saddle points (avoids the cycling instability of
        Euler on Hamiltonian games).

    Returns updated (z, m).  Box projection on z is the caller's
    responsibility (apply project_to_feasible_box after this).  The dual m
    is unconstrained (equality constraint).
    """
    def grad_z(z_eval, m_eval):
        return compute_G_L(z_eval, scenario) - _flow_balance_jacobian_T_m(m_eval, scenario)

    def grad_m(z_eval):
        return flow_balance(z_eval, scenario)

    if scheme == "forward_euler":
        dz = grad_z(z, m)
        ds = grad_m(z)
        z_new = z + lr_primal * dz
        m_new = m + lr_dual * ds
        return z_new, m_new
    elif scheme == "extragradient":
        # Korpelevich: predict half-step, evaluate at predicted point, correct.
        dz_h = grad_z(z, m)
        ds_h = grad_m(z)
        z_h = z + lr_primal * dz_h
        m_h = m + lr_dual * ds_h
        dz = grad_z(z_h, m_h)
        ds = grad_m(z_h)
        z_new = z + lr_primal * dz
        m_new = m + lr_dual * ds
        return z_new, m_new
    else:
        raise ValueError(f"Unknown scheme: {scheme!r}")


def integrate_primal_dual(scenario: Dict[str, Any],
                          z0: Optional[np.ndarray] = None,
                          m0: Optional[np.ndarray] = None,
                          n_steps: int = 800,
                          lr_primal: float = 0.001,
                          lr_dual: float = 0.001,
                          scheme: str = "forward_euler",
                          project_primal: bool = True,
                          divergence_norm: float = 1e6) -> Dict[str, Any]:
    """Integrate the primal-dual flow on L(z, m) = phi(z) - m^T s(z) where
    d_z phi = compute_G_L and s(z) is the flow-balance equality residual.

    Returns dict with:
        z_traj      : (T+1, d) primal trajectory
        m_traj      : (T+1, n) dual trajectory
        diverged    : bool
        n_steps_run : int (= T)
        scheme      : str

    The dual m is initialized at zero by default (or m0 if provided).  Some
    callers may prefer initializing at the scenario-supplied pi_star -- but
    pi_star is per-agent per-resource (N,n) and m is just per-resource (n,)
    for the flow-balance constraint, so the natural default is zero.
    """
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    alpha_floor = scenario["alpha_floor"]

    if z0 is None:
        z0 = np.zeros(N * d_i)
        for i in range(N):
            s = i * d_i
            z0[s:s+n] = 0.5; z0[s+n:s+2*n] = 0.5
            z0[s+2*n:s+2*n+(N-1)] = 0.5
            z0[s+2*n+(N-1)] = 0.1
    if m0 is None:
        m0 = np.zeros(n)

    z = project_to_feasible_box(z0.copy(), scenario) if project_primal else z0.copy()
    m = m0.copy()
    z_traj = [z.copy()]
    m_traj = [m.copy()]
    diverged = False
    for step in range(n_steps):
        try:
            z_new, m_new = primal_dual_step(z, m, scenario, lr_primal, lr_dual,
                                            scheme=scheme)
        except Exception:
            diverged = True; break
        if project_primal:
            z_new = project_to_feasible_box(z_new, scenario)
        z = z_new; m = m_new
        z_traj.append(z.copy())
        m_traj.append(m.copy())
        if (not np.all(np.isfinite(z)) or not np.all(np.isfinite(m))
                or np.linalg.norm(z) > divergence_norm
                or np.linalg.norm(m) > divergence_norm):
            diverged = True; break
    return {
        "z_traj": np.array(z_traj),
        "m_traj": np.array(m_traj),
        "diverged": diverged,
        "n_steps_run": len(z_traj) - 1,
        "scheme": scheme,
    }


def solve_primal_dual_ve(scenario: Dict[str, Any],
                         n_starts: int = 10,
                         max_iter: int = 4000,
                         lr_primal: float = 0.01,
                         lr_dual: float = 0.01,
                         tol: float = 1e-5,
                         rng: Optional[np.random.Generator] = None) -> Dict[str, Any]:
    """Find the primal-dual VE (z*, m*) where compute_G_L(z*) - J_s^T m* = 0
    in the projected sense AND flow_balance(z*) = 0.

    Uses extragradient on a multistart loop.  Returns the best (z*, m*) by
    combined residual.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    N = scenario["N"]
    n = scenario["n"]
    d_i = _per_agent_dim(scenario)
    alpha_floor = scenario["alpha_floor"]

    best = None
    best_obj = np.inf
    for start in range(n_starts):
        z = np.zeros(N * d_i)
        for i in range(N):
            s = i * d_i
            opt_xin = scenario["alpha_ij_U"][i] / scenario["beta_ij_U"][i]
            z[s:s+n] = rng.uniform(0.5 * opt_xin, 1.5 * opt_xin, n)
            z[s+n:s+2*n] = z[s:s+n].copy()  # x_out = x_in (flow balanced)
            z[s+2*n:s+2*n+(N-1)] = rng.uniform(alpha_floor[i] + 0.01, 1.0, N - 1)
            z[s+2*n+(N-1)] = 0.0
        z = project_to_feasible_box(z, scenario)
        m = np.zeros(n)
        lr_p = lr_primal; lr_d = lr_dual
        for it in range(max_iter):
            z_new, m_new = primal_dual_step(z, m, scenario, lr_p, lr_d,
                                            scheme="extragradient")
            z_new = project_to_feasible_box(z_new, scenario)
            # Residuals
            grad_z = compute_G_L(z_new, scenario) - _flow_balance_jacobian_T_m(m_new, scenario)
            primal_res = projected_residual(grad_z, z_new, scenario)
            flow_viol = float(np.linalg.norm(flow_balance(z_new, scenario)))
            z = z_new; m = m_new
            if primal_res < tol and flow_viol < tol:
                break
            if it % 500 == 499:
                lr_p *= 0.8; lr_d *= 0.8
        obj = primal_res + 10.0 * flow_viol
        if obj < best_obj:
            best_obj = obj
            best = {
                "z_star": z.copy(), "m_star": m.copy(),
                "primal_residual": float(primal_res),
                "flow_violation": float(flow_viol),
                "iterations": it + 1,
            }
    return best


def minty_residual_GL(z_prime: np.ndarray, z_star: np.ndarray,
                       m_star: np.ndarray, scenario: Dict[str, Any]) -> float:
    """Minty inner product on the primal direction of the joint flow with
    multipliers held fixed at m_star.

    F_primal(z) = -[compute_G_L(z) - J_s^T m_star]
    Residual: <F_primal(z'), z' - z*> = -<compute_G_L(z') - J_s^T m_star, z' - z*>

    Note: at the primal-dual VE (z*, m*), the *projected* primal gradient
    (compute_G_L(z*) - J_s^T m*) vanishes in the interior directions of R
    (Q1 §4.1 normal-cone reading).  The Minty inequality on the primal-
    direction monotonicity uses F_primal evaluated at z' with multipliers
    held at m_star.  This matches the derivation 07 §2-§4 analysis with
    g_L = compute_G_L + dualized terms.
    """
    grad_z = (compute_G_L(z_prime, scenario)
              - _flow_balance_jacobian_T_m(m_star, scenario))
    return float(-np.dot(grad_z, z_prime - z_star))


def empirical_minty_radius_GL(z_star: np.ndarray, m_star: np.ndarray,
                              scenario: Dict[str, Any],
                              n_dirs: int = 40, n_levels: int = 30,
                              r_max: float = 1.0, tol: float = -1e-3,
                              frac_pass_threshold: float = 0.8,
                              project: bool = True,
                              rng: Optional[np.random.Generator] = None) -> Dict[str, Any]:
    """Empirical Minty radius on F_primal = -[compute_G_L - J_s^T m_star]
    in the same contiguous-pass / 80%-threshold convention as
    `empirical_minty_radius`.

    Sampling and projection identical to the Q8 routine; only the residual
    formula changes (F is the primal-direction part of the Lagrangian
    gradient, not compute_g).
    """
    if rng is None:
        rng = np.random.default_rng(0)
    d = len(z_star)
    dirs = []
    for _ in range(n_dirs):
        v = rng.standard_normal(d)
        nv = np.linalg.norm(v)
        if nv > 1e-12:
            dirs.append(v / nv)
    levels = np.linspace(r_max / n_levels, r_max, n_levels)
    contiguous_radius = 0.0
    contiguous_broken = False
    last_passing_radius = 0.0
    per_level_stats = []
    for r in levels:
        residuals = []
        for v in dirs:
            zp = z_star + r * v
            if project:
                zp = project_to_feasible_box(zp, scenario)
            residuals.append(minty_residual_GL(zp, z_star, m_star, scenario))
        residuals = np.array(residuals)
        n_pass = int(np.sum(residuals >= tol))
        frac_pass = n_pass / len(residuals)
        per_level_stats.append({
            "r": float(r), "frac_pass": frac_pass,
            "min_res": float(residuals.min()),
            "median_res": float(np.median(residuals)),
            "max_res": float(residuals.max()),
        })
        if frac_pass >= frac_pass_threshold:
            last_passing_radius = r
            if not contiguous_broken:
                contiguous_radius = r
        else:
            contiguous_broken = True
    return {
        "empirical_radius": float(contiguous_radius),
        "last_passing_radius": float(last_passing_radius),
        "per_level_stats": per_level_stats,
        "n_dirs": len(dirs),
        "frac_pass_threshold": frac_pass_threshold,
        "tol": tol,
    }


def per_equilibrium_minty_radius_GL_theoretical(
    z_star: np.ndarray, m_star: np.ndarray, scenario: Dict[str, Any],
    eps_fd: float = 1e-4,
    n_dirs_T_A: int = 32,
    h_T_A: float = 0.05,
    rng: Optional[np.random.Generator] = None) -> Dict[str, float]:
    """Theoretical per-equilibrium Minty ball radius for the primal direction
    of compute_G_L with multipliers held at m_star.

    Same formula as `per_equilibrium_minty_radius_theoretical` (07 §4.1) but
    with the Jacobian of the *primal* gradient F_primal = -(compute_G_L -
    J_s^T m_star) replacing compute_g's Jacobian.  J_s^T m_star is linear
    in z (in fact constant once m_star is fixed), so its Jacobian
    contribution is zero -- the Jacobian of F_primal w.r.t. z is just
    minus the Jacobian of compute_G_L w.r.t. z.

    Reports both full-space and tangent-space mu_S^- (Q8 finding: at
    projected VEs the full-space mu_S^- is exactly zero on boundary-active
    directions; the tangent-space variant projects those out).
    """
    if rng is None:
        rng = np.random.default_rng(0)

    # Jacobian of compute_G_L at z* (with multipliers held in pi_star fixed
    # — note pi_star is the scenario-level dual not the flow-balance m).
    J = compute_jacobian_GL(z_star, scenario, eps=eps_fd)
    # F_primal = -compute_G_L + J_s^T m_star; J_F = -J (linear m term drops out)
    # The symmetric/antisymmetric structure inherits sign from J:
    # under F = -g convention, "monotone F" means J_S(F) = -J_S(g) is PSD;
    # mu_S^- := lambda_min(J_S(F)) = lambda_min(-J_S(g)) which is exactly
    # the same definition the Q8 routine uses on compute_G_L.
    S_J = (J + J.T) / 2.0
    eigs = np.linalg.eigvalsh(-S_J)
    mu_S_minus = float(max(eigs.min(), 0.0))
    eig_tol = max(eps_fd * float(np.max(np.abs(eigs))), 1e-8)
    positive_eigs = eigs[eigs > eig_tol]
    mu_S_minus_tangent = float(positive_eigs.min()) if len(positive_eigs) > 0 else 0.0

    # ||T_A||_op via second-order central difference on flow_coupling
    # (same primitive as Q8 — flow_coupling IS the z-dependent antisymmetric
    # component of compute_G_L).
    d = len(z_star)
    h = h_T_A
    g_A_star = compute_flow_coupling(z_star, scenario)
    gL_star = compute_G_L(z_star, scenario)

    # Linear (Jacobian) of compute_G_L for cubic-residual estimator
    JgL_at = np.zeros((d, d))
    for k in range(d):
        zp = z_star.copy(); zp[k] += eps_fd
        zm = z_star.copy(); zm[k] -= eps_fd
        JgL_at[:, k] = (compute_G_L(zp, scenario) -
                        compute_G_L(zm, scenario)) / (2 * eps_fd)

    T_A_op = 0.0
    C_3 = 0.0
    for _ in range(n_dirs_T_A):
        v = rng.standard_normal(d)
        nv = np.linalg.norm(v)
        if nv < 1e-12:
            continue
        v_unit = v / nv
        zp = z_star + h * v_unit
        zm = z_star - h * v_unit
        second = (compute_flow_coupling(zp, scenario) +
                  compute_flow_coupling(zm, scenario) -
                  2 * g_A_star) / (h ** 2)
        T_A_op = max(T_A_op, float(np.linalg.norm(second)))
        # C_3 third-derivative on compute_G_L (not compute_g — Q12 measures
        # the symmetric-cubic floor on the actual integrated vector field).
        zp2 = z_star + 2 * h * v_unit
        zm2 = z_star - 2 * h * v_unit
        cubic_vvv = (compute_G_L(zp2, scenario) - compute_G_L(zm2, scenario) -
                     4 * h * (JgL_at @ v_unit) -
                     4 * h * (compute_G_L(zp, scenario) - compute_G_L(zm, scenario) -
                              2 * h * (JgL_at @ v_unit))) / (2 * h ** 3)
        C_3 = max(C_3, float(np.linalg.norm(cubic_vvv)))

    rho_S = mu_S_minus / (2 * C_3) if C_3 > 1e-12 else np.inf
    rho_A = mu_S_minus / T_A_op if T_A_op > 1e-12 else np.inf
    rho = min(rho_S, rho_A)
    rho_S_tangent = mu_S_minus_tangent / (2 * C_3) if C_3 > 1e-12 else np.inf
    rho_A_tangent = mu_S_minus_tangent / T_A_op if T_A_op > 1e-12 else np.inf
    rho_tangent = min(rho_S_tangent, rho_A_tangent)
    return {
        "mu_S_minus": mu_S_minus,
        "mu_S_minus_tangent": mu_S_minus_tangent,
        "T_A_op": float(T_A_op),
        "C_3": float(C_3),
        "rho_S": float(rho_S),
        "rho_A": float(rho_A),
        "rho": float(rho),
        "rho_S_tangent": float(rho_S_tangent),
        "rho_A_tangent": float(rho_A_tangent),
        "rho_tangent": float(rho_tangent),
    }


def classify_primal_dual_trajectory(z_traj: np.ndarray, m_traj: np.ndarray,
                                    alpha_idx_arr: np.ndarray,
                                    late_frac: float = 0.5,
                                    var_cycle_thresh: float = 5e-3,
                                    var_fixed_thresh: float = 1e-5,
                                    diverged: bool = False,
                                    box_lo: float = 0.0, box_hi: float = 1.0,
                                    boundary_eps: float = 1e-3,
                                    boundary_frac: float = 0.5,
                                    dual_cycle_thresh: float = 1e-3) -> Dict[str, Any]:
    """Classify a primal-dual trajectory on the PRIMAL alpha block (matches
    Q11 methodology -- the architectural question is about primal saturation
    vs primal cycles), and additionally flag whether the dual coordinates
    are cycling.

    The primary outcome label uses `classify_trajectory` on z_traj.  A
    secondary `dual_cycling` flag is True iff the late-trajectory variance
    of m_traj exceeds `dual_cycle_thresh` -- diagnostic only.
    """
    primal_cls = classify_trajectory(z_traj, alpha_idx_arr,
                                     late_frac=late_frac,
                                     var_cycle_thresh=var_cycle_thresh,
                                     var_fixed_thresh=var_fixed_thresh,
                                     diverged=diverged,
                                     box_lo=box_lo, box_hi=box_hi,
                                     boundary_eps=boundary_eps,
                                     boundary_frac=boundary_frac)
    if diverged or len(m_traj) == 0:
        primal_cls["dual_cycling"] = False
        primal_cls["dual_late_var"] = float("nan")
        return primal_cls

    n_steps = len(m_traj)
    late_start = max(0, int(n_steps * (1.0 - late_frac)))
    late_m = m_traj[late_start:]
    dual_late_var = float(np.mean(np.var(late_m, axis=0))) if late_m.size > 0 else 0.0
    primal_cls["dual_late_var"] = dual_late_var
    primal_cls["dual_cycling"] = bool(dual_late_var >= dual_cycle_thresh)
    return primal_cls
