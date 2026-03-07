# Lagrangian Constraints — Rights as Boundary Conditions

---

## 0. Preamble

This document contains the formal mathematical derivation for the rights-as-constraints framework. The contribution is **applied mathematics**: we use the calculus of variations (constrained optimization, KKT theory) to prove that a "right" in multi-agent systems is formally equivalent to an inequality constraint in each agent's optimization problem. The thermodynamic grounding provides axioms and intuition; the mathematics provides the proof.

**Key references for the tools used:**

- [@Boyd2004] — KKT conditions, shadow prices.
- [@Facchinei2010] — coupled multi-agent optimization.
- [@Rosen1965] — variational equilibrium.

---

## 1. Variable Space: The Agent Action-Resource Model

### 1.1 Primitive Objects

Consider a system of $N \geq 2$ **agents** (entities) sharing an environment with $n$ **resource dimensions**. Each agent $i \in \{1, \ldots, N\}$ selects a **strategy vector** (action vector):

$$\mathbf{x}_i = (x_{i1}, x_{i2}, \ldots, x_{in}) \in \mathbb{R}_{\geq 0}^n$$

where component $x_{ij} \geq 0$ represents the quantity of resource $j$ that agent $i$ allocates to (consumes, claims, or utilizes). The non-negativity constraint reflects the physical impossibility of negative consumption.

**Interpretation:** The vector $\mathbf{x}_i$ is the agent's *resource-allocation strategy* — the complete description of how it distributes its effort across available resources to preserve its identity. In the language of the paper (§I), this is the quantitative representation of the agent's "physical vector" to acquire energy and maintain its boundary.

### 1.2 The Resource Environment

The environment provides a **finite resource endowment**:

$$\mathbf{R} = (R_1, R_2, \ldots, R_n) \in \mathbb{R}_{> 0}^n$$

where $R_j > 0$ is the total available quantity of resource $j$. Finiteness is guaranteed by the thermodynamic axiom: localized, usable (low-entropy) energy is bounded in any finite spatial region.

### 1.3 The Identity Preservation Objective

Each agent $i$ possesses a **utility function** (Identity Preservation objective):

$$U_i : \mathbb{R}_{\geq 0}^n \to \mathbb{R}$$

representing the net thermodynamic benefit of strategy $\mathbf{x}_i$. Formally, $U_i(\mathbf{x}_i)$ is the energy harvested by agent $i$ minus the metabolic cost of harvesting. We impose the following standard regularity conditions:

> **Assumption 1 (Regularity).** For each agent $i$:
> 
> (a) $U_i$ is twice continuously differentiable ($C^2$) on $\mathbb{R}_{\geq 0}^n$.
> 
> (b) $U_i$ is strictly concave in $\mathbf{x}_i$: $\nabla^2_{\mathbf{x}_i} U_i \prec 0$ (negative definite Hessian).
> 
> (c) $U_i$ is monotonically increasing at the origin: $\nabla_{\mathbf{x}_i} U_i(\mathbf{0}) \succ \mathbf{0}$ (each resource has positive marginal value when the agent has nothing).
>
> (d) $U_i(\mathbf{x}_i) \to -\infty$ as $\|\mathbf{x}_i\| \to \infty$ (coercivity).

**Physical motivation:** Condition (b) reflects diminishing returns — processing increasing quantities of any single resource incurs escalating metabolic costs (diminishing thermodynamic returns; see §III, Assumption 1). Condition (c) ensures that a zero-resource state is never optimal for a living entity — an agent with no resources cannot maintain its boundary and ceases to exist. Condition (d) guarantees that the unconstrained optimum exists at a finite point: sufficiently extreme consumption eventually incurs net thermodynamic harm (toxicity, metabolic overload, storage costs), so utility cannot grow without bound.

A concrete functional form satisfying all conditions is the **quadratic energy model**:

$$U_i(\mathbf{x}_i) = \sum_{j=1}^{n} \left( \alpha_{ij} \, x_{ij} - \frac{\beta_{ij}}{2} \, x_{ij}^2 \right)$$

where $\alpha_{ij} > 0$ is the marginal energy yield of resource $j$ to agent $i$ and $\beta_{ij} > 0$ governs the diminishing-returns rate. More general concave forms (CES, Cobb-Douglas) work identically for the structural results below.

---

## 2. The Unconstrained Problem (No Rights — The State of Nature)

### 2.1 Formulation

If no other agents exist — or, equivalently, if no mutual constraints (rights) are recognized — each agent solves independently:

$$\max_{\mathbf{x}_i \geq \mathbf{0}} \; U_i(\mathbf{x}_i)$$

Under Assumption 1, this has a unique interior solution at:

$$\nabla_{\mathbf{x}_i} U_i(\mathbf{x}_i^{\circ}) = \mathbf{0}$$

For the quadratic model:

$$x_{ij}^{\circ} = \frac{\alpha_{ij}}{\beta_{ij}} \quad \forall j$$

This is the agent's **unconstrained optimum** — the strategy it would pursue if it were alone in the universe.

### 2.2 The Collision Condition

When $N \geq 2$ agents share the environment, the physically realizable joint strategy must satisfy the **resource conservation constraint** (scarcity):

$$\sum_{i=1}^{N} x_{ij} \leq R_j \quad \forall j \in \{1, \ldots, n\}$$

**Definition 1 (Resource Collision).** A resource dimension $j$ is in *collision* if the sum of unconstrained optima exceeds supply:

