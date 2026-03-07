# Thermodynamic Friction — The Energy Cost of Conflict

---

## 0. Preamble

This document contains the formal mathematical derivation for the thermodynamic friction framework. Building directly on the Lagrangian constraints derivation, which proved that removing rights constraints leads to resource collision and conflict (Proposition 1), we now **quantify the energetic cost** of that conflict.

The contribution is **applied mathematics**: we use contest theory [@Tullock1980], boundary-integrity models, and network cost analysis to prove that unconstrained conflict is a net-negative thermodynamic outcome — dissipating more energy than the contested resource is worth.

**Key references for the tools used:**

- [@Tullock1980], *Efficient Rent Seeking*, in *Toward a Theory of the Rent-Seeking Society* — contest functions and rent dissipation.
- [@Skaperdas1996], "Contest Success Functions," *Economic Theory* — axiomatization of contest models.
- [@Hirshleifer1991], "The Technology of Conflict as an Economic Activity," *American Economic Review* — conflict technology and wasteful competition.
- [@GarfinkelSkaperdas2012], *The Oxford Handbook of the Economics of Peace and Conflict* — comprehensive treatment.

**Notational continuity from the Lagrangian constraints derivation:**

- $N$ agents, $n$ resource dimensions, strategy vectors $\mathbf{x}_i \in \mathbb{R}_{\geq 0}^n$.
- Utility functions $U_i(\mathbf{x}_i)$ satisfying Assumption 1 (regularity, strict concavity, positive origin gradient, coercivity).
- Resource endowment $\mathbf{R}$; collision condition $\sum_i x_{ij}^{\circ} > R_j$.
- Unconstrained optima $\mathbf{x}_i^{\circ}$; constrained optima $\mathbf{x}_i^*$.

---

## 1. From Collision to Conflict: The Resolution Mechanism

### 1.1 Recap: From Rights to Friction

The Lagrangian constraints derivation (Proposition 1) established that when rights constraints are absent and resource collision occurs, no stable allocation exists — each agent pursues its unconstrained optimum $\mathbf{x}_i^{\circ}$, and the aggregate demand $\sum_i \mathbf{x}_i^{\circ} > \mathbf{R}$ is physically infeasible. We noted that the collision must be resolved by "direct energy expenditure (conflict)."

This document formalizes that energy expenditure. We answer three questions:

1. **How much energy does conflict cost each agent?** (Sections 2–4)
2. **When does the total system cost exceed the resource value?** (Section 5)
3. **How does conflict cascade through the network?** (Section 7)

### 1.2 The Physical Mechanism

When two agents claim the same resource unit and no constraint directs either to yield, the resource is **contested**. Contest resolution requires energy expenditure by both parties — the attacker expends energy to breach the defender's boundary; the defender expends energy to resist. This expenditure is **pure waste** from the system's perspective: it does not create new resources, does not enhance either agent's productive capacity, and cannot be recovered. It is dissipated as heat (entropy), in exact analogy with mechanical friction converting kinetic energy to thermal energy.

---

## 2. The Boundary Integrity Model

### 2.1 Boundary as an Energetic Structure

Each agent $i$ maintains a **boundary** (Markov blanket in statistical physics; cell membrane in biology; legal/military defense in sociology) characterized by its **integrity**:

> **Definition 3 (Boundary Integrity).** Agent $i$'s boundary integrity is a scalar $B_i > 0$ measured in energy units, representing the total energetic investment in maintaining the boundary between the agent's internal low-entropy state and the external environment.

**Physical interpretation:** $B_i$ is the stored energy in the agent's defensive infrastructure — the immune system, the cell wall, the military budget, the information-security apparatus. A higher $B_i$ means a more robust boundary that is costlier to breach.

### 2.2 Boundary Maintenance Cost

Maintaining boundary integrity against environmental entropy requires continuous work:

$$C_{\text{maintain},i} = \gamma_i \cdot B_i$$

where $\gamma_i > 0$ is the **entropy leakage rate** — the rate at which the boundary degrades without active maintenance. This is the baseline metabolic cost of "being alive" (maintaining identity), independent of any external threat.

### 2.3 Boundary Resistance Function

When an external agent attempts to breach agent $i$'s boundary, the boundary exerts a **resistance** that the attacker must overcome. We model this as a force-displacement relationship:

> **Definition 4 (Boundary Resistance).** The work required to breach agent $i$'s boundary to depth $d \in [0, 1]$ (where $d = 0$ is the exterior and $d = 1$ is full breach) is:
> 
> $$W_{\text{breach}}(d) = \int_0^d F_i(s) \, ds$$
> 
> where $F_i(s) = B_i \cdot f(s)$ is the resistance force and $f : [0, 1] \to \mathbb{R}_{> 0}$ is a normalized resistance profile with $\int_0^1 f(s) \, ds = 1$.

The full breach cost is:

$$W_{\text{breach}}(1) = B_i \cdot \int_0^1 f(s) \, ds = B_i$$

That is, fully breaching agent $i$'s boundary requires work equal to the boundary's integrity — an energetically intuitive result.

**Resistance profile choices:**

| Profile | $f(s)$ | Physical meaning |
|---|---|---|
| Uniform | $f(s) = 1$ | Constant resistance (simple barrier) |
| Hardening | $f(s) = 2s$ | Resistance increases with depth (layered defense) |
| Shell | $f(s) = 2(1 - s)$ | Hard exterior, soft interior (biological cell) |

The qualitative results below hold for any positive, integrable $f$. The specific profile affects only the dynamics of partial breach, not the total cost.

---

## 3. The Contest Model: Conflict as Resource Competition

### 3.1 Setup

Consider a single contested resource of value $E_j > 0$ (energy units) that is in collision (Definition 1). Two agents $A$ and $B$ both claim this resource. In the absence of a rights constraint directing the allocation, the resource is resolved by a **contest**: each agent invests energy to increase its probability of winning.

