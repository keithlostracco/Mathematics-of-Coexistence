# IV. Rights as Optimization Constraints

<!-- Sources: supplementary/A-mathematical-derivations/lagrangian-constraints.md,
             supplementary/A-mathematical-derivations/thermodynamic-friction.md,
             supplementary/A-mathematical-derivations/information-negentropy.md -->

This section derives the first major result chain: rights are mathematically necessary constraints on multi-agent optimization (§4.1–§4.3), violating them generates quantifiable energy waste (§4.4–§4.5), and even subtle violations through deception inject measurable entropy with cumulative network effects (§4.6–§4.7).

---

## 4.1 The Finite Board: Scarcity as Mathematical Precondition

By Axiom $A_0$ and the finiteness of localized low-entropy energy, the environment's resource endowment $\mathbf{R} = (R_1, \ldots, R_n)$ is bounded. By Axiom $A_1$, each of the $N \geq 2$ agents is driven to maximize its utility $U_i(\mathbf{x}_i)$ — the net thermodynamic benefit of its resource-allocation strategy $\mathbf{x}_i \in \mathbb{R}_{\geq 0}^n$.

If no other agents exist — or equivalently, if no mutual constraints are recognized — each agent independently solves the unconstrained problem:

$$\max_{\mathbf{x}_i \geq \mathbf{0}} \; U_i(\mathbf{x}_i)$$

Under Assumption 1 (§III), each agent has a unique unconstrained optimum $\mathbf{x}_i^{\circ}$ with $x_{ij}^{\circ} > 0$ for every resource it can metabolize. By Lemma 1 (Inevitability of Collision), for any $N \geq N_j^*$ — where $N_j^*$ is the collision threshold for resource $j$ — the aggregate unconstrained demand exceeds supply: $\sum_i x_{ij}^{\circ} > R_j$ for at least one resource $j$.

The physically realizable joint strategy must satisfy the resource conservation (scarcity) constraint:

$$\sum_{i=1}^{N} x_{ij} \leq R_j \qquad \forall j$$

Two agents cannot exclusively consume the same unit of energy, nor occupy the same resource-state simultaneously. This exclusion principle on resource-action vectors — structurally analogous to exclusion constraints in physics — is the mathematical origin of constraint necessity.

---

## 4.2 Rights as Lagrangian Constraints

### Definition