$$\sum_{i=1}^{N} x_{ij}^{\circ} > R_j$$

**Lemma 1 (Inevitability of Collision).** *Given a finite resource endowment $\mathbf{R}$ shared by $N \geq 2$ agents with overlapping resource needs, collision is guaranteed whenever $N$ is sufficiently large. Specifically, for any resource $j$ essential to all agents, collision occurs whenever $N \geq N_j^* := \lfloor R_j / \min_i x_{ij}^{\circ} \rfloor + 1$.*

*Proof.* By Assumption 1(b)–(d), each agent $i$ has a unique finite unconstrained optimum with $x_{ij}^{\circ} > 0$ for every essential resource $j$. Let $\delta_j := \min_{i} x_{ij}^{\circ} > 0$. Then for any $N$ agents sharing resource $j$:

$$\sum_{i=1}^{N} x_{ij}^{\circ} \geq N \cdot \delta_j$$

Setting $N \cdot \delta_j > R_j$ gives $N > R_j / \delta_j$, so $N \geq \lfloor R_j / \delta_j \rfloor + 1 =: N_j^*$ suffices. For $N \geq N_j^*$, the aggregate unconstrained demand exceeds supply and resource $j$ is in collision by Definition 1. In any biologically realistic scenario — where per-capita endowment $R_j / N$ is small relative to individual metabolic requirements $x_{ij}^{\circ}$ — this bound is satisfied for many or all resource dimensions. $\square$

### 2.3 The State of Nature as Unbounded Competition

When collision occurs and no constraints exist, each agent pursues $\mathbf{x}_i^{\circ}$ regardless of the physical feasibility of the aggregate. The result is **simultaneous attempted over-extraction**: multiple agents' strategies claim the same physical resource units.

Since two agents cannot exclusively consume the same unit of energy (the exclusion principle on resource-action vectors; see §IV), the collision is resolved by **conflict** — the direct expenditure of stored energy to contest the resource. This generates the interaction costs (thermodynamic friction) quantified in the thermodynamic friction derivation.

The unconstrained case thus corresponds precisely to the Hobbesian "State of Nature": a high-entropy, high-friction regime where every agent's strategy is a potential threat to every other agent's boundary.

---

## 3. The Constrained Problem (Rights as Boundary Conditions)

### 3.1 Defining a Right Mathematically

We now introduce the central construction.