> **Definition 5 (Conflict Contest).** A conflict contest over resource $E_j$ between agents $A$ and $B$ is characterized by:
> 
> (a) **Contest investments** $e_A, e_B \geq 0$: the energy each agent diverts from productive use into conflict.
> 
> (b) **Contest success function** $p_A(e_A, e_B) \in [0, 1]$: the probability that agent $A$ wins (secures) the resource, with $p_B = 1 - p_A$.
> 
> (c) **Payoffs:**
> $$\Pi_A(e_A, e_B) = p_A(e_A, e_B) \cdot E_j - e_A$$
> $$\Pi_B(e_A, e_B) = (1 - p_A(e_A, e_B)) \cdot E_j - e_B$$

### 3.2 The Tullock Contest Success Function

We adopt the axiomatically grounded **Tullock contest success function** [@Skaperdas1996]:

$$p_A(e_A, e_B) = \frac{\sigma_A \, e_A^r}{\sigma_A \, e_A^r + \sigma_B \, e_B^r}$$

where:

- $\sigma_i > 0$ is agent $i$'s **conflict effectiveness** (strength, weaponry, information advantage)
- $r > 0$ is the **decisiveness parameter**: $r < 1$ means the contest is noisy (randomness dominates); $r = 1$ is the baseline lottery; $r > 1$ means the contest is decisive (larger investment almost certainly wins)

For $e_A = e_B = 0$, we define $p_A = \sigma_A / (\sigma_A + \sigma_B)$ by convention.

**Axiomatization [@Skaperdas1996]:** This is the unique contest success function satisfying:
(i) Homogeneity of degree zero in $(e_A, e_B)$ up to scaling;
(ii) Monotonicity ($\partial p_A / \partial e_A > 0$, $\partial p_A / \partial e_B < 0$);
(iii) Independence from irrelevant alternatives.

### 3.3 Nash Equilibrium of the Contest

Each agent chooses its contest investment to maximize its payoff, taking the other's investment as given.

**Case 1: Symmetric Agents ($\sigma_A = \sigma_B = 1$, $r = 1$)**

Agent $A$'s first-order condition:

$$\frac{\partial \Pi_A}{\partial e_A} = \frac{e_B}{(e_A + e_B)^2} \cdot E_j - 1 = 0$$

By symmetry, $e_A^* = e_B^*$. Substituting:

$$\frac{e_A^*}{(2 e_A^*)^2} \cdot E_j = 1 \implies e_A^* = \frac{E_j}{4}$$

> **Proposition 2 (Symmetric Contest Equilibrium).** *In a symmetric Tullock contest ($\sigma_A = \sigma_B$, $r = 1$) over resource $E_j$, the unique Nash equilibrium contest investments are:*
> 
> $$e_A^* = e_B^* = \frac{E_j}{4}$$
> 
> *Total contest dissipation:*
> 
> $$D_2 = e_A^* + e_B^* = \frac{E_j}{2}$$
> 
> *Each agent's expected payoff:*
> 
> $$\Pi_A^* = \Pi_B^* = \frac{E_j}{2} - \frac{E_j}{4} = \frac{E_j}{4}$$

**Interpretation:** Half the resource value is consumed by the act of fighting. Each agent expects to net only one quarter of the resource value — compared to the cooperative outcome (splitting the resource, per the Lagrangian constraints derivation) where each receives half with zero contest expenditure.

**Case 2: Asymmetric Agents ($V_A \neq V_B$, $r = 1$)**

For the general case with potentially different valuations $V_A$ and $V_B$ (how much each agent values the resource — we set $V_A = V_B = E_j$ for a common-value contest, but keep it general for the derivation):

First-order conditions:

$$\frac{e_B}{(e_A + e_B)^2} \cdot V_A = 1, \qquad \frac{e_A}{(e_A + e_B)^2} \cdot V_B = 1$$

Dividing: $\frac{e_B}{e_A} = \frac{V_B}{V_A}$, so $e_B = \frac{V_B}{V_A} e_A$.

Substituting back into $A$'s FOC:

$$\frac{V_B e_A / V_A}{e_A^2 (1 + V_B/V_A)^2} \cdot V_A = 1$$

$$e_A^* = \frac{V_A^2 V_B}{(V_A + V_B)^2}, \qquad e_B^* = \frac{V_A V_B^2}{(V_A + V_B)^2}$$

> **Proposition 3 (Asymmetric Contest Equilibrium).** *In a Tullock contest ($r = 1$) with valuations $V_A, V_B > 0$:*
> 
> $$e_A^* = \frac{V_A^2 V_B}{(V_A + V_B)^2}, \qquad e_B^* = \frac{V_A V_B^2}{(V_A + V_B)^2}$$
> 
> *Total dissipation:*
> 
> $$D_2 = e_A^* + e_B^* = \frac{V_A V_B}{V_A + V_B}$$
> 
> *This is the harmonic semi-mean of the valuations. For $V_A = V_B = E_j$: $D_2 = E_j/2$.*

**Note:** The total dissipation $D_2 = V_A V_B / (V_A + V_B)$ is maximized when $V_A = V_B$ (equal opponents waste the most). When one agent values the resource much more ($V_A \gg V_B$), the weaker agent invests very little and the contest is "cheap" — but the outcome is effectively determined by power asymmetry, which corresponds to exploitative resource extraction.

### 3.4 N-Agent Contest: Scaling to Populations

When $N \geq 2$ symmetric agents ($\sigma_i = 1$, $V_i = E_j$, $r = 1$) contest the same resource:

By symmetry, each invests $e^*$ and wins with probability $1/N$. Agent $i$'s FOC:

$$\frac{(N-1) e^*}{N^2 (e^*)^2} \cdot E_j = 1 \implies e^* = \frac{(N-1)}{N^2} \cdot E_j$$