> **Definition 2 (Right).** A *right* $\mathcal{R}_{B,k}$ of agent $B$ is an inequality constraint
>
> $$g_{Bk}(\mathbf{x}_A) \leq 0 \qquad (k = 1, \ldots, m_B)$$
>
> imposed on every other agent $A \neq B$'s optimization problem, where $g_{Bk} : \mathbb{R}_{\geq 0}^n \to \mathbb{R}$ is a continuously differentiable, convex function encoding a specific aspect of agent $B$'s protected boundary, satisfying $g_{Bk}(\mathbf{0}) < 0$ (the zero-action strategy violates no agent's rights).

**Notation.** The symbol $\mathcal{R}$ is used in three distinct contexts throughout the paper: $\mathcal{R}_{B,k}$ (subscripted) denotes agent $B$'s $k$-th right (this section); $\mathcal{R}_{\text{BL}}$ denotes the Burning-Library Ratio (§V); and $\mathcal{R}(\mathbf{x}_A)$ (with argument) denotes the composite reward function (§VII). The subscript or argument structure disambiguates all uses.

The constraint $g_{Bk}(\mathbf{x}_A) \leq 0$ defines a forbidden region in agent $A$'s strategy space. If $g_{Bk}(\mathbf{x}_A) > 0$, then strategy $\mathbf{x}_A$ violates agent $B$'s $k$-th right. The condition $g_{Bk}(\mathbf{0}) < 0$ restricts Definition 2 to *negative rights* — duties of non-interference. Positive rights (duties of provision, where inaction itself constitutes a violation) have the opposite sign structure and arise as stability conditions on cooperative equilibria rather than as first-order collision constraints; see §VIII for discussion. Subject to this scope, the framework is deliberately general: any restriction on one agent's strategy that protects another agent's domain qualifies — property rights, bodily autonomy, informational privacy, territorial sovereignty, and minimum resource guarantees are all encoded as inequality constraints.

**Examples:**

| Right (plain language) | Constraint $g_{Bk}(\mathbf{x}_A) \leq 0$ |
|---|---|
| $B$ is guaranteed minimum share $\bar{x}_{Bj}$ of resource $j$ | $x_{Aj} - (R_j - \bar{x}_{Bj}) \leq 0$ |
| $B$'s total resource intake cannot be reduced below threshold $\tau_B$ | $\sum_j x_{Aj} - (\lvert\mathbf{R}\rvert - \tau_B) \leq 0$ |
| $B$'s spatial/informational boundary $\Omega_B$ is inviolable | $\mathbb{1}[\mathbf{x}_A \in \Omega_B] \leq 0$ |

**Note on the indicator-function example.** The third row uses the indicator $\mathbb{1}[\mathbf{x}_A \in \Omega_B]$, which is neither continuously differentiable nor convex and therefore does not satisfy Definition 2's regularity requirements or the KKT conditions. It is included *for intuition only* — to convey that a boundary can be encoded as a zero-one membership condition. The formal treatment replaces such indicator constraints with smooth convex approximations (e.g., a distance-based penalty for convex $\Omega_B$) that recover the sharp boundary in the limit $\epsilon \to 0$ while preserving differentiability and convexity throughout the interior of the feasible set.

### The Constrained Optimization Problem

With rights in place, each agent $A$ solves:

$$\max_{\mathbf{x}_A \geq \mathbf{0}} \; U_A(\mathbf{x}_A) \quad \text{s.t.} \quad \begin{cases} x_{Aj} + \hat{x}_{-Aj} \leq R_j & \forall j \quad [\lambda_j \geq 0] \\ g_{Bk}(\mathbf{x}_A) \leq 0 & \forall B \neq A, \; k \quad [\mu_{Bk} \geq 0] \end{cases}$$

where $\hat{x}_{-Aj} = \sum_{i \neq A} x_{ij}$ is aggregate consumption by other agents, and $\lambda_j$, $\mu_{Bk}$ are the associated Lagrange multipliers. The Lagrangian:

$$\mathcal{L}_A = U_A(\mathbf{x}_A) - \sum_j \lambda_j(x_{Aj} + \hat{x}_{-Aj} - R_j) - \sum_{B \neq A} \sum_k \mu_{Bk} \, g_{Bk}(\mathbf{x}_A)$$

Under Assumption 1 and Slater's constraint qualification ($g_{Bk}(\mathbf{0}) < 0$ by Definition 2 provides a strictly feasible point), the KKT conditions are necessary and sufficient for optimality (concave objective, convex constraints by Definition 2; see [@Boyd2004, Ch. 5.5.3]).

### The Stationarity Condition: What Rights Cost

The KKT stationarity condition at the optimum $\mathbf{x}_A^*$ reads:

$$\underbrace{\frac{\partial U_A}{\partial x_{Aj}}\bigg|_{\mathbf{x}_A^*}}_{\substack{\text{Marginal energy} \\ \text{gain from resource } j}} = \underbrace{\lambda_j}_{\substack{\text{Shadow price of} \\ \text{resource scarcity}}} + \underbrace{\sum_{B,k} \mu_{Bk} \frac{\partial g_{Bk}}{\partial x_{Aj}}\bigg|_{\mathbf{x}_A^*}}_{\substack{\text{Aggregate cost of} \\ \text{other agents' rights}}} \qquad \forall j$$

At the optimum, the marginal benefit of consuming one more unit of resource $j$ exactly equals the marginal cost — decomposed into the scarcity cost (the resource is finite) and the rights cost (other agents' boundaries restrict access). This is the formal demonstration that every active right granted to one agent acts as a measurable restriction on every other agent.

---

## 4.3 The Shadow Price Theorem and the Impossibility of Infinite Freedom

> **Theorem 1 (Shadow Price Theorem).** *The optimal Lagrange multiplier $\mu_{Bk}^*$ associated with agent $B$'s $k$-th right satisfies:*
>
> $$\frac{\partial U_A^*}{\partial c_{Bk}} = \mu_{Bk}^* \geq 0$$
>
> *where $c_{Bk}$ parameterizes the constraint as $g_{Bk}(\mathbf{x}_A) \leq c_{Bk}$. That is, $\mu_{Bk}^*$ measures the marginal increase in agent $A$'s optimal utility per unit relaxation of agent $B$'s boundary constraint. Every right has a quantifiable energetic cost.*

**Corollary 1.1.** A right that is not active (not binding at the optimum) has zero cost ($\mu_{Bk}^* = 0$). A right that is active (binding) has strictly positive cost ($\mu_{Bk}^* > 0$). Rights cost nothing when they are not contested; the cost emerges only at points of conflict.

**Corollary 1.2 (Newton's Third Law Analog).** For every right $\mathcal{R}_{B,k}$ that actively constrains agent $A$, there exists a strictly positive shadow price $\mu_{Bk}^* > 0$ representing the energetic restriction imposed on $A$. The right is simultaneously a protection for $B$ and a cost for $A$: action and reaction are mathematically coupled through the shared constraint.

This result formalizes a central claim of the framework: every active right granted to one agent acts as a corresponding restriction on the freedom of others. The shadow price $\mu_{Bk}^*$ quantifies the cost to the constrained agent, though the magnitude of that cost need not equal the benefit to the right-holder.

> **Theorem 2 (Impossibility of Infinite Freedom).** *Let $N \geq 2$ agents share a finite resource endowment $\mathbf{R}$. Suppose each agent has at least one essential resource in common with at least one other agent, and that $N$ meets the collision threshold $N_j^*$ for at least one resource $j$ (Lemma 1). Then no feasible strategy profile can simultaneously be unconstrained-optimal for all agents:*
>
> $$\nexists \; (\mathbf{x}_1, \ldots, \mathbf{x}_N) \in \mathcal{F} \;\text{such that}\; \mathbf{x}_i = \mathbf{x}_i^{\circ} \;\; \forall i$$
>
> *where $\mathcal{F}$ is the feasible set under resource constraints.*

*Proof.* For $N \geq N_{j^*}^*$, the collision condition (Lemma 1) guarantees $\sum_i x_{ij^*}^{\circ} > R_{j^*}$ for some $j^*$. The profile $(\mathbf{x}_1^{\circ}, \ldots, \mathbf{x}_N^{\circ})$ therefore violates the scarcity constraint and lies outside $\mathcal{F}$. $\square$

**Corollary 2.1.** In any multi-agent system with resource collision, at least one rights constraint must be active ($\mu_{Bk}^* > 0$) at any feasible solution. Rights are not optional — they are mathematically necessary for coexistence.

Infinite freedom is *mathematically impossible* in a shared environment. An agent can have unrestricted strategy vectors only if it is the sole agent in the environment. The finiteness of localized free energy ensures that infinite freedom for all agents in a network is infeasible.

---

## 4.4 The Cooperative Equilibrium: Variational Equilibrium of the GNEP

When all $N$ agents optimize simultaneously, the system is a **Generalized Nash Equilibrium Problem (GNEP)** — a Nash game in which each agent's feasible set depends on the other agents' strategies through the shared resource constraints. The appropriate solution concept is:

> **Theorem 3 (Variational Equilibrium).** *Under Assumption 1, the GNEP possesses a Variational Equilibrium (VE) $(\mathbf{x}_1^*, \ldots, \mathbf{x}_N^*, \boldsymbol{\lambda}^*)$ satisfying:*
>
> *(a) All agents share the same shadow prices $\lambda_j^*$ for the shared resource constraints — every agent faces the same "price" for each scarce resource.*
>
> *(b) No agent can improve its utility by unilaterally deviating, given the constraints.*

*Proof.* The shared resource constraints $0 \leq x_{ij} \leq R_j$ ensure each agent's feasible set is compact (closed and bounded), satisfying the compactness hypothesis of Rosen (1965) Theorem 3. Existence follows from [@Rosen1965, Theorem 3]: under concavity of each $U_i$ and convexity of the shared constraint set, a Normalized Nash Equilibrium exists for every specified weight vector $r > 0$. $\square$

**Corollary 3.1 (Symmetry of Scarcity).** At the variational equilibrium, all agents experience the same marginal cost $\lambda_j^*$ per unit of shared resource. No agent is privileged in the mathematical structure of the scarcity constraints.

This is a mathematical analog of *equality before the law*: the scarcity constraint imposes a uniform cost structure. Individual differences arise only through differences in utility functions (agents value resources differently) and through specific rights constraints (agents have different protected domains).

> **Proposition 1 (Unconstrained Regime Implies Conflict).** *If all rights constraints are removed and the system is in collision, then (a) no stable allocation exists without an enforcement mechanism, (b) each agent's attempt to realize its unconstrained optimum generates a negative externality on other agents, and (c) the contested resources must be resolved by direct energy expenditure — conflict.*

This proposition establishes the precise sense in which the Hobbesian "state of nature" is mathematically unstable: without mutual constraints, no equilibrium exists, and the system defaults to the costly conflict dynamics quantified below.

---

## 4.5 The Energy Cost of Constraint Violation: Thermodynamic Friction

Proposition 1 establishes that removing constraints leads to conflict. We now quantify the energetic cost of that conflict — and prove that it is self-defeating.

### The Boundary Breach Model

When an agent violates another's boundary (the mathematical constraint), the violation requires physical work. The breach cost is determined by the defender's boundary integrity:

> **Definition 4 (Boundary Resistance).** The work required to breach agent $i$'s boundary to depth $d \in [0,1]$ is:
>
> $$W_{\text{breach}}(d) = \int_0^d F_i(s) \, ds = B_i \int_0^d f(s) \, ds$$
>
> where $F_i(s) = B_i \cdot f(s)$ is the resistance force and $f: [0,1] \to \mathbb{R}_{>0}$ is a normalized resistance profile with $\int_0^1 f(s) \, ds = 1$. Full breach costs $W_{\text{breach}}(1) = B_i$.

### The Contest Model

When two agents claim the same resource and no constraint directs either to yield, the resource is contested. We model this as a Tullock contest [@Tullock1980]:

> **Proposition 2 (Symmetric Contest Equilibrium).** *In a symmetric two-agent Tullock contest over resource $E_j > 0$, the Nash equilibrium contest investment per agent is $e^* = E_j/4$, and the total dissipation is:*
>
> $$D_2 = 2e^* = \frac{E_j}{2}$$
>
> *Half the resource's value is consumed by the act of fighting.*

This 50% dissipation rate is the minimum — the waste under idealized conditions with equal contestants and no collateral damage.

### The Friction Multiplier

In reality, conflict imposes costs beyond the direct contest investment: offensive exposure, defensive damage, and repair costs. The total cost is captured by the friction multiplier:

> **Definitions 6–7 (Conflict Damage and Repair).** The offensive and defensive damage fractions $\delta^{\text{off}}, \delta^{\text{def}} \in [0,1]$ (Definition 6) and the repair cost multiplier $\kappa \geq 1$ (Definition 7) together determine the **friction multiplier** for a contested interaction:
>
> $$\Phi = 1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})$$
>
> Rebuilding costs $\kappa$ times the damage; see Appendix A for the full boundary-damage model.

Under physically realistic parameters ($\kappa = 2$, $\delta^{\text{off}} + \delta^{\text{def}} = 0.4$), the friction multiplier exceeds 2.

> **Theorem 4 (Dissipation Scaling).** *In an $N$-player symmetric contest:*
>
> $$D_N = \frac{(N-1)}{N} E_j \xrightarrow{N \to \infty} E_j$$
>
> *Contest waste approaches 100% of the resource value as the number of competitors grows.*

The friction multiplier $\Phi > 2$ triggers:

> **Theorem 5 (Net-Negative Conflict).** *The adversarial contest is system-net-negative whenever $\Phi > N/(N-1)$:*
>
> $$V_{\text{net}} = E_j\left(1 - \Phi \cdot \frac{N-1}{N}\right) < 0$$
>
> *The total energy dissipated by the conflict exceeds the value of the contested resource.*

**Corollary 5.1 (Inevitability).** For $\Phi > 1$ (any non-trivial friction), the net-negative condition is satisfied for all $N \geq N^*$. In physical systems with non-trivial friction, $N^*$ is typically small.

Theorems 4–5 establish that **conflict is not merely suboptimal — it is self-destructive**: the combatants collectively dissipate more energy than the prize they are fighting over. This is the thermodynamic basis for the subsequent proof (§V) that cooperation strictly dominates defection.

> **Theorem 6 (Cooperation Dominance).** *The social welfare under cooperation exceeds that under conflict by at least:*
>
> $$SW_{\text{coop}} - SW_{\text{conflict}} \geq \Phi \cdot \frac{N-1}{N} \cdot E_j$$

*Proof.* Under cooperation, all agents operate within legitimate constraints and no energy is dissipated in boundary conflict; thus $SW_{\text{coop}} \geq E_j$ (no energy is dissipated in conflict). Under conflict, Theorem 5 gives $SW_{\text{conflict}} = E_j(1 - \Phi(N-1)/N)$. Subtracting: $SW_{\text{coop}} - SW_{\text{conflict}} \geq E_j - E_j(1 - \Phi(N-1)/N) = \Phi \cdot (N-1)/N \cdot E_j$. $\square$

### Cascading Friction: Network Amplification

A single boundary violation does not affect only the two parties involved. In a cooperative network, every agent's payoff depends on the aggregate trust level:

> **Definition 9 (Friction Injection).** A violation of severity $v$ injects friction:
>
> $$\Delta\phi = \eta \cdot v$$
>
> into the network friction coefficient $\phi$, where $\eta$ is the friction sensitivity parameter.

> **Theorem 7 (Cascading Friction).** *A single violation of severity $v$ imposes a network-wide cost:*
>
> $$C_{\text{cascade}} = \frac{\eta \cdot v \cdot M \cdot \bar{E}}{\epsilon}$$
>
> *where $M$ is the number of cooperative transactions per period, $\bar{E}$ is the average transaction value, and $\epsilon$ is the trust recovery rate.*

Under realistic parameters, the cascading amplification ratio ($\eta M \bar{E}/\epsilon$) reaches $10^3$ to $10^4$ — a single violation costs the network thousands of times the direct damage. This is the formal counterpart of the observable phenomenon where a single act of bad faith (a corporate scandal, a treaty violation, a trust breach) degrades an entire institution's functioning far beyond the immediate damage.

**Corollary 7.1 (Friction Ratchet).** If the rate of violations exceeds a critical threshold $\nu^*$, the friction coefficient $\phi$ diverges and the cooperative network disintegrates entirely.

---

## 4.6 Micro-Friction: The Information-Theoretic Cost of Deception

The preceding analysis addresses *macro-friction* — overt boundary violations (theft, assault, war). We now extend the framework to *micro-friction*: subtle violations that corrupt the informational channel between agents without physically breaching boundaries.

### Deception as Entropy Injection

Agents rely on information from their environment and from other agents to compute optimal strategies. When one agent deliberately corrupts the information available to another, the victim acts on false premises, selects a suboptimal strategy, and suffers an energetic loss.

> **Definition 13 (Honest Communication).** A transmission is honest if $Y$ is a sufficient statistic for $\Theta$: $H(\Theta|Y) = 0$, equivalently $I(\Theta; Y) = H(\Theta)$.

> **Definition 14 (Deception).** Agent $A$ deceives Agent $B$ by transmitting a signal $Y$ through a channel $p(Y|\Theta)$ such that $H(\Theta|Y) > 0$ when $A$ could have transmitted honestly ($H(\Theta|Y) = 0$ is achievable). The injected entropy is:
>
> $$\Delta H = H(\Theta|Y) \geq 0$$

We model the deceptive channel as a binary symmetric channel (BSC) with deception rate $q \in [0, 0.5]$ — the probability that any given communication is strategically false. The binary entropy function $h(q) = -q\log_2 q - (1-q)\log_2(1-q)$ quantifies the channel noise.

### The Decision Cost of Deception

> **Theorem 8 (Decision Cost of Deception).** *In the binary-state quadratic decision model, when Agent $B$ receives a signal with deception rate $q > 0$, the expected utility loss relative to honest communication is:*
>
> $$\Delta U_B(q) = \frac{q(1-q)(\alpha_H - \alpha_L)^2}{2\beta}$$
>
> *where $\alpha_H$ and $\alpha_L$ are the high and low marginal resource yields and $\beta$ is the diminishing-returns rate. The cost scales with $q(1-q)$, with the square of the signal's decision-relevance $(\alpha_H - \alpha_L)^2$, and inversely with $\beta$.*

Deception does not merely reduce information quality; it causes the victim to make *actively harmful* decisions — allocating resources to the wrong uses, trusting the wrong partners, preparing for the wrong threats.

### The Verification Cost

> **Theorem 9 (Metabolic Verification Cost).** *The energy overhead required to verify a signal with deception rate $q$ is:*
>
> $$\Delta W(q) = W_{\text{honest}} \cdot \frac{h(q)}{1 - h(q)}$$
>
> *This cost is eventually convex in $q$: because $h(q)$ is concave near the origin, $\Delta W(q)$ is itself concave for small $q$ and has an inflection point near $q \approx 0.04$, above which it becomes convex in $q$. The cost diverges as $q \to 0.5$ (pure noise). At $q = 0.05$, verification overhead is approximately 40%. At $q = 0.25$, it exceeds 430%.*

**Corollary 9.1 (Inevitability of Deception Cost).** For any deception rate $q > 0$, $\min(\Delta U_B, \Delta W) > 0$. No costless deception exists: the receiver either suffers decision loss or pays verification overhead (or both).

---

## 4.7 Systemic Deception and Network Collapse

Individual acts of deception are locally damaging, but the more consequential finding concerns the *cumulative* effect of deception across a network.

### The Deception-Friction Mapping

> **Definition 17 (Deception-Friction Mapping).** The friction injected by a deceptive transmission is:
>
> $$\Delta\phi = \eta_{\text{info}} \cdot \Delta H \cdot W_{\text{bit}}$$
>
> where $\eta_{\text{info}}$ is the information-friction sensitivity and $W_{\text{bit}}$ is the metabolic cost per bit of deceptive signal processed.

This mapping unifies macro-friction (physical boundary violations, §4.5) and micro-friction (information corruption) into a single network friction framework. Both increase the system's ambient "heat" — the energy wasted on defense, verification, and suboptimal decisions rather than productive cooperation.

### The Network Collapse Theorem

> **Theorem 10 (Cumulative Micro-Friction — The Systemic Deception Theorem).** *A network of $N$ agents with $M$ cooperative transactions per period and average deception rate $\bar{q} > 0$ suffers a total per-period efficiency loss of:*
>
> $$\mathcal{L}_{\text{deception}} = \underbrace{M \cdot \Delta U_{\text{avg}}(\bar{q})}_{\text{decision losses}} + \underbrace{M \cdot W_{\text{honest}} \cdot \frac{h(\bar{q})}{1 - h(\bar{q})}}_{\text{verification costs}}$$
>
> *where $\Delta U_{\text{avg}}(\bar{q})$ is the average per-transaction decision loss (Theorem 8 averaged over all transaction types). The total cost: (a) is zero if and only if $\bar{q} = 0$ (perfect honesty); (b) grows super-linearly with $\bar{q}$ due to the $h(\bar{q})/(1 - h(\bar{q}))$ divergence; and (c) exceeds the network's cooperative surplus $E_{\text{coop net}}$ at a critical deception rate $\bar{q}^*$, beyond which cooperation becomes energetically unprofitable.*

Small, persistent lies are catastrophic. The verification-cost term diverges as $\bar{q} \to 0.5$: a network in which half of all communications are unreliable cannot sustain cooperation at any level. Even well below this physical limit, a modest network-average deception rate drives the total overhead past the cooperative surplus, triggering collapse.

> **Corollary 10.1 (Honesty Efficiency Principle).** *Honesty is mathematically defined as the communication regime that maximizes network efficiency. Any deviation from honest communication ($\bar{q} > 0$) imposes a strictly positive, compounding cost on the network. The zero-deception point is a unique global optimum:*
>
> $$\phi_{\text{honest}} = 0 \iff \bar{q} = 0 \iff \text{network operates at maximum cooperative efficiency}$$

The honesty result is unconditional: it holds for any network topology, any number of agents, and any depth of decision pipeline. It is the information-theoretic analog of the zero-friction condition in mechanics — the state in which no energy is wasted on overhead.

---

## 4.8 Summary of Section IV

The results of this section form a complete logical chain:

1. **Scarcity creates collision** (Lemma 1): multiple agents' unconstrained demands exceed supply.

2. **Rights are necessary** (Theorem 2): no allocation satisfying all agents' optima exists; mutual constraints are required.

3. **Rights have quantifiable cost** (Theorem 1): every active constraint has a shadow price measuring its energetic impact.

4. **A cooperative equilibrium exists** (Theorem 3): the GNEP possesses a variational equilibrium with uniform shadow prices.

5. **Removing rights triggers conflict** (Proposition 1): the unconstrained regime is unstable.

6. **Conflict is self-destructive** (Theorem 5): the energy dissipated by conflict exceeds the value of the contested resource.

7. **Conflict waste scales with network size** (Theorem 4): approaching 100% dissipation as competitors increase.

8. **Cooperation strictly dominates conflict** (Theorem 6): the cooperative surplus exceeds the conflict outcome by at least the total friction loss.

9. **Single violations cascade** (Theorem 7): network amplification at ratios of $10^3$–$10^4$.

10. **Deception is measurably costly** (Theorems 8–9): even "small" lies degrade decisions and impose verification overhead.

11. **Systemic dishonesty collapses the network** (Theorem 10): a critical deception rate $\bar{q}^*$ drives total overhead past the cooperative surplus.

12. **Honesty is optimal** (Corollary 10.1): zero deception is the unique efficiency-maximizing communication regime.

These results show that any rational agent operating in a shared, finite-resource environment has strong mathematical reasons to respect rights constraints and communicate honestly. What remains to be shown is that these individual incentives aggregate into a *system-level equilibrium* — that cooperation is not merely individually rational but collectively stable. This is the subject of §V.