> **Definition 2 (Right).** A *right* $\mathcal{R}_{B,k}$ of agent $B$ is a constraint of the form
> 
> $$g_{Bk}(\mathbf{x}_A) \leq 0 \qquad (k = 1, \ldots, m_B)$$
> 
> imposed on every other agent $A \neq B$'s optimization problem, where $g_{Bk} : \mathbb{R}_{\geq 0}^n \to \mathbb{R}$ is a continuously differentiable, convex function encoding a specific aspect of agent $B$'s protected boundary, satisfying $g_{Bk}(\mathbf{0}) < 0$ (the zero-action strategy violates no agent's rights).

**Scope note.** The condition $g_{Bk}(\mathbf{0}) < 0$ restricts Definition 2 to *negative rights* — duties of non-interference ("do not take $B$'s resources," "do not cross $B$'s boundary"). *Positive rights* — duties of provision ("supply $B$ with at least $\tau_B$ units") — have the opposite sign structure: $g_{Bk}(\mathbf{0}) = \tau_B > 0$, so inaction itself constitutes a violation. The present framework derives negative rights as the first-order consequence of resource collision under $A_1$; positive rights arise as stability conditions on an already-established cooperative equilibrium (see §VIII, Future Work).

**Interpretation:** The function $g_{Bk}$ defines a **forbidden region** in agent $A$'s action space. If $g_{Bk}(\mathbf{x}_A) > 0$, then strategy $\mathbf{x}_A$ violates agent $B$'s $k$-th right. The constraint $g_{Bk}(\mathbf{x}_A) \leq 0$ forces agent $A$ to remain outside $B$'s protected domain.

**Examples of constraint functions:**

| Right (plain language) | Constraint function $g_{Bk}(\mathbf{x}_A) \leq 0$ | Meaning |
|---|---|---|
| B has a guaranteed minimum share $\bar{x}_{Bj}$ of resource $j$ | $g_{Bk}(\mathbf{x}_A) = x_{Aj} - (R_j - \bar{x}_{Bj})$ | A cannot take more than $R_j - \bar{x}_{Bj}$ of resource $j$ |
| B's total resource intake cannot be reduced below threshold $\tau_B$ | $g_{Bk}(\mathbf{x}_A) = \sum_j x_{Aj} - (|\mathbf{R}| - \tau_B)$, where $|\mathbf{R}| = \sum_j R_j$ | A's total consumption is bounded |
| B's spatial boundary $\Omega_B$ is inviolable | $g_{Bk}(\mathbf{x}_A) = \mathbb{1}[\mathbf{x}_A \cap \Omega_B \neq \emptyset]$ | A's action vector cannot penetrate B's physical/informational boundary |

> **Note.** The spatial boundary example uses an indicator function for conceptual clarity. Since $\mathbb{1}[\cdot]$ is neither continuously differentiable nor convex, in practice it is replaced by a smooth convex approximation (e.g., a distance-based penalty for convex $\Omega_B$) satisfying Definition 2's regularity requirements.

The framework is deliberately general: **any** restriction on one agent's strategy that protects another agent's domain is a right. This includes property rights, bodily autonomy, informational privacy, and territorial sovereignty — all encoded as inequality constraints.

### 3.2 The Constrained Optimization Problem

With rights in place, agent $A$'s optimization problem becomes:

$$\max_{\mathbf{x}_A \geq \mathbf{0}} \; U_A(\mathbf{x}_A) \qquad \text{subject to:}$$

$$\text{(i) Resource scarcity:} \quad x_{Aj} + \hat{x}_{-Aj} \leq R_j \quad \forall j \qquad [\lambda_j \geq 0]$$

$$\text{(ii) Rights of other agents:} \quad g_{Bk}(\mathbf{x}_A) \leq 0 \quad \forall B \neq A, \; k = 1, \ldots, m_B \qquad [\mu_{Bk} \geq 0]$$

where $\hat{x}_{-Aj} = \sum_{i \neq A} x_{ij}$ is the aggregate consumption of resource $j$ by all other agents (taken as given from $A$'s perspective), and $\lambda_j$, $\mu_{Bk}$ are the associated Lagrange multipliers.

### 3.3 The Lagrangian

Assembling the Lagrangian for agent $A$:

$$\mathcal{L}_A(\mathbf{x}_A, \boldsymbol{\lambda}, \boldsymbol{\mu}) = U_A(\mathbf{x}_A) - \sum_{j=1}^{n} \lambda_j \left( x_{Aj} + \hat{x}_{-Aj} - R_j \right) - \sum_{B \neq A} \sum_{k=1}^{m_B} \mu_{Bk} \, g_{Bk}(\mathbf{x}_A)$$

where $\boldsymbol{\lambda} = (\lambda_1, \ldots, \lambda_n)$ and $\boldsymbol{\mu} = \{\mu_{Bk}\}_{B \neq A, \, k}$.

---

## 4. The Karush-Kuhn-Tucker (KKT) Conditions

### 4.1 First-Order Necessary Conditions

Under Assumption 1 and standard constraint qualification (Slater's condition holds: $g_{Bk}(\mathbf{0}) < 0$ for all $B, k$ by Definition 2, and continuity then gives $g_{Bk}(\epsilon\mathbf{1}/n) < 0$ for sufficiently small $\epsilon > 0$, providing a strictly feasible interior point), the KKT conditions are both necessary and sufficient for optimality (concave objective, convex constraints; see [@Boyd2004, §5.5.3]). At the optimum $\mathbf{x}_A^*$:

**(i) Stationarity:**

$$\frac{\partial U_A}{\partial x_{Aj}}\bigg|_{\mathbf{x}_A^*} = \lambda_j + \sum_{B \neq A} \sum_{k=1}^{m_B} \mu_{Bk} \frac{\partial g_{Bk}}{\partial x_{Aj}}\bigg|_{\mathbf{x}_A^*} \qquad \forall j$$

**(ii) Primal feasibility:**

$$x_{Aj}^* + \hat{x}_{-Aj} \leq R_j \qquad \forall j$$
$$g_{Bk}(\mathbf{x}_A^*) \leq 0 \qquad \forall B \neq A, \; \forall k$$

**(iii) Dual feasibility:**

$$\lambda_j \geq 0 \quad \forall j, \qquad \mu_{Bk} \geq 0 \quad \forall B, k$$

**(iv) Complementary slackness:**

$$\lambda_j \left( x_{Aj}^* + \hat{x}_{-Aj} - R_j \right) = 0 \qquad \forall j$$
$$\mu_{Bk} \, g_{Bk}(\mathbf{x}_A^*) = 0 \qquad \forall B, k$$

### 4.2 Interpretation of the Stationarity Condition

The stationarity condition (i) has a precise physical reading:

$$\underbrace{\frac{\partial U_A}{\partial x_{Aj}}}_{\substack{\text{Marginal energy} \\ \text{gain from resource } j}} = \underbrace{\lambda_j}_{\substack{\text{Shadow price of} \\ \text{resource scarcity}}} + \underbrace{\sum_{B,k} \mu_{Bk} \frac{\partial g_{Bk}}{\partial x_{Aj}}}_{\substack{\text{Aggregate cost of} \\ \text{other agents' rights}}}$$

**At the optimum, the marginal benefit of consuming one more unit of resource $j$ exactly equals the marginal cost — decomposed into two components: the scarcity cost (the resource is finite) and the rights cost (other agents' boundaries restrict access).**

This is the mathematical formalization of the framework's core assertion: *"Every right granted to agent $A$ acts as an equal and opposite restriction on the freedom of agent $B$."*

---

## 5. The Shadow Price of a Right

### 5.1 The Lagrange Multiplier as the Cost of a Right

> **Theorem 1 (Rights as Optimization Constraints — The Shadow Price Theorem).**
> 
> *Let $\mathbf{x}_A^*(\boldsymbol{c})$ denote agent $A$'s optimal strategy as a function of the constraint parameters $\boldsymbol{c} = \{c_{Bk}\}$, where the $k$-th right of agent $B$ is parameterized as $g_{Bk}(\mathbf{x}_A) \leq c_{Bk}$. Then the optimal value function $U_A^*(\boldsymbol{c}) = U_A(\mathbf{x}_A^*(\boldsymbol{c}))$ satisfies:*
> 
> $$\frac{\partial U_A^*}{\partial c_{Bk}} = \mu_{Bk}^* \geq 0$$
> 
> *where $\mu_{Bk}^*$ is the optimal Lagrange multiplier associated with agent $B$'s $k$-th right. That is, the multiplier $\mu_{Bk}^*$ measures the marginal increase in agent $A$'s optimal energy intake per unit relaxation of agent $B$'s $k$-th boundary constraint.*

*Proof.* This is a direct application of the shadow price interpretation of Lagrange multipliers [see @Boyd2004, §5.6.3]. Under Assumption 1 and constraint qualification, the optimal value function is differentiable in the constraint parameters, and the derivative equals the associated multiplier. $\square$

### 5.2 Physical Interpretation

**Corollary 1.1.** *Every right has a non-negative cost. A right that is not active (not binding at the optimum) has zero cost. A right that is active (binding) has strictly positive cost.*

This follows directly from complementary slackness and dual feasibility:

- If $g_{Bk}(\mathbf{x}_A^*) < 0$ (the constraint is slack — $A$ is not pressing against $B$'s boundary), then $\mu_{Bk}^* = 0$. The right exists but imposes no cost because $A$'s unconstrained optimum already respects it.
- If $g_{Bk}(\mathbf{x}_A^*) = 0$ (the constraint is active — $A$ is at $B$'s boundary), then $\mu_{Bk}^* > 0$. The right actively restricts $A$'s strategy and has a quantifiable energetic cost.

**Corollary 1.2 (Newton's Third Law Analog).** *For every right $\mathcal{R}_{B,k}$ that actively constrains agent $A$, there exists a strictly positive shadow price $\mu_{Bk}^* > 0$ representing the energetic restriction imposed on $A$. The right is simultaneously a protection for $B$ and a cost for $A$: action and reaction are mathematically coupled through the shared constraint.*

### 5.3 The "Price" of a Right in the Quadratic Model

For the quadratic energy model with a single resource and the constraint $g_B(x_A) = x_A - (R - \bar{x}_B) \leq 0$ (agent $B$ is guaranteed at least $\bar{x}_B$):

The Lagrangian:

$$\mathcal{L}(x_A, \mu) = \alpha_A x_A - \frac{\beta_A}{2} x_A^2 - \mu\bigl(x_A - (R - \bar{x}_B)\bigr)$$

KKT stationarity:

$$\alpha_A - \beta_A x_A - \mu = 0$$

**Case 1: Constraint not binding** ($x_A^{\circ} = \alpha_A / \beta_A \leq R - \bar{x}_B$).

Agent $A$'s unconstrained optimum already respects $B$'s right. Then $\mu^* = 0$ and $x_A^* = \alpha_A / \beta_A$. The right exists but costs $A$ nothing.

**Case 2: Constraint binding** ($\alpha_A / \beta_A > R - \bar{x}_B$).

Agent $A$ would prefer more than is allowed. The constraint forces $x_A^* = R - \bar{x}_B$ and:

$$\mu^* = \alpha_A - \beta_A(R - \bar{x}_B) > 0$$

The shadow price $\mu^*$ is the marginal energy that $A$ forfeits because of $B$'s right. This is:

- **Increasing** in $\alpha_A$ (the more $A$ values the resource, the costlier the constraint).
- **Decreasing** in $\beta_A$ (the faster $A$'s returns diminish, the less it cares about the cap).
- **Increasing** in $\bar{x}_B$ (the more $B$ is guaranteed, the more $A$ must forfeit).
- **Decreasing** in $R$ (the more total resource exists, the less binding the constraint).

These are physically intuitive: rights are costlier when entities are more capable, more "hungry," and when resources are scarcer.

---

## 6. Theorem 2: The Impossibility of Unconstrained Coexistence

> **Theorem 2 (Impossibility of Infinite Freedom).**
> 
> *Let $N \geq 2$ agents share a finite resource endowment $\mathbf{R}$. Suppose each agent has at least one essential resource (a resource $j$ for which $\partial U_i / \partial x_{ij} |_{\mathbf{x}_i = \mathbf{0}} > 0$) in common with at least one other agent, and that aggregate unconstrained demand exceeds supply for at least one resource ($\sum_i x_{ij}^{\circ} > R_j$ for some $j$). Then no feasible strategy profile $(\mathbf{x}_1, \ldots, \mathbf{x}_N)$ can simultaneously be unconstrained-optimal for all agents. Formally:*
> 
> $$\nexists \; (\mathbf{x}_1, \ldots, \mathbf{x}_N) \in \mathcal{F} \; \text{ such that } \; \mathbf{x}_i = \mathbf{x}_i^{\circ} \;\; \forall i$$
> 
> *where $\mathcal{F} = \{(\mathbf{x}_1, \ldots, \mathbf{x}_N) : \sum_i x_{ij} \leq R_j \; \forall j, \; \mathbf{x}_i \geq \mathbf{0} \; \forall i\}$ is the feasible set and $\mathbf{x}_i^{\circ}$ is agent $i$'s unconstrained optimum.*

*Proof.* Let $j^*$ be a resource dimension that is essential for agents $A$ and $B$ (at minimum). By Assumption 1(c) and strict concavity, both agents have strictly positive unconstrained optima: $x_{Aj^*}^{\circ} > 0$ and $x_{Bj^*}^{\circ} > 0$.

Consider the aggregate unconstrained demand:

$$\sum_{i=1}^{N} x_{ij^*}^{\circ} \geq x_{Aj^*}^{\circ} + x_{Bj^*}^{\circ}$$

For the claim to fail — i.e., for all agents to achieve their unconstrained optima simultaneously — we would need:

$$\sum_{i=1}^{N} x_{ij^*}^{\circ} \leq R_{j^*}$$

But as $N$ grows or as agents' capacities increase relative to $R_{j^*}$, this inequality is violated. More precisely, for any fixed $R_{j^*}$ and any collection of agents each requiring $x_{ij^*}^{\circ} > 0$, there exists a finite $N^*$ such that $\sum_{i=1}^{N^*} x_{ij^*}^{\circ} > R_{j^*}$.

In any biologically relevant system (multiple organisms sharing finite local resources), the collision condition $\sum_i x_{ij}^{\circ} > R_j$ is satisfied for at least one $j$, making the simultaneous unconstrained-optimal profile infeasible. $\square$

**Corollary 2.1.** *In any multi-agent system with resource collision, at least one rights constraint must be active ($\mu_{Bk}^* > 0$ for some $B, k$) at any feasible solution. Rights are not optional — they are mathematically necessary for coexistence.*

**Physical interpretation:** This is the formal proof of the framework's assertion: *"Infinite freedom is mathematically impossible in a shared environment. An entity can only have unrestricted vectors if it is the only entity in the universe."*

---

## 7. The Multi-Agent Coupled System: Generalized Nash Equilibrium

### 7.1 Formulation

When all $N$ agents optimize simultaneously, each taking the others' strategies into account, the system is a **Generalized Nash Equilibrium Problem (GNEP)**. Each agent $i$ solves:

$$\max_{\mathbf{x}_i \geq \mathbf{0}} \; U_i(\mathbf{x}_i) \qquad \text{s.t.} \quad \sum_{l=1}^{N} x_{lj} \leq R_j \;\; \forall j, \quad g_{Bk}(\mathbf{x}_i) \leq 0 \;\; \forall B \neq i, \; k$$

The feasible set for each agent depends on the other agents' strategies (through the shared resource constraints). This is what makes the problem a *generalized* Nash problem, not a standard one.

### 7.2 Solution Concept: Variational Equilibrium

A **Variational Equilibrium** (VE), also called a Normalized Nash Equilibrium [@Rosen1965], is a strategy profile $(\mathbf{x}_1^*, \ldots, \mathbf{x}_N^*)$ such that:

1. Each agent $i$'s strategy $\mathbf{x}_i^*$ is optimal given the others' strategies, and
2. All agents share the **same** Lagrange multipliers $\boldsymbol{\lambda}^* = (\lambda_1^*, \ldots, \lambda_n^*)$ for the shared resource constraints.

> **Theorem 3 (Existence and Structure of the Cooperative Equilibrium).**
> 
> *Under Assumption 1 (regularity), the GNEP possesses a Variational Equilibrium $(\mathbf{x}_1^*, \ldots, \mathbf{x}_N^*, \boldsymbol{\lambda}^*)$. At this equilibrium:*
> 
> *(a) The shared shadow prices $\lambda_j^*$ are identical for all agents — every agent faces the same "price" for each scarce resource.*
> 
> *(b) The stationarity condition for each agent $i$ reads:*
> 
> $$\frac{\partial U_i}{\partial x_{ij}}\bigg|_{\mathbf{x}_i^*} = \lambda_j^* + \sum_{B \neq i, k} \mu_{Bk}^{(i)} \frac{\partial g_{Bk}}{\partial x_{ij}}\bigg|_{\mathbf{x}_i^*} \qquad \forall j$$
> 
> *(c) No agent can improve its utility by unilaterally deviating from $\mathbf{x}_i^*$, given the constraints.*

*Proof.* The shared resource constraints $0 \leq x_{ij} \leq R_j$ give each agent a compact, convex feasible set, each $U_i$ is concave by Assumption 1, and the joint constraint set is convex. These are the hypotheses of [@Rosen1965, Theorem 3], which guarantees that a Normalized Nash Equilibrium exists for every weight vector $r > 0$. The shared-multiplier property is the defining feature of the VE solution concept. $\square$

### 7.3 Interpretation: Equality Before the Constraints

**Corollary 3.1 (Symmetry of Scarcity).** *At the variational equilibrium, all agents experience the same marginal cost $\lambda_j^*$ per unit of each shared resource. No agent is privileged in the mathematical structure of the shared constraints.*

This is a mathematical analog of **equality before the law**: the scarcity constraint imposes a uniform cost structure on all agents. Individual differences arise only through differences in utility functions $U_i$ (different agents value resources differently) and through the specific rights constraints $g_{Bk}$ (different agents have different protected domains).

### 7.4 The "Mutual Constraint" Structure

At the variational equilibrium, the full system of KKT conditions across all agents forms a coupled system:

$$\frac{\partial U_i}{\partial x_{ij}} = \lambda_j^* + \sum_{B \neq i, k} \mu_{Bk}^{(i)} \frac{\partial g_{Bk}}{\partial x_{ij}} \qquad \forall i, j$$

$$\sum_{i=1}^{N} x_{ij}^* \leq R_j, \quad \lambda_j^* \geq 0, \quad \lambda_j^*\left(\sum_i x_{ij}^* - R_j\right) = 0 \qquad \forall j$$

$$g_{Bk}(\mathbf{x}_i^*) \leq 0, \quad \mu_{Bk}^{(i)} \geq 0, \quad \mu_{Bk}^{(i)} g_{Bk}(\mathbf{x}_i^*) = 0 \qquad \forall i, B \neq i, k$$

This coupled system is the **mathematical object** that corresponds to a "social contract" in philosophical language: a self-consistent set of mutual constraints that no agent can improve upon unilaterally. The system of mutual rights is not imposed from outside — it emerges as the necessary structure of any stable multi-agent coexistence under scarcity.

---

## 8. Worked Example: Two Agents, One Divisible Resource

### 8.1 Setup

Let $N = 2$, $n = 1$ (agents $A$ and $B$, one resource of total quantity $R$). The quadratic utility functions are:

$$U_A(x_A) = \alpha_A x_A - \frac{\beta_A}{2} x_A^2, \qquad U_B(x_B) = \alpha_B x_B - \frac{\beta_B}{2} x_B^2$$

where $x_B = R - x_A$ (by resource conservation, taking the constraint as binding for simplicity — the interesting case).

### 8.2 Unconstrained Optima

$$x_A^{\circ} = \frac{\alpha_A}{\beta_A}, \qquad x_B^{\circ} = \frac{\alpha_B}{\beta_B}$$

**Collision condition:** $x_A^{\circ} + x_B^{\circ} > R$, i.e., $\frac{\alpha_A}{\beta_A} + \frac{\alpha_B}{\beta_B} > R$.

### 8.3 With Rights: Agent $B$ Has a Guaranteed Minimum $\bar{x}_B$

Agent $A$ maximizes $U_A(x_A)$ subject to $x_A \leq R - \bar{x}_B$.

**Lagrangian:**

$$\mathcal{L}(x_A, \mu) = \alpha_A x_A - \frac{\beta_A}{2} x_A^2 - \mu\left(x_A - R + \bar{x}_B\right)$$

**KKT conditions:**

$$\alpha_A - \beta_A x_A^* - \mu^* = 0$$
$$\mu^* \geq 0, \quad x_A^* \leq R - \bar{x}_B, \quad \mu^*(x_A^* - R + \bar{x}_B) = 0$$

**Solution:**

If $\frac{\alpha_A}{\beta_A} \leq R - \bar{x}_B$ (constraint not binding):
$$x_A^* = \frac{\alpha_A}{\beta_A}, \qquad \mu^* = 0$$

If $\frac{\alpha_A}{\beta_A} > R - \bar{x}_B$ (constraint binding):
$$x_A^* = R - \bar{x}_B, \qquad \mu^* = \alpha_A - \beta_A(R - \bar{x}_B)$$

### 8.4 Numerical Illustration

Let $\alpha_A = 10$, $\beta_A = 1$, $\alpha_B = 8$, $\beta_B = 1$, $R = 12$, $\bar{x}_B = 5$.

- Unconstrained optima: $x_A^{\circ} = 10$, $x_B^{\circ} = 8$. Collision: $10 + 8 = 18 > 12$.
- With $B$'s right: $A$ can take at most $R - \bar{x}_B = 7$.
- Since $x_A^{\circ} = 10 > 7$, the constraint binds: $x_A^* = 7$, $\mu^* = 10 - 1 \cdot 7 = 3$.
- **The cost of $B$'s right to $A$:** Agent $A$ loses $\mu^* = 3$ units of marginal energy due to $B$'s guaranteed share.
- Agent $A$'s constrained utility: $U_A(7) = 10(7) - \frac{1}{2}(49) = 70 - 24.5 = 45.5$.
- Agent $A$'s unconstrained utility: $U_A(10) = 10(10) - \frac{1}{2}(100) = 100 - 50 = 50$.
- **Total cost to $A$:** $50 - 45.5 = 4.5$ energy units.

### 8.5 Social Welfare Comparison

**With rights ($\bar{x}_B = 5$):**

- $U_A(7) = 45.5$, $U_B(5) = 8(5) - \frac{1}{2}(25) = 27.5$.
- **Total system utility:** $45.5 + 27.5 = 73.0$.

**Without rights (collision → conflict, modeled as equal split $x_A = x_B = 6$):**

- $U_A(6) = 10(6) - \frac{1}{2}(36) = 42$, $U_B(6) = 8(6) - \frac{1}{2}(36) = 30$.
- **Total system utility:** $42 + 30 = 72.0$.

**Without rights (A takes all, unconstrained):**

- $U_A(10) = 50$, $U_B(2) = 8(2) - \frac{1}{2}(4) = 14$.
- **Total system utility:** $50 + 14 = 64.0$.

The rights-constrained allocation achieves the highest total system utility. The unconstrained "greedy" solution is the worst for the system. This is a preview of the Nash Equilibrium result developed in the game-theory derivation.

> **Remark (Why the gap is small here).** The welfare difference between the VE allocation (73.0) and the naive equal split (72.0) is only ~1.4%. This is a *mathematical artifact of near-symmetric agents*: when $\beta_A = \beta_B$, the VE allocation $x_i^* = (\alpha_i - \lambda^*)/\beta$ differs from equal split only through the $\alpha_i$ differences. With $\alpha_A = 10$ and $\alpha_B = 8$ (a 20% gap), the heterogeneity is small and equal split is nearly optimal. In general, the welfare gain from optimally differentiated allocation scales with agent heterogeneity. The following asymmetric example demonstrates this.

### 8.6 Asymmetric Example: Heterogeneous Metabolic Efficiency

In biological systems, agents rarely have identical metabolic profiles. Consider two agents with the **same marginal yield** ($\alpha$) but **different diminishing-returns rates** ($\beta$) — e.g., Agent $A$ is an efficient large-scale processor (forests, apex predators, industrial economies) while Agent $B$ saturates quickly (specialized microorganisms, artisanal producers).

**Parameters:** $\alpha_A = 10$, $\beta_A = 0.5$ (slow diminishing returns); $\alpha_B = 10$, $\beta_B = 2$ (fast diminishing returns); $R = 12$.

**Unconstrained optima:** $x_A^{\circ} = 20$, $x_B^{\circ} = 5$. Collision: $25 > 12$.

**Variational Equilibrium:**

$$\lambda^* = \frac{x_A^{\circ} + x_B^{\circ} - R}{1/\beta_A + 1/\beta_B} = \frac{20 + 5 - 12}{2 + 0.5} = \frac{13}{2.5} = 5.2$$

$$x_A^* = \frac{10 - 5.2}{0.5} = 9.6, \qquad x_B^* = \frac{10 - 5.2}{2} = 2.4$$

The VE allocates **four times more** to the efficient processor — not because $A$ is "more important," but because $A$ extracts more marginal value from each additional unit.

**Social welfare comparison:**

| Allocation | $x_A$ | $x_B$ | $U_A$ | $U_B$ | **Total SW** |
|---|---|---|---|---|---|
| **VE (optimal rights)** | 9.6 | 2.4 | 72.96 | 18.24 | **91.20** |
| **Greedy ($A$ takes all)** | 12 | 0 | 84.00 | 0.00 | 84.00 |
| **Equal split** | 6 | 6 | 51.00 | 24.00 | 75.00 |

The VE now outperforms equal split by **21.6%** and the greedy allocation by **8.6%**. The equal-split regime is particularly wasteful: it forces 6 units onto Agent $B$, whose fast-saturating metabolism means each unit beyond ~2.4 costs more to process than it yields. Biologically, this is analogous to force-feeding an organism past its metabolic optimum — raw resource ≠ usable energy.

**Key insight:** The framework does not merely prove that *some* constraint system beats anarchy. It proves that the *mathematically optimal* constraint system (the VE) allocates resources according to each agent's capacity to convert them into useful work — and this allocation can dramatically outperform naive "fairness" (equal split) precisely when agents are diverse.

### 8.7 Symmetric Example: Same-Species Competition and the Scarcity Gradient

The most common biological scenario is conspecific competition: agents of the **same species** sharing the **same environment** ($\alpha_A = \alpha_B = \alpha$, $\beta_A = \beta_B = \beta$). Here the framework reveals a different but equally important result.

**Parameters:** $\alpha = 10$, $\beta = 1$; resource $R$ varies.

**Unconstrained optima:** $x_A^{\circ} = x_B^{\circ} = 10$. **Collision** occurs whenever $R < 20$.

**VE for symmetric agents:** By symmetry of the KKT system, the variational equilibrium assigns each agent exactly half:

$$x_A^* = x_B^* = \frac{R}{2}, \qquad \lambda^* = \alpha - \beta \cdot \frac{R}{2}$$

**Fairness is not assumed — it is derived.** The equal split emerges as a mathematical theorem from the structure of identical utility functions and shared scarcity constraints. No external notion of "justice" is required.

**The cost of defection:** If one agent defects (seizes its unconstrained optimum $x_A = 10$, leaving the other with $R - 10$), the total system welfare drops. The magnitude of this loss scales with scarcity:

| $R$ | Scarcity | VE: $x_i^*$ | VE: $U_i$ | VE: SW | Defect: $(x_A, x_B)$ | Defect: SW | **VE Advantage** |
|---|---|---|---|---|---|---|---|
| 20 | None | 10.0 | 50.0 | 100.0 | (10, 10) | 100.0 | 0% |
| 16 | Mild | 8.0 | 48.0 | 96.0 | (10, 6) | 92.0 | **4.3%** |
| 14 | Moderate | 7.0 | 45.5 | 91.0 | (10, 4) | 82.0 | **11.0%** |
| 12 | Scarce | 6.0 | 42.0 | 84.0 | (10, 2) | 68.0 | **23.5%** |
| 10 | Severe | 5.0 | 37.5 | 75.0 | (10, 0) | 50.0 | **50.0%** |

Three results emerge from this table:

1. **Under abundance ($R \geq 20$), rights have zero cost** — both agents achieve their unconstrained optima, all multipliers are zero, and the constraint system is slack. Rights exist in principle but impose no restriction. This is the mathematical counterpart of the observation that ethical conflicts rarely arise when resources are plentiful.

2. **As scarcity increases, the cost of defection grows super-linearly.** Moving from mild to severe scarcity, the VE advantage jumps from 4% to 50%. This is because the defector's gain (moving from $R/2$ to 10) is bounded by the concavity of $U$, while the victim's loss (moving from $R/2$ to $R - 10$) accelerates as it approaches zero — the region where each lost unit is maximally valuable.

3. **Under severe scarcity ($R = 10$), defection eliminates the other agent entirely** ($x_B = 0 \implies U_B = 0$). The defector captures $U_A = 50$, but the system loses $U_B = 37.5$ — a net destruction of 25 units of welfare. This is the mathematical signature of Thermodynamic Friction (§IV.5): unrestricted competition in scarce environments doesn't redistribute value, it *dissipates* it.

> **Corollary 3.2 (Rights as Scarcity Insurance).** *The value of a rights constraint system is monotonically increasing in scarcity. Under abundance, rights are costless and unnecessary. Under scarcity, rights become the dominant determinant of system welfare. This explains why ethical systems universally intensify during resource crises — it is not cultural convention but mathematical necessity.*

---

## 9. The Transition to Conflict: Removing the Constraint ($\mu = 0$ Everywhere)

### 9.1 Statement

> **Proposition 1 (Unconstrained Regime Implies Conflict).**
> 
> *If all rights constraints are removed ($g_{Bk}$ dropped for all $B, k$), and the system is in collision ($\sum_i x_{ij}^{\circ} > R_j$ for some $j$), then:*
> 
> *(a) No stable allocation exists without an enforcement mechanism.*
> 
> *(b) Each agent's attempt to realize its unconstrained optimum generates a negative externality on other agents.*
> 
> *(c) The resulting contested resource must be resolved by direct energy expenditure (conflict), creating the interaction cost function quantified in the thermodynamic friction derivation.*

*Proof of (a).* Without constraints, each agent $i$ attempts $\mathbf{x}_i^{\circ}$. The aggregate $\sum_i \mathbf{x}_i^{\circ} > \mathbf{R}$ is physically infeasible. Since no constraint directs agents to reduce consumption, and each agent's unilateral best response is $\mathbf{x}_i^{\circ}$ regardless of the others' (by strict concavity, the optimal response function without constraints is constant), there is no self-correcting mechanism. The unconstrained Nash equilibrium is infeasible — it requires $\sum_i \mathbf{x}_i^{\circ} > \mathbf{R}$. Any feasible allocation requires at least one agent to accept less than its optimum, which it has no incentive to do without a constraint. $\square$

*Proof of (b).* When $A$ claims $x_{Aj}^{\circ}$, the remaining resource for all other agents is $R_j - x_{Aj}^{\circ}$. In the collision regime, $R_j - x_{Aj}^{\circ} < \sum_{i \neq A} x_{ij}^{\circ}$, meaning $A$'s strategy forces at least one other agent below its optimum. This is the definition of a negative externality. $\square$

**Remark.** Part (c) connects directly to the thermodynamic friction derivation. When the mathematical constraint is absent, the physical reality of resource exclusion (two agents cannot consume the same molecule) is enforced not by agreement but by energy expenditure — combat, theft, or defense. The constraint $g_{Bk}(\mathbf{x}_A) \leq 0$ is the mathematical mechanism that replaces costly physical enforcement with costless (zero-friction) boundary recognition.

---

## 10. Summary of Results

| # | Result | Statement | Significance |
|---|---|---|---|
| **T1** | Shadow Price Theorem | $\partial U_A^* / \partial c_{Bk} = \mu_{Bk}^* \geq 0$ | Every right has a quantifiable energetic cost to the constrained agent |
| **C1.1** | Active vs. Inactive Rights | Binding constraints have $\mu > 0$; slack constraints have $\mu = 0$ | Rights cost nothing when not contested; cost emerges only at points of conflict |
| **C1.2** | Newton's Third Law Analog | Each right is simultaneously a protection and a cost | Action-reaction structure of mutual constraints |
| **L1** | Inevitability of Collision | Collision guaranteed for $N \geq N_j^*$ agents sharing finite resources | Scarcity makes constraint necessity quantitative, not merely qualitative |
| **T2** | Impossibility of Infinite Freedom | No feasible profile achieves all agents' unconstrained optima simultaneously | Rights are mathematically necessary, not optional |
| **C2.1** | Necessity of Active Constraints | At least one $\mu_{Bk}^* > 0$ at any feasible solution | Some agent is always constrained |
| **T3** | Variational Equilibrium | GNEP has a solution with shared shadow prices | "Equality before the law" emerges from the mathematical structure |
| **C3.1** | Symmetry of Scarcity | All agents face the same $\lambda_j^*$ per shared resource | Uniform cost structure; individual differences arise only through $U_i$ and $g_{Bk}$ |
| **C3.2** | Rights as Scarcity Insurance | Value of rights monotonically increasing in scarcity | Ethical intensification during crises is mathematical necessity |
| **P1** | Unconstrained → Conflict | Removing constraints in collision regime produces no stable allocation | The State of Nature is mathematically unstable; links to thermodynamic friction |

---

## 11. Notation Index

| Symbol | Meaning |
|---|---|
| $N$ | Number of agents |
| $n$ | Number of resource dimensions |
| $\mathbf{x}_i \in \mathbb{R}_{\geq 0}^n$ | Agent $i$'s strategy (resource-allocation) vector |
| $R_j$ | Total available quantity of resource $j$ |
| $U_i(\mathbf{x}_i)$ | Agent $i$'s utility (Identity Preservation objective) |
| $\alpha_{ij}, \beta_{ij}$ | Marginal yield and diminishing-returns parameters (quadratic model) |
| $\mathbf{x}_i^{\circ}$ | Agent $i$'s unconstrained optimum |
| $g_{Bk}(\mathbf{x}_A)$ | Constraint function encoding agent $B$'s $k$-th right |
| $\lambda_j$ | Lagrange multiplier for resource $j$ scarcity |
| $\mu_{Bk}$ | Lagrange multiplier (shadow price) for agent $B$'s $k$-th right |
| $\hat{x}_{-Aj}$ | Aggregate consumption of resource $j$ by all agents other than $A$ |
| $\mathcal{L}_A$ | Lagrangian for agent $A$'s constrained optimization |
| $\mathcal{F}$ | Feasible strategy set under resource and rights constraints |

> **Symbol disambiguation.** The symbol $R_j$ in this file denotes total resource quantity. In other derivation files, $r$ denotes coupling distance (value dynamics), contest decisiveness (thermodynamic friction), and time-preference rate (game theory). Context and subscripts distinguish these uses.