> **Theorem 4 (Dissipation Scaling — The Tragedy of Contest).** *In a symmetric $N$-agent Tullock contest ($r = 1$) over resource $E_j$:*
> 
> *(a) Each agent's equilibrium investment:*
> 
> $$e_i^* = \frac{N - 1}{N^2} \cdot E_j$$
> 
> *(b) Total contest dissipation:*
> 
> $$D_N = N \cdot e_i^* = \frac{N - 1}{N} \cdot E_j$$
> 
> *(c) Each agent's expected payoff:*
> 
> $$\Pi_i^* = \frac{E_j}{N} - \frac{(N-1) E_j}{N^2} = \frac{E_j}{N^2}$$
> 
> *(d) Dissipation ratio:*
> 
> $$\frac{D_N}{E_j} = \frac{N - 1}{N} = 1 - \frac{1}{N}$$

*Proof.* Part (a): With $N$ symmetric agents, agent $i$'s success probability is:

$$p_i = \frac{e_i}{e_i + \sum_{k \neq i} e_k}$$

At a symmetric equilibrium ($e_k = e^*$ for all $k$), $p_i = 1/N$. The FOC is:

$$\frac{\partial \Pi_i}{\partial e_i} = \frac{(N-1) e^*}{(N e^*)^2} \cdot E_j - 1 = 0$$

Solving: $e^* = (N-1) E_j / N^2$. Parts (b)–(d) follow by direct computation. $\square$

**Corollary 4.1 (Vanishing Individual Returns).**

$$\lim_{N \to \infty} \Pi_i^* = \lim_{N \to \infty} \frac{E_j}{N^2} = 0$$

As the number of contestants grows, each agent's expected return collapses to zero while the aggregate waste approaches the full resource value. The contest becomes a pure value-destruction mechanism.

**Corollary 4.2 (Unit Dissipation Limit).**

$$\lim_{N \to \infty} \frac{D_N}{E_j} = 1$$

In the limit of many contestants, the **entire resource value is dissipated in conflict**. No value remains for any agent. This is the mathematical expression of the "tragedy of the commons" reframed as a thermodynamic result.

| $N$ | Individual investment $e_i^*$ | Total dissipation $D_N$ | $D_N / E_j$ | Individual payoff $\Pi_i^*$ |
|---|---|---|---|---|
| 2 | $E_j/4$ | $E_j/2$ | 50% | $E_j/4$ |
| 3 | $2E_j/9$ | $2E_j/3$ | 66.7% | $E_j/9$ |
| 5 | $4E_j/25$ | $4E_j/5$ | 80% | $E_j/25$ |
| 10 | $9E_j/100$ | $9E_j/10$ | 90% | $E_j/100$ |
| 100 | $99E_j/10000$ | $99E_j/100$ | 99% | $E_j/10000$ |

**Physical reading:** This table demonstrates that the energy spent fighting exceeds the energy gained from the resource. Even with just 2 agents, half the value is burned. With 10 agents, 90% is burned. The resource doesn't get "won" — it gets **lost**.

---

## 4. The Full Cost of Conflict: Boundary Damage and Repair

### 4.1 Beyond Contest Expenditure

The Tullock contest model captures the energy directly invested in fighting (the "ammunition"), but conflict inflicts additional costs:

1. **Offensive boundary damage** — the attacker's boundary degrades from neglect (energy diverted to attack) and counter-damage.
2. **Defensive boundary damage** — the defender's boundary is physically damaged by the attack.
3. **Repair costs** — both agents must subsequently invest energy to restore boundary integrity.

These costs are **on top of** the contest dissipation $D_N$ computed above.

### 4.2 Boundary Damage Functions

> **Definition 6 (Conflict Boundary Damage).** In a conflict where agent $i$ invests $e_i$ in the contest:
> 
> (a) **Offensive damage** to the attacker's own boundary:
> 
> $$\Delta B_i^{\text{off}} = \delta^{\text{off}} \cdot e_i$$
> 
> where $\delta^{\text{off}} \in [0, 1]$ is the offensive damage coefficient — the fraction of contest investment that translates into self-boundary degradation (energy diverted from maintenance, physical exposure during attack, counter-strikes).
> 
> (b) **Defensive damage** to the opponent's boundary:
> 
> $$\Delta B_j^{\text{def}} = \delta^{\text{def}} \cdot e_i$$
> 
> where $\delta^{\text{def}} \in [0, 1]$ is the defensive damage coefficient — the fraction of agent $i$'s attack energy that penetrates and damages agent $j$'s boundary.

**Interpretation:** In a two-agent conflict where both invest $e^*$:

- Agent $A$'s total boundary damage: $\Delta B_A = \delta^{\text{off}} \cdot e_A^* + \delta^{\text{def}} \cdot e_B^*$
- Agent $B$'s total boundary damage: $\Delta B_B = \delta^{\text{off}} \cdot e_B^* + \delta^{\text{def}} \cdot e_A^*$

For symmetric agents ($e_A^* = e_B^* = e^*$):

$$\Delta B_A = \Delta B_B = (\delta^{\text{off}} + \delta^{\text{def}}) \cdot e^*$$

### 4.3 Repair Costs: The Thermodynamic Asymmetry

Repairing a damaged boundary is thermodynamically more expensive than maintaining an intact one. This is a direct consequence of the Second Law: destruction increases entropy; reconstruction requires importing negentropy (ordered energy) from the environment.

> **Definition 7 (Repair Multiplier).** The energy required to repair boundary damage $\Delta B_i$ is:
> 
> $$W_{\text{repair},i} = \kappa \cdot \Delta B_i$$
> 
> where $\kappa \geq 1$ is the **repair multiplier**. The strict inequality $\kappa > 1$ holds in any physical system because:
> 
> (i) Repair requires first clearing the damage (entropy removal), then rebuilding (negentropy import) — two thermodynamic steps vs. one for maintenance.
> 
> (ii) The damaged state has higher entropy than the pre-damage state; returning to the original configuration requires at least $\Delta S \cdot T$ additional work (Clausius inequality / minimum work theorem, Second Law of Thermodynamics).

**Empirical calibration:** In biological systems, wound healing typically costs 2–5× more energy than the maintenance cost of the equivalent tissue (due to inflammation, immune response, scar tissue remodeling). We use $\kappa = 2$ as a conservative baseline in worked examples.

### 4.4 Total Conflict Cost: The Complete Ledger

Assembling all cost components for a two-agent symmetric contest ($r = 1$, $\sigma_A = \sigma_B$):

| Cost component | Per agent | System total |
|---|---|---|
| Contest investment $e_i^*$ | $E_j / 4$ | $E_j / 2$ |
| Boundary damage $\Delta B_i$ | $(\delta^{\text{off}} + \delta^{\text{def}}) \cdot E_j / 4$ | $(\delta^{\text{off}} + \delta^{\text{def}}) \cdot E_j / 2$ |
| Repair cost $W_{\text{repair},i}$ | $\kappa (\delta^{\text{off}} + \delta^{\text{def}}) \cdot E_j / 4$ | $\kappa (\delta^{\text{off}} + \delta^{\text{def}}) \cdot E_j / 2$ |
| **Total cost per agent** | $[1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})] \cdot E_j / 4$ | |
| **Total system cost** | | $[1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})] \cdot E_j/2$ |

Define the **total friction multiplier**:

$$\Phi \triangleq 1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})$$

Then:

$$L_{\text{system}}^{(2)} = \Phi \cdot \frac{E_j}{2}$$

where $L_{\text{system}}^{(2)}$ is the total system loss from a two-agent contest.

---

## 5. The Net-Negative Theorem

### 5.1 Statement

> **Theorem 5 (Net-Negative Conflict — The Thermodynamic Friction Theorem).**
> 
> *In a conflict contest over resource $E_j$ between $N \geq 2$ symmetric agents with friction multiplier $\Phi = 1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})$:*
> 
> *(a) The total system loss (energy dissipated by conflict) is:*
> 
> $$L_{\text{system}}^{(N)} = \Phi \cdot \frac{N - 1}{N} \cdot E_j$$
> 
> *(b) The net system value (resource obtained minus all costs) is:*
> 
> $$V_{\text{net}} = E_j - L_{\text{system}}^{(N)} = E_j \left(1 - \Phi \cdot \frac{N - 1}{N}\right)$$
> 
> *(c) The conflict is **net-negative** ($V_{\text{net}} < 0$) if and only if:*
> 
> $$\Phi > \frac{N}{N - 1}$$
> 
> *For $N = 2$: $\Phi > 2$. For $N \geq 3$: $\Phi > 3/2$. For $N \to \infty$: $\Phi > 1$.*

*Proof.* The contest dissipation for $N$ symmetric agents is $D_N = \frac{N-1}{N} E_j$ (Theorem 4). Total boundary damage across all agents is $N \cdot (\delta^{\text{off}} + \delta^{\text{def}}) \cdot e_i^* = (\delta^{\text{off}} + \delta^{\text{def}}) \cdot \frac{N-1}{N} E_j$ (each agent's damage is $(\delta^{\text{off}} + \delta^{\text{def}}) e_i^*$, summed over $N$ agents, using $N e_i^* = D_N$). Similarly, total repair cost is $\kappa (\delta^{\text{off}} + \delta^{\text{def}}) \cdot \frac{N-1}{N} E_j$. Summing:

$$L_{\text{system}}^{(N)} = \left[1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})\right] \cdot \frac{N-1}{N} E_j = \Phi \cdot \frac{N-1}{N} E_j$$

The net value is $V_{\text{net}} = E_j - L_{\text{system}}^{(N)}$. Setting $V_{\text{net}} < 0$:

$$E_j < \Phi \cdot \frac{N-1}{N} E_j \iff 1 < \Phi \cdot \frac{N-1}{N} \iff \Phi > \frac{N}{N-1}$$

All damage terms are aggregate: $L_{\text{system}}^{(N)}$ sums contest dissipation and boundary damage across all $N$ agents, not per-pair. For asymmetric agents, the per-pair damage components $(\delta_i^{\text{off}} + \delta_i^{\text{def}}) e_i^*$ are summed over all $i$. $\square$

> **Remark (per-agent damage and N-scaling).** The per-agent damage term $(\delta^{\text{off}} + \delta^{\text{def}}) e_i^*$ is exact for $N = 2$ (one opponent). For $N > 2$, each agent inflicts offensive damage on one primary target but receives defensive damage from $N-1$ opponents; the correct per-agent formula is $(\delta^{\text{off}} + (N-1)\delta^{\text{def}}) e_i^*$. Because the proof uses the *aggregate* total $N \cdot (\delta^{\text{off}} + \delta^{\text{def}}) e_i^*$ — which equals the sum of all pairwise offensive hits and underestimates total defensive exposure — the formula is a **conservative lower bound** on system-wide conflict cost for $N > 2$. The qualitative conclusions of Theorem 5 (net-negativity threshold) remain valid and are, if anything, strengthened when the full $N > 2$ damage is accounted for.

### 5.2 Physical Interpretation

**Corollary 5.1 (Inevitability of Net-Negative Conflict).** *For any physical system where boundary damage is non-negligible ($\delta^{\text{off}} + \delta^{\text{def}} > 0$) and repair is thermodynamically irreversible ($\kappa > 1$), the conflict is net-negative for sufficiently many contestants.*

*Proof.* As $N \to \infty$, the threshold $N/(N-1) \to 1$. Since $\Phi = 1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}}) > 1$ whenever $\delta^{\text{off}} + \delta^{\text{def}} > 0$, there exists a finite $N^*$ such that $\Phi > N^*/(N^* - 1)$, beyond which the conflict is net-negative. Specifically:

$$N^* = \left\lfloor \frac{\Phi}{\Phi - 1} \right\rfloor + 1$$

$\square$

**Corollary 5.2 (The Two-Agent Threshold).** *For two agents ($N = 2$), the conflict is net-negative when $\Phi > 2$, i.e., when:*

$$(1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}}) > 1$$

*With $\kappa = 2$ (conservative repair multiplier) and $\delta^{\text{off}} = \delta^{\text{def}} = 0.2$ (modest damage coefficients): $\Phi = 1 + 3 \cdot 0.4 = 2.2 > 2$. The conflict is net-negative even between just two agents.*

### 5.3 Numerical Illustration: The Friction Multiplier Landscape

The following table shows the total system loss $L_{\text{system}}^{(N)} / E_j$ for various parameter combinations:

| $\delta^{\text{off}} + \delta^{\text{def}}$ | $\kappa$ | $\Phi$ | $N = 2$ | $N = 5$ | $N = 10$ | $N = 100$ |
|---|---|---|---|---|---|---|
| 0 (pure contest) | — | 1.0 | 50% | 80% | 90% | 99% |
| 0.2 | 1.5 | 1.5 | 75% | 120% | 135% | 148.5% |
| 0.4 | 2.0 | 2.2 | 110% | 176% | 198% | 217.8% |
| 0.6 | 2.0 | 2.8 | 140% | 224% | 252% | 277.2% |
| 0.8 | 3.0 | 4.2 | 210% | 336% | 378% | 415.8% |

Values exceeding 100% represent **net-negative outcomes** — the system dissipates more energy than the contested resource contains. With even modest boundary damage parameters ($\delta = 0.2$, $\kappa = 1.5$), two-agent contests are net-neutral and five-agent contests are already deeply net-negative.

---

## 6. Comparison: Conflict vs. Cooperative Regimes

### 6.1 The Cooperative Baseline

Under the rights-based cooperative regime (Theorem 3), agents achieve the variational equilibrium allocation with:

- **Zero contest expenditure:** No agent invests energy in fighting.
- **Zero boundary damage:** No boundaries are breached.
- **Zero repair costs:** No damage to repair.
- **Shadow price costs only:** Each agent's cost is bounded by the Lagrange multipliers $\mu_{Bk}^*$ — the opportunity cost of respecting others' rights.

The total system welfare under cooperation (Theorem 3) is:

$$SW_{\text{coop}} = \sum_{i=1}^N U_i(\mathbf{x}_i^*)$$

### 6.2 The Conflict Regime

Under conflict (no rights), the total system welfare is:

$$SW_{\text{conflict}} = \sum_{i=1}^N \left[ p_i \cdot E_j - e_i^* - W_{\text{repair},i} \right] = E_j - D_N - W_{\text{repair, total}}$$

$$= E_j - \Phi \cdot \frac{N-1}{N} E_j = E_j \left(1 - \Phi \cdot \frac{N-1}{N}\right)$$

### 6.3 The Cooperation Premium

> **Theorem 6 (Cooperation Dominance).** *The cooperative regime strictly dominates the conflict regime whenever resource collision occurs. Specifically:*
>
> $$SW_{\text{coop}} - SW_{\text{conflict}} \geq \Phi \cdot \frac{N-1}{N} \cdot E_j > 0$$
>
> *The cooperation premium is:*
> - *Increasing in $N$ (more agents → more waste in conflict)*
> - *Increasing in $\Phi$ (more boundary damage → more destructive conflict)*
> - *Increasing in $E_j$ (higher-value resources → higher absolute waste)*

*Proof.* Under cooperation, the full resource value $E_j$ is available for productive allocation (minus only the shadow-price opportunity costs, which are transfers between agents, not system losses). Under conflict, the system loses $L_{\text{system}}^{(N)} = \Phi \cdot \frac{N-1}{N} E_j$ in pure waste. Since waste does not produce utility:

$$SW_{\text{coop}} - SW_{\text{conflict}} \geq L_{\text{system}}^{(N)} = \Phi \cdot \frac{N-1}{N} \cdot E_j > 0$$

The inequality is strict because $\Phi \geq 1$, $N \geq 2$, and $E_j > 0$. $\square$

**Physical interpretation:** This is the formal proof of our central claim: *"The only way to globally minimize $E_{\text{conflict}}$ across the system is to establish mutual constraints."* The cooperative premium quantifies exactly how much energy the system saves by adopting rights.

### 6.4 Worked Example: Cooperation vs. Conflict Under Scarcity

Using the symmetric agents from the Lagrangian constraints derivation, §8.7 ($\alpha = 10$, $\beta = 1$), with $R = 12$ and $\Phi = 2.2$ ($\delta^{\text{off}} = \delta^{\text{def}} = 0.2$, $\kappa = 2$):

**Cooperative regime (VE):**
- Allocation: $x_A^* = x_B^* = 6$
- Utilities: $U_A = U_B = 42$
- System welfare: $SW_{\text{coop}} = 84$

**Conflict regime:**

The contested portion is the collision overlap. Each agent wants 10 but only 12 is available. The contested amount is $\sum x_i^{\circ} - R = 20 - 12 = 8$ units.

Contest over the excess demand ($E_{\text{contested}} = 8$ in resource units, with energy value depending on the utility function):

- Contest dissipation: $D_2 = E_{\text{contested}}/2 = 4$ (energy units lost to fighting)
- Boundary damage + repair: $(1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}}) \cdot D_2 = 3 \cdot 0.4 \cdot 4 = 4.8$
- Total system loss: $D_2 + 4.8 = 8.8$ energy units

Even a simplified conflict model shows the cooperation premium: the system saves at least 8.8 energy units by establishing mutual constraints — more than the entire contested portion of the resource.

---

## 7. Cascading Network Effects: Trust and Ambient Friction

### 7.1 Motivation

The preceding analysis treats each conflict as isolated. In reality, conflict events propagate through the network: when agent $A$ violates agent $B$'s boundary, every other agent in the network must **update its threat model**. This section formalizes the cascading cost.

### 7.2 The Network Friction Coefficient

> **Definition 8 (Network Friction).** Consider a network of $N$ agents engaged in cooperative resource exchange. The **network friction coefficient** $\phi \geq 0$ parameterizes the per-transaction overhead cost due to monitoring, verification, and precautionary defense:
> 
> $$C_{\text{overhead}}(\phi) = \phi \cdot E_{\text{transaction}}$$
> 
> where $E_{\text{transaction}}$ is the energy value of a cooperative transaction. At $\phi = 0$, transactions are frictionless (perfect trust). At $\phi > 0$, each interaction bears an overhead tax.

**Examples of friction overhead:**
- **Biological:** Immune surveillance costs (metabolic energy spent monitoring for pathogens, even when healthy).
- **Economic:** Transaction costs (legal fees, contract enforcement, insurance, escrow).
- **Societal:** Policing, auditing, intelligence gathering, defensive military posture.

### 7.3 Trust as a State Variable

Define the **network trust level** $T \in [0, 1]$ as the complement of normalized friction:

$$T = \frac{1}{1 + \phi}$$

- $T = 1$: perfect trust ($\phi = 0$), frictionless cooperation.
- $T \to 0$: zero trust ($\phi \to \infty$), cooperative transactions become prohibitively expensive.

Equivalently: $\phi = \frac{1 - T}{T}$.

### 7.4 Violation-Induced Friction Increase

Each boundary violation increases the network friction coefficient:

> **Definition 9 (Friction Injection).** When a boundary violation of severity $v > 0$ (measured in energy units of damage) occurs at time $t$, the network friction coefficient updates as:
> 
> $$\phi_{t+1} = \phi_t + \eta \cdot v$$
> 
> where $\eta > 0$ is the **friction sensitivity** — how strongly the network responds to violations. The sensitivity $\eta$ depends on:
> - **Visibility:** Public violations have higher $\eta$ (all agents update simultaneously).
> - **Precedent:** First violations in a low-friction network have higher $\eta$ (trust is fragile).
> - **Network density:** Denser networks (more inter-agent connections) have higher $\eta$ (information propagates faster).

### 7.5 The Cost of Ambient Friction

If the network has $M$ cooperative transactions per period, each of average value $\bar{E}$, the **total friction tax** per period is:

$$C_{\text{friction}} = \phi \cdot M \cdot \bar{E}$$

This is the aggregate overhead energy that the network burns on monitoring, verification, and defense — energy that could otherwise go to productive Identity Preservation.

### 7.6 Friction Recovery (Trust Rebuilding)

Trust rebuilds slowly through consistent cooperative behavior:

> **Definition 10 (Friction Decay).** In the absence of new violations, the friction coefficient decays toward zero at rate $\epsilon \in (0, 1)$ per period:
> 
> $$\phi_{t+1} = (1 - \epsilon) \cdot \phi_t$$
> 
> This exponential decay means friction halves every $t_{1/2} = \ln 2 / \ln(1/(1 - \epsilon))$ periods.

**Key asymmetry:** Friction injection (Definition 9) is **instantaneous and additive** — a single violation immediately increases $\phi$. Friction recovery is **gradual and multiplicative** — rebuilding trust requires persistent cooperative behavior over many periods. This asymmetry is thermodynamically natural: increasing entropy (breaking trust) is easy; decreasing entropy (rebuilding trust) requires sustained work.

### 7.7 The Cascading Cost Theorem

> **Theorem 7 (Cascading Friction — The Network Amplification Effect).**
> 
> *A single boundary violation of severity $v$ in a network with $M$ transactions of average value $\bar{E}$ and friction sensitivity $\eta$ produces a **total cascading cost** of:*
> 
> $$C_{\text{cascade}} = \frac{\eta \cdot v \cdot M \cdot \bar{E}}{\epsilon}$$
> 
> *over the full recovery period $[t_{\text{violation}}, \infty)$. The ratio of cascading cost to direct conflict cost $v$ is:*
> 
> $$\frac{C_{\text{cascade}}}{v} = \frac{\eta \cdot M \cdot \bar{E}}{\epsilon}$$
> 
> *This ratio scales linearly with network size ($M$) and inversely with recovery rate ($\epsilon$).*

*Proof.* The violation at time $t_0$ injects $\Delta\phi = \eta v$ into the friction coefficient. Without further violations, the excess friction at time $t_0 + k$ is:

$$\Delta\phi_k = \eta v \cdot (1 - \epsilon)^k$$

The excess friction cost at period $k$ is $\Delta\phi_k \cdot M \cdot \bar{E}$. The total cascading cost is the sum over all future periods:

$$C_{\text{cascade}} = \sum_{k=0}^{\infty} \eta v \cdot (1 - \epsilon)^k \cdot M \cdot \bar{E} = \eta v \cdot M \cdot \bar{E} \cdot \frac{1}{\epsilon}$$

using the geometric series formula $\sum_{k=0}^{\infty} q^k = 1/(1-q)$ for $q = 1 - \epsilon \in (0, 1)$. $\square$

### 7.8 Numerical Illustration: The Amplification Factor

Consider a modest-sized economic network:

| Parameter | Symbol | Value | Interpretation |
|---|---|---|---|
| Network transactions / period | $M$ | 1,000 | A small community |
| Average transaction value | $\bar{E}$ | 10 | Energy units per transaction |
| Friction sensitivity | $\eta$ | 0.01 | 1% of violation severity becomes friction |
| Recovery rate | $\epsilon$ | 0.05 | ~14 periods to halve friction |
| Violation severity | $v$ | 50 | A significant boundary breach |

**Direct cost of the violation:** $v = 50$ energy units.

**Cascading cost:**

$$C_{\text{cascade}} = \frac{0.01 \times 50 \times 1000 \times 10}{0.05} = \frac{5000}{0.05} = 100{,}000 \text{ energy units}$$

**Amplification factor:** $C_{\text{cascade}} / v = 100{,}000 / 50 = 2{,}000\times$.

The network-level damage from a single violation is **two thousand times** greater than the direct damage. This formalizes the intuition that small lies or broken promises don't destroy the network immediately, but they increase the ambient "heat" (distrust).

### 7.9 Multiple Violations: The Friction Ratchet

When violations are recurring (rate $\nu$ violations per period, each of severity $v$), the steady-state friction coefficient is:

$$\phi_{\infty} = \frac{\nu \cdot \eta \cdot v}{\epsilon}$$

and the steady-state friction tax is:

$$C_{\text{friction}}^{\infty} = \phi_{\infty} \cdot M \cdot \bar{E} = \frac{\nu \cdot \eta \cdot v \cdot M \cdot \bar{E}}{\epsilon}$$

> **Corollary 7.1 (Friction Ratchet).** *If the violation rate $\nu$ exceeds the critical threshold:*
> 
> $$\nu^* = \frac{\epsilon}{\eta \cdot v} \cdot \frac{E_{\text{coop net}}}{M \cdot \bar{E}}$$
> 
> *where $E_{\text{coop net}}$ is the total cooperative surplus of the network, then the friction tax exceeds the cooperative surplus and the network collapses — cooperation becomes energetically unprofitable.*

This is the mathematical formalization of societal collapse: when violations are too frequent and trust recovery is too slow, the overhead cost of maintaining any cooperative structure exceeds its benefit, and agents are better off in isolation or smaller, higher-trust sub-networks.

---

## 8. The Interaction Cost Function: Formal Definition

Synthesizing the results above into a single mathematical object:

> **Definition 11 (Interaction Cost Function).** The **interaction cost function** $\mathcal{C} : \mathbb{R}_{\geq 0}^N \times [0, \infty) \to \mathbb{R}_{\geq 0}$ maps a strategy profile and network friction state to the total energy dissipated by non-cooperative interactions:
> 
> $$\mathcal{C}(\mathbf{e}, \phi) = \underbrace{\sum_{i=1}^{N} e_i}_{\text{contest dissipation}} + \underbrace{(1 + \kappa) \sum_{i=1}^{N} (\delta^{\text{off}} + \delta^{\text{def}}) \, e_i}_{\text{boundary damage + repair}} + \underbrace{\phi \cdot M \cdot \bar{E}}_{\text{ambient friction tax}}$$
> 
> where $\mathbf{e} = (e_1, \ldots, e_N)$ is the vector of contest investments.
> 
> At the contest Nash equilibrium:
> 
> $$\mathcal{C}^* = \Phi \cdot \frac{N-1}{N} \cdot E_j + \phi \cdot M \cdot \bar{E}$$

*(The per-agent boundary damage term $(\delta^{\text{off}} + \delta^{\text{def}})e_i$ is exact for $N=2$; for $N>2$ this is a conservative lower bound — see Remark following Theorem 5.)*

This is the concept of thermodynamic friction, now given a precise mathematical form. It is the formal name for what physics would loosely call the "frictional heat" generated by conflict in a multi-agent system.

---

## 9. Extended Worked Examples

### 9.1 Example 1: Two-Agent Resource Contest (Baseline)

**Setup:** Two symmetric agents ($\sigma_A = \sigma_B = 1$), one resource worth $E_j = 100$ energy units. Boundary parameters: $\delta^{\text{off}} = 0.15$, $\delta^{\text{def}} = 0.25$, $\kappa = 2$.

**Friction multiplier:**

$$\Phi = 1 + (1 + 2)(0.15 + 0.25) = 1 + 3 \times 0.4 = 2.2$$

**Contest equilibrium:**

$$e_A^* = e_B^* = \frac{100}{4} = 25$$

**Total dissipation:** $D_2 = 50$

**Boundary damage per agent:** $(\delta^{\text{off}} + \delta^{\text{def}}) \times 25 = 0.4 \times 25 = 10$

**Repair cost per agent:** $\kappa \times 10 = 20$

**Total system loss:** $50 + 2(10 + 20) = 50 + 60 = 110$ (i.e., $\Phi \times 50 = 2.2 \times 50 = 110$)

**Net system value:** $100 - 110 = -10$ energy units.

**Verdict: Net-negative.** The conflict dissipated 10% more energy than the resource contained. Both agents would have been better off splitting the resource (each getting 50 energy units with zero conflict cost).

### 9.2 Example 2: Five-Agent Scramble

Same parameters as above, but $N = 5$.

$$e_i^* = \frac{4 \times 100}{25} = 16, \qquad D_5 = 5 \times 16 = 80$$

**Total system loss:** $\Phi \times 80 = 2.2 \times 80 = 176$

**Net system value:** $100 - 176 = -76$ energy units.

**Verdict: Catastrophically net-negative.** The system dissipates 76% more energy than the resource is worth. Each agent's expected payoff: $100/25 = 4$ from winning, minus $16$ investment, minus boundary+repair costs.

### 9.3 Example 3: The "Profitable Bully" — When Unilateral Defection Pays (Temporarily)

Not all defection is immediately net-negative for the defector. Consider agents with valuations $V_A = V_B = 100$ but asymmetric effectiveness ($\sigma_A = 3$, $\sigma_B = 1$) in the standard Tullock model:

Using the symmetric-valuation Tullock NE with effectiveness weights, the investments are:

$$e_A^* = e_B^* = \frac{\sigma_A \sigma_B}{(\sigma_A + \sigma_B)^2} E_j = \frac{3}{16} \times 100 = 18.75$$

Winning probabilities: $p_A = \frac{\sigma_A}{\sigma_A + \sigma_B} = \frac{3}{4}$, $p_B = \frac{1}{4}$.

Agent $A$'s expected payoff (before boundary costs): $0.75 \times 100 - 18.75 = 56.25$.

Agent $B$'s expected payoff: $0.25 \times 100 - 18.75 = 6.25$.

Total contest dissipation: $2 \times 18.75 = 37.5$.

With boundary costs ($\Phi = 2.2$): total system loss = $2.2 \times 37.5 = 82.5$.

**System net:** $100 - 82.5 = 17.5$ — barely positive.

**But the bully profits at the victim's expense.** The private incentive to bully exists even when the systemic outcome is nearly net-negative. **This is precisely why rights as constraints are necessary** (Theorem 2): the bully's profit is private and short-term; the system's loss is public, and cascading friction (Theorem 7) means the network-level damage vastly exceeds the direct cost.

---

## 10. Decisive Contests ($r > 1$): Escalation Dynamics

### 10.1 The Impact of Decisiveness

When $r > 1$, the contest becomes "all-or-nothing" — agents invest more aggressively because a marginal increase in investment translates into a larger increase in winning probability.

For symmetric agents with general $r$:

$$e_i^* = \frac{r(N-1)}{N^2} \cdot E_j, \qquad D_N = \frac{r(N-1)}{N} \cdot E_j$$

> **Corollary 5.3 (Escalation Instability).** *For $r > 1$ and $N \geq 2$, the dissipation exceeds the resource value ($D_N > E_j$) when $r > N/(N-1)$. For $N = 2$: $r > 2$. For large $N$: $r > 1 + 1/N \approx 1$. The contest self-destructs — even the "pure contest" expenditure exceeds what the resource is worth, before accounting for boundary damage.*

**Physical interpretation:** Arms races are decisive contests with $r > 1$. The mathematical result predicts what history confirms: arms races consume more resources than the territories they contest are worth.

---

## 11. Summary of Results

| # | Result | Statement | Significance |
|---|---|---|---|
| **P2** | Symmetric Contest NE | $e_i^* = E_j/4$ (each), $D_2 = E_j/2$ | Half the resource is consumed by fighting |
| **P3** | Asymmetric Contest NE | $D_2 = V_A V_B/(V_A + V_B)$ | Harmonic semi-mean dissipation |
| **T4** | Dissipation Scaling | $D_N = (N-1)E_j/N \to E_j$ | Contest waste approaches 100% as $N$ grows |
| **C4.1** | Vanishing Returns | $\Pi_i^* = E_j/N^2 \to 0$ | Individual gains collapse |
| **C4.2** | Unit Dissipation Limit | $D_N/E_j \to 1$ | Full resource dissipation in the limit |
| **T5** | Net-Negative Conflict | $V_{\text{net}} < 0 \iff \Phi > N/(N-1)$ | Conflict dissipates more than the resource is worth |
| **C5.1** | Inevitability | Net-negative for all $N \geq N^*$ when $\Phi > 1$ | Physical systems always hit the threshold |
| **C5.2** | Two-Agent Threshold | Net-negative for $N = 2$ when $\Phi > 2$ | Even 1-on-1 conflict can be net-negative |
| **T6** | Cooperation Dominance | $SW_{\text{coop}} - SW_{\text{conflict}} \geq \Phi \cdot \frac{N-1}{N} E_j$ | Cooperation is strictly superior |
| **T7** | Cascading Friction | $C_{\text{cascade}} = \eta v M \bar{E} / \epsilon$ | Network amplification of direct damage |
| **C7.1** | Friction Ratchet | Collapse threshold $\nu^*$ | Too many violations → network disintegration |
| **C5.3** | Escalation Instability | $D_N > E_j$ for $r > N/(N-1)$ | Arms races are self-destructive |

---

## 12. Notation Index

| Symbol | Meaning |
|---|---|
| $B_i$ | Agent $i$'s boundary integrity (energy units) |
| $\gamma_i$ | Entropy leakage rate (boundary degradation per unit time) |
| $F_i(s)$ | Boundary resistance function at depth $s$ |
| $E_j$ | Energy value of contested resource $j$ |
| $e_i$ | Agent $i$'s contest investment (energy diverted to conflict) |
| $\sigma_i$ | Agent $i$'s conflict effectiveness |
| $r$ | Contest decisiveness parameter |
| $p_i$ | Agent $i$'s contest success probability |
| $\Pi_i$ | Agent $i$'s contest payoff |
| $\delta^{\text{off}}$ | Offensive boundary damage coefficient |
| $\delta^{\text{def}}$ | Defensive boundary damage coefficient |
| $\kappa$ | Repair multiplier ($\geq 1$; thermodynamic irreversibility) |
| $\Phi$ | Total friction multiplier: $1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})$ |
| $D_N$ | Total contest dissipation for $N$ agents |
| $L_{\text{system}}^{(N)}$ | Total system loss (dissipation + damage + repair) |
| $V_{\text{net}}$ | Net system value (resource value minus total loss) |
| $\phi$ | Network friction coefficient |
| $T$ | Network trust level: $1/(1 + \phi)$ |
| $\eta$ | Friction sensitivity (how strongly violations increase $\phi$) |
| $\epsilon$ | Friction recovery rate |
| $M$ | Number of cooperative transactions per period |
| $\bar{E}$ | Average energy per cooperative transaction |
| $\nu$ | Violation rate (violations per period) |
| $\mathcal{C}$ | Interaction cost function |

> **Symbol disambiguation.** In this file: $\sigma_i$ = conflict effectiveness, $r$ = contest decisiveness parameter. In other derivation files, $\sigma$ denotes assimilation intensity (value dynamics), search efficiency (information-negentropy Part B), or survival probability (game theory). The symbol $r$ denotes coupling distance (value dynamics) or time-preference rate (game theory). Context and subscripts distinguish these uses throughout the paper.