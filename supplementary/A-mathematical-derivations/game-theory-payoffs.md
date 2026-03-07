# Energy-Based Game Theory — Ethics as Nash Equilibrium

---

## 0. Preamble

This document contains the formal mathematical derivation for the energy-based game theory framework. Building on the preceding derivations, we now construct **energy-denominated payoff matrices** and prove that the cooperative strategy set traditionally identified as "ethics" is the unique Nash Equilibrium of the repeated multi-agent interaction game.

The contribution is **applied mathematics**: we use classical game theory [@Nash1950], the theory of repeated games [@Fudenberg1986], evolutionary game theory [@MaynardSmith1973], and mechanism design to prove that cooperation emerges not from moral sentiment but from the mathematical structure of energy-based payoffs.

**Key references for the tools used:**

- [@Nash1950] — existence of Nash equilibrium.
- [@Fudenberg1986] — cooperation in infinitely repeated games.
- [@MaynardSmith1973] — evolutionary stable strategies.
- [@Axelrod1984] — iterated Prisoner's Dilemma and tit-for-tat.
- [@OsborneRubinstein1994] — comprehensive treatment of equilibrium concepts.

**Notational continuity from preceding derivations:**

- $N$ agents, strategy vectors $\mathbf{x}_i$, utility functions $U_i$ (Lagrangian constraints derivation).
- Resource endowment $\mathbf{R}$; scarcity constraints $\sum_i x_{ij} \leq R_j$ (Lagrangian constraints derivation).
- Friction multiplier $\Phi = 1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})$ (thermodynamic friction derivation).
- Network friction coefficient $\phi$; friction sensitivity $\eta$; recovery rate $\epsilon$ (thermodynamic friction derivation).
- Deception cost $\Delta U_B(q)$; verification overhead $\Delta W(q)$ (information-entropy derivation).
- Cooperative transaction count $M$; average transaction value $\bar{E}$ (thermodynamic friction derivation).

---

## 1. The Energy-Denominated Payoff Model

### 1.1 Motivation: Why Energy Changes Everything

Standard game theory uses abstract utility values (often called "points" or "utils"). The Prisoner's Dilemma, for example, assigns payoffs like (3, 3) for mutual cooperation and (1, 1) for mutual defection, without specifying what these numbers represent or where they come from.

Our framework replaces abstract utils with **thermodynamic energy** (Joules, Calories, or normalized energy units). This is not merely a relabeling — it imports the physical constraints that energy must satisfy:

1. **Conservation:** Energy is neither created nor destroyed. Conflict does not generate new energy; it dissipates existing energy as waste heat (thermodynamic friction derivation, §5).
2. **Positivity of costs:** All physical actions require energy expenditure ($W = \int F \cdot dx \geq 0$). Conflict investments, boundary damage, and repair are non-negative real costs, not arbitrary parameters.
3. **Diminishing returns:** The concavity of utility in resources (Assumption 1b) means that marginal gains decrease while marginal losses increase — a thermodynamic asymmetry that breaks the symmetry of abstract payoffs.
4. **Network coupling:** An agent's payoff depends not only on the current interaction but on the network friction state $\phi$, which persists across interactions (thermodynamic friction derivation, §7).

These physical constraints **structurally determine** the payoff matrices. The cooperative equilibrium is not an assumption fed into the model — it is a **consequence** of the physics.

### 1.2 Strategy Space

Each agent selects from two meta-strategies in any pairwise interaction over a contested resource:

> **Definition 19 (Cooperative and Defection Strategies).**
>
> - **Cooperate (C):** Respect the rights constraint (Definition 2). Accept the constrained allocation $\mathbf{x}_i^*$ determined by the variational equilibrium (Theorem 3). Incur only the trade/coordination cost $c > 0$ (the energy cost of negotiation, contract enforcement, or social coordination).
>
> - **Defect (D):** Violate the rights constraint. Attempt to seize the resource by force or deception. This triggers the conflict contest (thermodynamic friction derivation, §3) and/or deception channel (information-entropy derivation, §2), incurring the associated costs.

**Interpretation:** "Cooperate" means operating within the constraint system (ethical behavior). "Defect" means violating constraints (unethical behavior). The strategy choice is not about morality — it is about whether to expend energy on conflict or coordination.

### 1.3 The Energy Variables

For a pairwise interaction over resource $E_R > 0$:

| Symbol | Meaning | Source |
|---|---|---|
| $E_R$ | Energy value of the contested resource | Physical environment |
| $c$ | Coordination cost (trade negotiation, contract) | Cooperative overhead; $c \ll E_R$ |
| $e^*$ | Nash equilibrium contest investment per agent | Thermodynamic friction, Prop. 2: $e^* = E_R/4$ (symmetric) |
| $\Phi$ | Total friction multiplier | Thermodynamic friction: $\Phi = 1 + (1+\kappa)(\delta^{\text{off}} + \delta^{\text{def}})$ |
| $\phi_0$ | Current network friction coefficient | Thermodynamic friction, §7 |
| $\Delta\phi$ | Friction injection from defection | Thermodynamic friction, Def. 9: $\Delta\phi = \eta \cdot v$ |
| $\bar{E}$ | Average cooperative transaction value | Network parameter |
| $M$ | Number of transactions per period | Network parameter |

---

## 2. The Two-Player Payoff Matrix

### 2.1 Construction

Consider agents $A$ and $B$ interacting over resource $E_R$. Using the energy variables defined above, with the equal-split convention under cooperation:

**Case (C, C) — Mutual Cooperation:**

Both agents respect the constraint. The resource is split according to the variational equilibrium (equal split for symmetric agents). Each pays the coordination cost $c$.

$$\pi_A^{CC} = \pi_B^{CC} = \frac{E_R}{2} - c$$

**Case (D, C) — Unilateral Defection (A defects, B cooperates):**

Agent $A$ attacks the cooperating agent $B$. Since $B$ is not investing in contest (expecting cooperation), $A$ seizes the resource but still incurs:
- The metabolic cost of the aggressive action: $e_A^{\text{attack}}$ (energy of mounting the violation)
- Boundary damage to self (offensive): $\delta^{\text{off}} \cdot e_A^{\text{attack}}$ (exposure cost)
- Repair of self-damage: $\kappa \cdot \delta^{\text{off}} \cdot e_A^{\text{attack}}$

Agent $B$, caught unprepared, suffers:
- Loss of the full resource: $-E_R$ (relative to the cooperative baseline)
- Defensive boundary damage: $\delta^{\text{def}} \cdot e_A^{\text{attack}}$
- Repair cost: $\kappa \cdot \delta^{\text{def}} \cdot e_A^{\text{attack}}$

However, the defector against a cooperator faces much lower resistance. We model the attack cost against an undefended boundary as $e_A^{\text{attack}} = \theta \cdot E_R$ where $\theta \in (0, 1)$ is the **exploitation efficiency** — the fraction of the resource's value the defector must spend to seize it from an unprepared cooperator. Typically $\theta \ll 1/2$ (attacking an undefended target is cheap).

$$\pi_A^{DC} = E_R - \theta E_R \left[1 + (1 + \kappa)\delta^{\text{off}}\right] = E_R\left[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})\right]$$

$$\pi_B^{DC} = -\theta E_R (1 + \kappa)\delta^{\text{def}}$$

The victim $B$ receives nothing from the resource and additionally suffers boundary damage and repair costs from the attack.

**Case (C, D) — Symmetric mirror of (D, C):**

$$\pi_A^{CD} = -\theta E_R (1 + \kappa)\delta^{\text{def}}$$

$$\pi_B^{CD} = E_R\left[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})\right]$$

**Case (D, D) — Mutual Defection:**

Both agents fight. This is the Tullock contest from the thermodynamic friction derivation (Proposition 2). Each invests $e^* = E_R/4$, wins with probability 1/2, and suffers boundary damage from both offense and defense plus repair costs.

Each agent's expected payoff is the winning prize minus all costs:

$$\pi_A^{DD} = \pi_B^{DD} = \frac{E_R}{2} - e^* - (\delta^{\text{off}} + \delta^{\text{def}}) e^* - \kappa(\delta^{\text{off}} + \delta^{\text{def}}) e^*$$

$$= \frac{E_R}{2} - \left[1 + (1 + \kappa)(\delta^{\text{off}} + \delta^{\text{def}})\right] e^* = \frac{E_R}{2} - \Phi \cdot \frac{E_R}{4}$$

$$= \frac{E_R}{2}\left(1 - \frac{\Phi}{2}\right)$$

### 2.2 The Payoff Matrix (Single-Round)

Assembling into standard normal form, with row player $A$ and column player $B$:

$$\begin{array}{c|c|c}
 & B: C & B: D \\ \hline
A: C & \left(\frac{E_R}{2} - c, \;\; \frac{E_R}{2} - c\right) & \left(-\theta E_R (1+\kappa)\delta^{\text{def}}, \;\; E_R[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})]\right) \\ \hline
A: D & \left(E_R[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})], \;\; -\theta E_R (1+\kappa)\delta^{\text{def}}\right) & \left(\frac{E_R}{2}(1 - \frac{\Phi}{2}), \;\; \frac{E_R}{2}(1 - \frac{\Phi}{2})\right) \\
\end{array}$$

### 2.3 Parameterization: The Physical Prisoner's Dilemma

To classify this game, define shorthand payoffs:

$$T = \pi^{DC}_{\text{defector}} = E_R\left[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})\right] \quad \text{(Temptation)}$$

$$R = \pi^{CC} = \frac{E_R}{2} - c \quad \text{(Reward for cooperation)}$$

$$P = \pi^{DD} = \frac{E_R}{2}\left(1 - \frac{\Phi}{2}\right) \quad \text{(Punishment for mutual defection)}$$

$$S = \pi^{CD}_{\text{sucker}} = -\theta E_R (1+\kappa)\delta^{\text{def}} \quad \text{(Sucker's payoff)}$$

The classic Prisoner's Dilemma requires $T > R > P > S$. Let us verify each inequality under physical constraints:

**Claim: $T > R$ (temptation exceeds reward) when exploitation is cheap.**

$$T > R \iff E_R[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})] > \frac{E_R}{2} - c$$

$$\iff \frac{E_R}{2} + c > \theta E_R(1 + (1+\kappa)\delta^{\text{off}})$$

$$\iff \theta < \frac{1/2 + c/E_R}{1 + (1+\kappa)\delta^{\text{off}}}$$

For $c \ll E_R$ and $\delta^{\text{off}} = 0.15$, $\kappa = 2$: threshold $\approx 0.5/1.45 \approx 0.345$. So $T > R$ when the exploitation cost $\theta < 0.345$ — i.e., when stealing from a cooperator is less than 34.5% of the resource value. This is the standard condition: defection is *tempting* when exploiting a cooperator is cheap.

**Claim: $R > P$ (cooperation beats mutual defection).**

$$R > P \iff \frac{E_R}{2} - c > \frac{E_R}{2}\left(1 - \frac{\Phi}{2}\right) = \frac{E_R}{2} - \frac{\Phi E_R}{4}$$

$$\iff \frac{\Phi E_R}{4} > c$$

Since $\Phi \geq 1$ and $c \ll E_R$, this holds for any non-trivial friction multiplier. Even with zero boundary damage ($\Phi = 1$), mutual cooperation beats mutual defection as long as the coordination cost is less than $E_R/4$ — i.e., less than the per-agent contest dissipation.

**Claim: $P > S$ (mutual defection beats being the sucker) when friction is not too extreme.**

$$P > S \iff \frac{E_R}{2}\left(1 - \frac{\Phi}{2}\right) > -\theta E_R(1+\kappa)\delta^{\text{def}}$$

$$\iff \frac{1}{2} - \frac{\Phi}{4} + \theta(1+\kappa)\delta^{\text{def}} > 0 \iff \Phi < 2 + 4\theta(1+\kappa)\delta^{\text{def}} \equiv \Phi_{\text{PD}}$$

For the baseline parameters ($\theta = 0.15$, $\kappa = 2$, $\delta^{\text{def}} = 0.25$): $\Phi_{\text{PD}} = 2 + 4(0.15)(3)(0.25) = 2.45$. Since the baseline $\Phi = 2.2 < 2.45$, the PD ordering $P > S$ holds. For $\Phi \geq \Phi_{\text{PD}}$, the game transitions to a **Chicken** (Hawk-Dove) structure with $T > R > S > P$: mutual defection becomes *worse* than being the sucker, because the contest dissipation at high friction overwhelms the sucker's one-sided damage. This transition is *favorable* for cooperation: the repeated-game cooperation condition (Theorem 11) becomes easier to satisfy since $T - P$ grows larger, and even the one-shot game admits cooperative mixed-strategy Nash equilibria under the Chicken structure.

**Claim: $S < 0$ (the sucker always loses).**

$$S = -\theta E_R(1 + \kappa)\delta^{\text{def}} < 0$$

since all parameters are positive. The sucker not only fails to obtain the resource but suffers boundary damage from the defector's attack.

> **Proposition 4 (Physical Prisoner's Dilemma).** *Under the energy-based payoff model with physical constraints ($E_R > 0$, $c \ll E_R$, $\theta < (1/2 + c/E_R)/(1 + (1+\kappa)\delta^{\text{off}})$, $1 < \Phi < \Phi_{\text{PD}} = 2 + 4\theta(1+\kappa)\delta^{\text{def}}$), the single-round game has the structure of a Prisoner's Dilemma: $T > R > P > S$.*
>
> *In the single-round game, defection is the dominant strategy for each agent. The unique Nash Equilibrium is $(D, D)$ with payoffs $(P, P)$, even though $(C, C)$ with payoffs $(R, R)$ is Pareto-superior.*

*Proof.* The inequalities $T > R > P > S$ are verified above under the stated parameter conditions. In a simultaneous single-round game:

- If $B$ plays $C$: $A$ prefers $D$ ($T > R$).
- If $B$ plays $D$: $A$ prefers $D$ ($P > S$).

So $D$ strictly dominates $C$ for each player. The unique NE is $(D, D)$. But $R > P$ means both agents prefer $(C, C)$ to $(D, D)$, establishing the Pareto inefficiency of the one-shot equilibrium. $\square$

**Physical interpretation:** In a single, unrepeated encounter, the thermodynamic pressure to exploit creates a trap: each agent's individually rational choice leads to a collectively irrational outcome. This is the "State of Nature" — mathematically unstable and energetically wasteful.

### 2.4 Numerical Illustration: The Baseline Game

**Parameters:** $E_R = 100$, $c = 2$, $\theta = 0.15$, $\delta^{\text{off}} = 0.15$, $\delta^{\text{def}} = 0.25$, $\kappa = 2$.

Computed payoffs:

$$T = 100[1 - 0.15(1 + 3 \times 0.15)] = 100[1 - 0.15 \times 1.45] = 100 \times 0.7825 = 78.25$$

$$R = 50 - 2 = 48$$

$$\Phi = 1 + 3(0.15 + 0.25) = 2.2$$

$$P = 50(1 - 2.2/2) = 50(1 - 1.1) = 50 \times (-0.1) = -5$$

$$S = -0.15 \times 100 \times 3 \times 0.25 = -11.25$$

| | $B: C$ | $B: D$ |
|---|---|---|
| $A: C$ | **(48, 48)** | (−11.25, 78.25) |
| $A: D$ | (78.25, −11.25) | (−5, −5) |

**Observations:**

1. **Mutual defection is net-negative** ($P = -5$): both agents *lose* energy. The conflict destroys more than the resource provides (consistent with Theorem 5, since $\Phi = 2.2 > 2$).
2. **Mutual cooperation yields a large surplus** ($R = 48$ each, system total = 96).
3. **Temptation is high** ($T = 78.25$), but the victim suffers ($S = -11.25$).
4. **The cooperation premium** is $R - P = 48 - (-5) = 53$ per agent — the energy saved by ethical behavior compared to the conflict equilibrium.

---

## 3. The Repeated Game: Cooperation as Equilibrium

### 3.1 Why Repetition Matters

The single-round Prisoner's Dilemma has defection as the unique NE. But entities in the real world — biological organisms, economic agents, nations — interact **repeatedly** over indefinite timeframes. The theory of repeated games [@Fudenberg1986] shows that sustained cooperation can emerge as an equilibrium in the repeated version of the game.

The key parameter is the **discount factor** $\delta \in (0, 1)$, representing how much agents value future payoffs relative to present ones. In our thermodynamic framework, $\delta$ has a natural physical interpretation:

> **Definition 20 (Discount Factor).** The discount factor $\delta$ for an agent with planning horizon $T$ (periods) and per-period survival probability $\sigma \in (0, 1]$ is:
>
> $$\delta = \sigma \cdot e^{-r}$$
>
> where $r \geq 0$ is the time-preference rate. For entities optimizing over long horizons (high $\sigma$, low $r$), $\delta \to 1$. For entities with short horizons (low $\sigma$ or high $r$), $\delta \to 0$.

**Physical interpretation:** $\delta$ close to 1 means the agent expects to interact many more times and therefore cares about its reputation and the future state of the network. $\delta$ close to 0 means the agent has a short horizon ("live fast, die young") and underweights future consequences. An agent with an infinite-timeline belief (afterlife, legacy) effectively has $\delta \to 1$; this is formalized in §7 below.

### 3.2 Trigger Strategies: Grim and Tit-for-Tat

The simplest mechanism to sustain cooperation in repeated games is a **trigger strategy** — a rule that starts cooperating and retaliates against defection.

> **Definition 21 (Grim Trigger).** Agent $i$ plays $C$ in every period as long as no agent has ever played $D$. If any defection occurs, agent $i$ plays $D$ forever.

> **Definition 22 (Tit-for-Tat, TFT).** Agent $i$ plays $C$ in period 1. In period $t > 1$, agent $i$ plays whatever the opponent played in period $t - 1$.

Both strategies embody a simple enforcement mechanism: cooperation is maintained as long as agents observe cooperation; defection triggers retaliation. The threat of retaliation — sustained loss of cooperative payoffs — creates a cost to defection that extends beyond the single interaction.

### 3.3 The Cooperation Condition (Grim Trigger)

Under the grim trigger strategy, the following holds:

> **Theorem 11 (Cooperation as Nash Equilibrium — The Ethics Theorem).**
>
> *In the infinitely repeated energy-based game with discount factor $\delta$, the cooperative outcome $(C, C)$ in every period is sustainable as a Nash Equilibrium (under grim trigger) if and only if:*
>
> $$\delta \geq \frac{T - R}{T - P} = \delta^*$$
>
> *where $T$, $R$, $P$ are the temptation, reward, and punishment payoffs. The critical discount factor $\delta^*$ has the physical interpretation: cooperation is sustainable when agents sufficiently value future interactions.*

*Proof.* Consider agent $A$'s incentive to deviate from the cooperative profile $(C, C, C, \ldots)$.

**Payoff from continued cooperation:**

$$V_A^{\text{coop}} = R + \delta R + \delta^2 R + \cdots = \frac{R}{1 - \delta}$$

**Payoff from one-shot defection (then punished forever):**

The deviating agent gets $T$ in the current period, then $(D, D)$ forever:

$$V_A^{\text{deviate}} = T + \delta P + \delta^2 P + \cdots = T + \frac{\delta P}{1 - \delta}$$

Cooperation is incentive-compatible when $V_A^{\text{coop}} \geq V_A^{\text{deviate}}$:

$$\frac{R}{1 - \delta} \geq T + \frac{\delta P}{1 - \delta}$$

$$R \geq (1 - \delta) T + \delta P$$

$$R - P \geq (1 - \delta)(T - P)$$

$$\frac{R - P}{T - P} \geq 1 - \delta$$

$$\delta \geq 1 - \frac{R - P}{T - P} = \frac{T - R}{T - P}$$

Since both agents face the same calculation (the game is symmetric), $(C, C)$ sustained by grim trigger is a NE whenever $\delta \geq \delta^*$. $\square$

### 3.4 Computing $\delta^*$ Under Physical Constraints

Using the energy-based payoffs from §2.3:

$$\delta^* = \frac{T - R}{T - P}$$

**Baseline numerical example** (§2.4 parameters):

$$\delta^* = \frac{78.25 - 48}{78.25 - (-5)} = \frac{30.25}{83.25} = 0.3634$$

> **Corollary 11.1 (Low Cooperation Threshold).** *Under the physical payoff model with $\Phi > 2$ (net-negative mutual defection), the critical discount factor satisfies $\delta^* < 0.5$. Agents need only value the future at more than 36% of the present to sustain cooperation.*

*Proof.* When $P < 0$ (which occurs for $\Phi > 2$, per §2.4):

$$T - P = T + |P| > T$$

$$\delta^* = \frac{T - R}{T - P} < \frac{T - R}{T} = 1 - \frac{R}{T}$$

It remains to show $R > T/2$, i.e., $1 - R/T < 0.5$. Substituting the payoff expressions from §2.3, $R = E_R/2 - c$ and $T = E_R[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})]$, the condition $R > T/2$ reduces to:

$$c < \frac{\theta E_R}{2}\bigl(1 + (1+\kappa)\delta^{\text{off}}\bigr)$$

This holds whenever the exploitation overhead exceeds twice the coordination cost — a condition satisfied for any non-trivial $\theta$, since the PD ordering already requires $c \ll E_R$. For the baseline values ($c = 2$, $\theta = 0.15$, $E_R = 100$, $\kappa = 2$, $\delta^{\text{off}} = 0.15$): the right side is $0.15 \times 100 \times 1.45 / 2 = 10.875 \gg 2 = c$, and $R/T = 48/78.25 = 0.614 > 0.5$, giving $\delta^* < 1 - 0.614 = 0.386 < 0.5$. $\square$

**Physical interpretation:** Because mutual defection under physical energy payoffs is net-negative ($P < 0$), the punishment for defection is **automatically severe** — agents don't just earn less, they actively *lose* energy. This makes cooperation easy to sustain: even agents with modest foresight ($\delta > 0.36$) find it in their interest to cooperate. Compare this with the abstract PD (e.g., $T=5, R=3, P=1, S=0$) where $\delta^* = 0.5$ — physical constraints make cooperation **more** accessible, not less.

### 3.5 Sensitivity Analysis: $\delta^*$ Across Parameter Regimes

| Regime | $\Phi$ | $\theta$ | $T$ | $R$ | $P$ | $S$ | $\delta^*$ |
|---|---|---|---|---|---|---|---|
| Low friction ($\Phi=1.0$) | 1.0 | 0.15 | 78.25 | 48 | 25 | −11.25 | 0.568 |
| Moderate ($\Phi=1.5$) | 1.5 | 0.15 | 78.25 | 48 | 12.5 | −11.25 | 0.460 |
| **Baseline** ($\Phi=2.2$) | 2.2 | 0.15 | 78.25 | 48 | −5 | −11.25 | **0.363** |
| High friction ($\Phi=3.0$) | 3.0 | 0.15 | 78.25 | 48 | −25 | −11.25 | 0.293 |
| Very high ($\Phi=4.0$) | 4.0 | 0.15 | 78.25 | 48 | −50 | −11.25 | 0.236 |
| Cheap exploit ($\theta=0.05$) | 2.2 | 0.05 | 92.75 | 48 | −5 | −3.75 | 0.458 |
| Expensive exploit ($\theta=0.30$) | 2.2 | 0.30 | 56.50 | 48 | −5 | −22.50 | 0.138 |

> **Note on game type.** Rows with $\Phi \geq \Phi_{\text{PD}}$ (High friction, Very high) and rows where $\theta$ is small enough that $P < S$ (Cheap exploit, where $\Phi_{\text{PD}} = 2 + 4(0.05)(3)(0.25) = 2.15 < 2.2$) are Chicken games ($T > R > S > P$), not Prisoner's Dilemmas. The cooperation threshold formula $\delta^* = (T - R)/(T - P)$ and all subsequent theorems apply identically to both game structures; the Chicken structure actually yields a *lower* $\delta^*$ because $T - P$ is larger.

**Key findings:**

1. **Higher friction → lower $\delta^*$ → easier cooperation.** When conflict is more destructive, the "punishment" for mutual defection is harsher, making cooperation sustainable even for short-sighted agents.
2. **Higher exploitation cost → lower $\delta^*$.** When defection is expensive (well-defended targets), the temptation premium shrinks and cooperation is easier.
3. **In all physical regimes, $\delta^* < 0.6$.** Cooperation is sustainable for any agent that values future interactions at more than ~60% of present ones — a modest requirement.

---

## 4. Network Effects: The Friction Amplifier

### 4.1 Incorporating Network Friction into Payoffs

The single-interaction payoffs above omit a crucial physical cost: defection injects friction into the network (thermodynamic friction derivation, §7), degrading all future cooperative transactions. This makes defection costlier than the single-round analysis suggests.

> **Definition 23 (Network-Adjusted Payoffs).** Let $\phi_t$ be the network friction at time $t$. An agent's effective per-period payoff from cooperation is:
>
> $$R_{\text{net}}(\phi_t) = R - \phi_t \cdot \bar{E}$$
>
> Defection in period $t$ injects friction $\Delta\phi = \eta \cdot v$ (Definition 9), where $v$ is the violation severity. The defector's effective payoff in the defection period is $T$ (the attack profit), but all future cooperative payoffs for both agents are degraded by the cascading friction.

### 4.2 The Full Defection Cost

Over the infinite horizon, the total cost of a single defection (beyond the immediate payoff shift) includes the cascading friction (Theorem 7):

$$C_{\text{cascade}} = \frac{\eta \cdot v \cdot M \cdot \bar{E}}{\epsilon}$$

This cost is distributed across all $M$ transactions and all agents in the network. The fraction borne by the defecting agent (through degraded future cooperative payoffs) is:

$$C_{\text{defector}}^{\text{cascade}} = \frac{C_{\text{cascade}}}{N} = \frac{\eta \cdot v \cdot M \cdot \bar{E}}{N \cdot \epsilon}$$

> **Theorem 12 (Network-Adjusted Cooperation Condition).**
>
> *When network friction effects are included, the effective punishment payoff becomes:*
>
> $$\tilde{P} = P - \frac{C_{\text{defector}}^{\text{cascade}}}{(1/\epsilon)} = P - \frac{\eta \cdot v \cdot M \cdot \bar{E}}{N}$$
>
> *(amortized over the recovery time horizon). The network-adjusted critical discount factor is:*
>
> $$\tilde{\delta}^* = \frac{T - R}{T - \tilde{P}} < \delta^*$$
>
> *Network friction makes cooperation strictly easier to sustain.*

*Proof.* Since the cascading friction is a real energy cost borne by the defector (via degraded future cooperative opportunities), and $C_{\text{defector}}^{\text{cascade}} > 0$, we have $\tilde{P} < P$. Therefore $T - \tilde{P} > T - P$, and:

$$\tilde{\delta}^* = \frac{T - R}{T - \tilde{P}} < \frac{T - R}{T - P} = \delta^*$$

$\square$

### 4.3 Numerical Illustration

For the violation severity we set $v = E_R$, the per-interaction resource pool. This represents a full-violation baseline: a defector who appropriates the counterpart's entire resource share causes harm equal to $E_R$. This is the natural unit for energy-denominated violations, and the bound $v \leq E_R$ follows from resource conservation (a single interaction cannot extract more than $E_R$ from the system). The numerical results scale linearly with $v$; smaller violations reduce $C_{\text{cascade}}$ proportionally.

Using baseline parameters ($E_R = 100$, $M = 1000$, $\bar{E} = 10$, $\eta = 0.01$, $v = E_R = 100$, $N = 100$, $\epsilon = 0.05$):

$$C_{\text{defector}}^{\text{cascade}} = \frac{0.01 \times 100 \times 1000 \times 10}{100 \times 0.05} = \frac{10{,}000}{5} = 2{,}000$$

Amortized over the recovery period ($\sim 1/\epsilon = 20$ periods):

$$\tilde{P}_{\text{per period}} \approx P - 2000/20 = -5 - 100 = -105$$

$$\tilde{\delta}^* = \frac{78.25 - 48}{78.25 - (-105)} = \frac{30.25}{183.25} = 0.165$$

**With network friction, the cooperation threshold drops to $\tilde{\delta}^* = 0.165$.** Even extremely short-sighted agents find cooperation rational when the network punishes defection through friction cascades.

### 4.4 Deception Penalties

Defection via deception (lies, fraud) rather than overt conflict incurs the micro-friction costs from the information-entropy derivation:

- Decision cost to the victim: $\Delta U_B(q)$ (Theorem 8)
- Verification overhead on the network: $\Delta W(q)$ (Theorem 9)
- Deception-induced friction: $\Delta\phi_{\text{info}} = \eta_{\text{info}} \cdot \Delta H \cdot W_{\text{bit}}$ (Definition 17)

These costs further increase the effective punishment and reduce $\tilde{\delta}^*$. The deception channel does not create a "cheaper" form of defection — it incurs different but equally real thermodynamic costs.

---

## 5. Extension to $N$-Player Games

### 5.1 The $N$-Player Public Goods Game

To extend beyond two players, consider the canonical $N$-player interaction: a **public goods game** with energy-denominated payoffs.

> **Definition 24 ($N$-Player Energy Public Goods Game).** $N$ agents each choose whether to Cooperate ($C$: contribute energy $c_i > 0$ to a shared pool) or Defect ($D$: contribute nothing). The shared pool generates a return multiplied by factor $\alpha > 1$ (the efficiency gain from cooperation) and is distributed equally. Agent $i$'s payoff:
>
> $$\pi_i = \frac{\alpha \sum_{j=1}^{N} c_j \cdot \mathbb{1}[j \text{ cooperates}]}{N} - c_i \cdot \mathbb{1}[i \text{ cooperates}] - \phi \cdot \bar{E} \cdot \frac{N - n_C}{N}$$
>
> where $n_C$ is the number of cooperators and the last term captures the friction tax from defectors (proportional to the defection rate).

In our framework, $\alpha$ is the **cooperative multiplier** — the ratio of total output under cooperation to total input. This is derived from the Lagrangian constraints result that the variational equilibrium allocates resources more efficiently than the unconstrained regime.

More concretely, when all $N$ agents cooperate, each contributes $c$ and receives $\alpha c$ (net gain $(\alpha - 1)c$). When $n_C < N$ agents cooperate, the cooperators pay the coordination cost while defectors free-ride, but the system suffers friction loss.

### 5.2 The One-Shot $N$-Player Equilibrium

In the single-round game, defection is dominant when:

$$\frac{\alpha c}{N} < c \iff \alpha < N$$

That is, defection dominates when the cooperative return to each individual is less than the individual's contribution — the standard free-rider problem. For large $N$, this holds unless $\alpha$ is very large.

The one-shot NE is universal defection, yielding payoff $\pi_i^{DD} = -\phi_0 \bar{E}$ (only the friction tax from the non-cooperative environment). The cooperative payoff is $\pi_i^{CC} = (\alpha - 1)c$. The efficiency loss is:

$$\Delta\pi = (\alpha - 1)c + \phi_0 \bar{E} > 0$$

### 5.3 The Repeated $N$-Player Game

> **Theorem 13 (N-Player Cooperation Sustainability).**
>
> *In the infinitely repeated $N$-player energy public goods game with discount factor $\delta$ and grim trigger punishment (all agents defect forever upon any defection), cooperation is a NE if:*
>
> $$\delta \geq \delta_N^* = \frac{\pi_i^{\text{deviate}} - \pi_i^{CC}}{\pi_i^{\text{deviate}} - \pi_i^{DD}}$$
>
> *where $\pi_i^{\text{deviate}}$ is agent $i$'s payoff from unilaterally defecting while all others cooperate:*
>
> $$\pi_i^{\text{deviate}} = \frac{\alpha (N-1) c}{N} - 0 = \frac{\alpha(N-1)c}{N}$$
>
> *(receives the public good without contributing). The critical discount factor is:*
>
> $$\delta_N^* = \frac{\frac{\alpha(N-1)c}{N} - (\alpha - 1)c}{\frac{\alpha(N-1)c}{N} + \phi_0 \bar{E}} = \frac{c(N - \alpha)}{(N-1)\alpha c + N\phi_0\bar{E}}$$

*Proof.* The deviation payoff is $\pi_i^{\text{deviate}} = \alpha(N-1)c/N$ (receives share of the $(N-1)$ cooperators' contributions without paying). The cooperative payoff is $\pi_i^{CC} = \alpha c - c = (\alpha-1)c$. The punishment payoff is $\pi_i^{DD} = -\phi_0\bar{E}$ (universal defection with friction tax). Applying the grim trigger calculation:

$$\delta_N^* = \frac{\pi_i^{\text{deviate}} - \pi_i^{CC}}{\pi_i^{\text{deviate}} - \pi_i^{DD}} = \frac{\alpha(N-1)c/N - (\alpha-1)c}{\alpha(N-1)c/N + \phi_0\bar{E}}$$

Simplifying the numerator:

$$\frac{\alpha(N-1)c - N(\alpha-1)c}{N} = \frac{c[\alpha N - \alpha - \alpha N + N]}{N} = \frac{c(N - \alpha)}{N}$$

So:

$$\delta_N^* = \frac{c(N - \alpha)/N}{\alpha(N-1)c/N + \phi_0\bar{E}} = \frac{c(N-\alpha)}{\alpha(N-1)c + N\phi_0\bar{E}}$$

$\square$

*Remark:* The deviation payoff above omits the friction tax $\phi_0\bar{E}/N$ that Definition 24 imposes on all agents, including the deviator, in the defection round. Including this term yields the corrected threshold $\delta_N^{*,\text{corr}} = [c(N-\alpha) - \phi_0\bar{E}] / [(N-1)(\alpha c + \phi_0\bar{E})]$, which is strictly smaller than the stated $\delta_N^*$. The omission is thus conservative: cooperation is achievable for any $\delta \geq \delta_N^*$ per the theorem, and in fact for the strictly smaller $\delta_N^{*,\text{corr}}$ as well. All qualitative conclusions — cooperation scales with $N$, friction lowers the threshold — are strengthened rather than weakened.

### 5.4 Properties of $\delta_N^*$

> **Corollary 13.1 (Cooperation Strengthens with Network Friction).**
>
> $$\frac{\partial \delta_N^*}{\partial \phi_0} < 0$$
>
> *Higher network friction (harsher punishment for the all-defect state) makes cooperation easier to sustain.*

*Proof.* The numerator $c(N - \alpha)$ does not depend on $\phi_0$. The denominator $\alpha(N-1)c + N\phi_0\bar{E}$ is strictly increasing in $\phi_0$. Therefore $\delta_N^*$ is strictly decreasing in $\phi_0$. $\square$

> **Corollary 13.2 (Cooperation Strengthens with Scale Under Friction).**
>
> *When friction is non-negligible ($\phi_0 > 0$), the critical discount factor $\delta_N^*$ remains bounded (does not approach 1) as $N \to \infty$:*
>
> $$\lim_{N \to \infty} \delta_N^* = \frac{c}{\alpha c + \phi_0 \bar{E}} < 1$$

*Proof.* Dividing numerator and denominator by $N$:

$$\delta_N^* = \frac{c(1 - \alpha/N)}{\alpha(1 - 1/N)c + \phi_0\bar{E}} \xrightarrow{N \to \infty} \frac{c}{\alpha c + \phi_0\bar{E}}$$

Since $\phi_0 > 0$: $\alpha c + \phi_0\bar{E} > c$ (for $\alpha > 1$ or $\phi_0 > 0$), so the limit is strictly less than 1. $\square$

**Physical interpretation:** In classical game theory (abstract payoffs, no friction), the critical discount factor for $N$-player public goods games approaches 1 as $N \to \infty$ — cooperation becomes unsustainable in large groups. With energy-based payoffs and network friction, this pathology **disappears**: the friction penalty of universal defection grows with group size, keeping cooperation accessible even in large populations. This is the formal proof that the cooperative equilibrium holds and strengthens as the network scales.

### 5.5 Numerical Illustration: $N$-Player Cooperation Thresholds

**Parameters:** $c = 10$, $\alpha = 2$ (cooperative doubling), $\phi_0 = 0.5$ (moderate background friction), $\bar{E} = 10$.

| $N$ | Deviation gain $\pi^{\text{dev}} - \pi^{CC}$ | Punishment gap $\pi^{\text{dev}} - \pi^{DD}$ | $\delta_N^*$ |
|---|---|---|---|
| 2 | 0 | 10 + 5 = 15 | 0.000 |
| 3 | 3.33 | 13.33 + 5 = 18.33 | 0.182 |
| 5 | 6.00 | 16 + 5 = 21 | 0.286 |
| 10 | 8.00 | 18 + 5 = 23 | 0.348 |
| 50 | 9.60 | 19.6 + 5 = 24.6 | 0.390 |
| 100 | 9.80 | 19.8 + 5 = 24.8 | 0.395 |
| $\infty$ | 10.00 | 20 + 5 = 25 | 0.400 |

**Key result:** Even as $N \to \infty$, $\delta_N^*$ converges to 0.4, well below 1. Cooperation remains a Nash Equilibrium for any agent with $\delta \geq 0.4$. Without friction ($\phi_0 = 0$), $\delta_N^*$ for $N = 100$ would be $9.8/19.8 = 0.495$, and for $N \to \infty$ it would approach $10/20 = 0.5$. Friction provides the extra margin that makes cooperation robust.

---

## 6. Evolutionary Stability: Defection Cannot Invade

### 6.1 The Evolutionary Game-Theoretic Framework

Beyond asking whether cooperation is a NE, we ask: **can defection invade a cooperative population?** This is the evolutionary stability question [@MaynardSmith1973].

> **Definition 25 (Evolutionary Stable Strategy, ESS).** A strategy $s^*$ is an ESS if, for any mutant strategy $s' \neq s^*$:
>
> (a) $\pi(s^*, s^*) > \pi(s', s^*)$ (**strict NE**), or
>
> (b) $\pi(s^*, s^*) = \pi(s', s^*)$ and $\pi(s^*, s') > \pi(s', s')$ (**stability condition**).

### 6.2 TFT as an Approximate ESS

In the iterated Prisoner's Dilemma with energy payoffs, Tit-for-Tat (TFT) is a well-known strong performer [@Axelrod1984]. While TFT is not a strict ESS in the technical sense (it does not strictly outperform other "nice" strategies like Always-Cooperate in a homogeneous population), it satisfies a strong **invasion barrier** condition:

> **Theorem 14 (Defection Invasion Barrier).**
>
> *In a population of $N$ TFT-playing agents with discount factor $\delta > \delta^*$, a mutant Always-Defect (ALLD) agent earns:*
>
> $$V_{\text{ALLD}} = T + \frac{\delta P}{1 - \delta}$$
>
> *while a TFT agent in the same population earns:*
>
> $$V_{\text{TFT}} = \frac{R}{1 - \delta}$$
>
> *The ALLD mutant is strictly dominated ($V_{\text{ALLD}} < V_{\text{TFT}}$) when:*
>
> $$\delta > \frac{T - R}{T - P} = \delta^*$$
>
> *Under the physical payoff model with $\Phi > 2$, this holds for all $\delta > 0.363$ (baseline parameters).*

*Proof.* An ALLD mutant, upon meeting a TFT agent, defects in round 1 (getting $T$) and then faces retaliation: mutual defection from round 2 onward (getting $P$ each round). Its lifetime payoff against any TFT agent is:

$$V_{\text{ALLD}} = T + \delta P + \delta^2 P + \cdots = T + \frac{\delta P}{1 - \delta}$$

A TFT agent meeting other TFT agents cooperates every round:

$$V_{\text{TFT}} = R + \delta R + \delta^2 R + \cdots = \frac{R}{1 - \delta}$$

Then $V_{\text{TFT}} > V_{\text{ALLD}}$:

$$\frac{R}{1 - \delta} > T + \frac{\delta P}{1 - \delta}$$

$$R > (1 - \delta)T + \delta P$$

$$\delta > \frac{T - R}{T - P} = \delta^*$$

which is exactly the cooperation condition from Theorem 11. $\square$

**Physical interpretation:** A defector entering a cooperative population gets one "hit" (the temptation payoff $T$) and then finds itself in perpetual mutual defection — which, under physical payoffs, means perpetual net-negative returns ($P < 0$). The defector's strategy is self-defeating: it destroys the cooperative environment it needs to profit from. In evolutionary terms, the "invasion fitness" of defection is negative in a cooperative ecology.

### 6.3 The Defector's Dilemma: Extinction Through Friction

Beyond the direct retaliation mechanism, the defector also faces the cascading friction cost (§4). Even if a defector can avoid direct retaliation (e.g., in a large anonymous population), each defection increases the network friction $\phi$, which degrades the returns to *all* agents — including the defector. In a population where the defector's payoff depends on the cooperative surplus (because even defectors benefit from a low-friction network for their non-defection interactions), systematic defection is a self-undermining strategy.

> **Corollary 14.1 (Defection Self-Extinction in Friction Environments).** *In a network with friction coupling, a defector whose defection rate $\nu_D$ injects enough friction to push $\phi$ above the network collapse threshold (Corollary 7.1) destroys the cooperative surplus from which it profits. In the limit, a population of defectors achieves the minimum network payoff $\pi^{DD} = -\phi_0 \bar{E}$, which is strictly less than zero. Defection is not merely dominated — it is self-destructive.*

---

## 7. The Altruism Matrix: Game-Theoretic Foundation

### 7.1 Connecting to the Paper's Framework

The paper (§5.6) identifies four mechanisms explaining altruism. We now provide the game-theoretic formalization for each.

### 7.2 Mechanism A: Inclusive Fitness as Extended Payoffs

In biological systems, an agent's "identity" extends to genetically related individuals [@Hamilton1964a]. We model this by augmenting the payoff function:

> **Definition 26 (Inclusive Fitness Payoff).** Agent $i$'s inclusive payoff is:
>
> $$\Pi_i^{\text{incl}} = \pi_i + \sum_{j \neq i} r_{ij} \, \pi_j$$
>
> where $r_{ij} \in [0, 1]$ is the **relatedness coefficient** between agents $i$ and $j$ (probability of shared genetic identity at a random locus).

For a standard diploid organism: $r_{\text{parent-child}} = 0.5$, $r_{\text{siblings}} = 0.5$, $r_{\text{cousins}} = 0.125$.

**Hamilton's Rule in energy terms:** Agent $i$ will sacrifice personal payoff $\pi_i = -C$ if the benefit to relative $j$ satisfies $r_{ij} \cdot B > C$, where $B$ is the benefit (in energy units) to agent $j$. This is a standard optimization: maximize the inclusive payoff $\Pi_i^{\text{incl}} = -C + r_{ij} B \geq 0$.

### 7.3 Mechanism B: Infinite Horizon (Belief-Extended $\delta$)

If an agent believes its identity persists beyond physical death, its effective discount factor approaches 1:

$$\delta_{\text{believer}} = 1 - \epsilon_{\text{belief}} \approx 1$$

where $\epsilon_{\text{belief}} \to 0$ reflects the agent's confidence in post-mortem persistence. Under Theorem 11, any $\delta > \delta^*$ sustains cooperation. For $\delta \to 1$, not only is cooperation sustained but the agent is willing to accept **any** finite short-term cost for long-term cooperative benefit: self-sacrifice becomes "rational" under the agent's model of reality.

### 7.4 Mechanism C: Coupled Systems (Merged Boundaries)

When two agents merge boundaries (parent-child, spouses), they effectively become a single agent with a joint utility function:

$$U_{AB}(\mathbf{x}_A, \mathbf{x}_B) = w_A U_A(\mathbf{x}_A) + w_B U_B(\mathbf{x}_B)$$

where $w_A, w_B > 0$ are the coupling weights. The "self-sacrifice" of agent $A$ for agent $B$ is reinterpreted as internal resource reallocation within the merged system — the macro-entity $AB$ optimizes its *joint* boundary, shedding a component to save a more vital one.

### 7.5 Mechanism D: Heuristic Over-Extension (Generalized Relatedness)

The empathy heuristic effectively inflates the perceived relatedness coefficient:

$$\hat{r}_{ij} = r_{ij} + \epsilon_{\text{empathy}} > r_{ij}$$

where $\epsilon_{\text{empathy}} \geq 0$ is the over-extension term generated by the agent's abstract-reasoning capacity. When $\hat{r}_{ij}$ is large enough, Hamilton's Rule triggers even for unrelated strangers: $\hat{r}_{ij} B > C$ can hold even when $r_{ij} = 0$.

### 7.6 Unified Formalization

All four mechanisms operate by expanding the agent's **effective payoff function** to internalize some fraction of other agents' payoffs:

$$\Pi_i^{\text{eff}} = \pi_i + \sum_{j \neq i} w_{ij} \pi_j$$

where the weights $w_{ij}$ are determined by:

| Mechanism | Source of $w_{ij}$ |
|---|---|
| A. Inclusive fitness | Genetic relatedness $r_{ij}$ |
| B. Infinite horizon | Discount factor $\delta \to 1$ (via repeated-game embedding) |
| C. Coupled systems | Boundary merger weights $w_A, w_B$ |
| D. Heuristic over-extension | Empathic projection $\hat{r}_{ij}$ |

In each case, the agent is still maximizing its **own** (extended) payoff — altruism is *selfish optimization over an expanded utility function*, as the framework predicts.

---

## 8. Tit-for-Tat Dynamics in Energy Terms

### 8.1 Short-Term Defection Profit is Erasure

We now formally show that a defector's short-term energy gain is **wiped out** over repeated interactions.

> **Theorem 15 (Defection Profit Erasure).**
>
> *An agent that defects once against a TFT population and then returns to cooperation incurs a net lifetime loss whenever:*
>
> $$\delta > \frac{T - R}{R - S}$$
>
> *(without friction). Under the physical payoff model (baseline parameters), the basic threshold is $\delta = 0.511$. When network friction costs are included ($F = 100$ per period over 20 recovery periods), the threshold drops to $\delta \approx 0.17$.*

*Proof.* Consider an agent that defects in period $t$ (getting $T$), is retaliated against in period $t+1$ (getting $S$), and then both agents return to cooperation from period $t+2$ onward. The deviation costs the agent:

- Period $t$: gains $T$ instead of $R$ (net gain: $T - R$)
- Period $t+1$: earns $S$ instead of $R$ (net loss: $R - S$)
- Periods $t+2, \ldots$: back to $R$ (no change)

Present-value net gain from the one-shot deviation:

$$\Delta V = (T - R) - \delta(R - S)$$

The deviation is unprofitable ($\Delta V < 0$) when:

$$\delta > \frac{T - R}{R - S}$$

With baseline parameters: $\delta > (78.25 - 48)/(48 - (-11.25)) = 30.25/59.25 = 0.511$.

However, this analysis ignores the network friction cost. Including the per-period friction penalty amortized over recovery time ($\sim 1/\epsilon = 20$ periods), even a single defection imposes a sustained future cost. From §4.3, the per-defector cascade cost is $C_{\text{defector}}^{\text{cascade}} = 2{,}000$, giving $F = 2{,}000 / 20 = 100$ energy units per period of degraded cooperative returns. When we include this:

$$\Delta V_{\text{adj}} = (T - R) - \delta(R - S) - \delta \sum_{k=1}^{1/\epsilon} \delta^{k-1} F$$

This makes the defection-erasure threshold strictly lower than $\delta = 0.511$:

$$\frac{T - R}{R - S + \delta F/(1-\delta)} < \frac{T - R}{R - S}$$

Numerically, the condition $\Delta V_{\text{adj}} < 0$ holds for $\delta \gtrsim 0.17$ after including friction. $\square$

**Physical interpretation:** The defector's profit ($T - R = 30.25$) is a one-time energy windfall. The retaliation cost ($R - S = 59.25$) comes one period later. The friction cost ($F = 100$/period) compounds over $\sim 20$ periods. For any agent that expects to survive more than a few interactions ($\delta > 0.17$), the short-term defection profit is negative on net. Defection is an energetic "payday loan" with ruinous interest.

---

## 9. System-Level Optimality: The Welfare Theorem

### 9.1 The Social Welfare Function

Define the **system welfare** as the total energy available to all agents for Identity Preservation:

$$SW = \sum_{i=1}^{N} \pi_i - \mathcal{C}_{\text{total}}$$

where $\mathcal{C}_{\text{total}}$ is the total interaction cost (Definition 11 plus Definition 18).

### 9.2 The Maximum Welfare Theorem

> **Theorem 16 (Cooperation Maximizes System Welfare).**
>
> *Among all strategy profiles in the repeated $N$-player game, the cooperative profile ($C$ for all agents in all periods) uniquely maximizes the per-period system welfare:*
>
> $$SW^{CC} = N(\alpha - 1)c \geq SW^{s} \quad \forall \text{ strategy profiles } s$$
>
> *with equality only when $s$ is also universally cooperative.*

*Proof.* Under universal cooperation:
- Total resource input: $Nc$ (all agents contribute)
- Total output: $\alpha N c$ (cooperative multiplier)
- Net welfare: $N(\alpha - 1)c$
- Interaction cost: $\mathcal{C}_{\text{total}} = 0$ (no conflict, no deception, $\phi = 0$)

Under any profile with $n_D > 0$ defectors:
- Resource input: $(N - n_D)c < Nc$ (defectors don't contribute)
- Output: $\alpha(N - n_D)c < \alpha Nc$ (reduced by lost contributions)
- Network friction tax: $\phi \cdot M \cdot \bar{E} > 0$ (deviators bear friction penalty)
- Net welfare: strictly less than $N(\alpha - 1)c$

Formally:

$$SW^{CC} - SW^{s} = \underbrace{n_D (\alpha - 1)c}_{\text{lost contributions}} + \underbrace{\phi(s) M \bar{E}}_{\text{friction tax}} > 0$$

for any $s$ with $n_D > 0$. Uniqueness follows from the strict inequality above: for any strategy profile with $n_D \geq 1$ defectors, the lost-contributions term $n_D(\alpha - 1)c > 0$ ensures that no defecting profile achieves $SW^{CC}$. (*Note: The Tullock contest dissipation term $D(s)$ applies to arms-race conflict settings — see thermodynamic friction derivation, §3, Proposition 2 — and does not apply in this public goods free-rider context; uniqueness here rests solely on the lost-contributions and friction-tax terms.*) $\square$

### 9.3 The System-Level Nash Equilibrium

Combining Theorems 11 and 16:

> **Corollary 16.1 (Ethics as the Unique Efficient Nash Equilibrium).**
>
> *In the infinitely repeated energy-based game with $\delta > \delta^*$:*
>
> *(a) Universal cooperation is a Nash Equilibrium (Theorem 11).*
>
> *(b) Universal cooperation uniquely maximizes system welfare (Theorem 16).*
>
> *(c) Universal cooperation minimizes total interaction cost ($\mathcal{C}_{\text{total}} = 0$).*
>
> *Therefore, the cooperative strategy profile ("ethics") is the unique Nash Equilibrium that is also Pareto-optimal and system-welfare-maximizing.*

**Physical interpretation:** This is the central result of the paper — the formal proof that *"Ethics is the objectively measurable, mathematically optimal algorithm for maximizing the Identity Preservation of the maximum number of entities within a closed system."* The "optimization" is not hypothetical; it is the standard Nash equilibrium selection criterion applied to energy-denominated payoffs under physical constraints.

---

## 10. Cross-Scale Application (Preview)

### 10.1 Why Scale Matters

The preceding analysis assumes agents of comparable scale. A natural question arises: does the equilibrium hold when agents differ vastly in scale (ant vs. human vs. AGI)?

The answer is affirmative, but the argument rests on the **Accumulated Negentropy** concept (developed in the negentropy derivation). The key insight: in the energy-based payoff model, a super-entity's temptation payoff $T$ from exploiting smaller entities is bounded by the physical cost of exploitation (the contest dissipation costs from Theorem 5 and Corollary 5.3 of the thermodynamic friction derivation), while the smaller entities' collective accumulated negentropy represents an irreplaceable informational asset whose destruction leaves the super-entity worse off.

The formal cross-scale proof is completed in the negentropy derivation. The $N$-player results (§5) apply directly: the super-entity is one agent, the smaller entities are $N - 1$ agents, and the cooperative multiplier $\alpha$ captures the generative value of the information-dense biosphere.

---

## 11. Summary of Results

| # | Result | Statement | Significance |
|---|---|---|---|
| **P4** | Physical PD | $T > R > P > S$ under energy payoffs with $\Phi > 1$ | Single-round defection is tempting but destructive |
| **T11** | Ethics Theorem | Cooperation is NE for $\delta \geq \delta^* = (T-R)/(T-P)$ | Cooperation emerges from physical structure |
| **C11.1** | Low Threshold | $\delta^* < 0.5$ when $\Phi > 2$ | Physical payoffs make cooperation easy to sustain |
| **T12** | Network Adjustment | $\tilde{\delta}^* < \delta^*$ with friction cascades | Network coupling reinforces cooperation |
| **T13** | $N$-Player | $\delta_N^*$ bounded below 1 even as $N \to \infty$ | Cooperation scales to large populations |
| **C13.1** | Friction Robustness | $\partial \delta_N^*/\partial \phi_0 < 0$ | More friction → easier cooperation |
| **C13.2** | Scale Robustness | $\lim_{N \to \infty} \delta_N^* < 1$ under friction | No large-$N$ cooperation breakdown |
| **T14** | Invasion Barrier | ALLD cannot invade TFT population for $\delta > \delta^*$ | Defection is evolutionarily unstable |
| **C14.1** | Defection Self-Extinction | Systematic defection destroys cooperative surplus | Defection is self-undermining |
| **T15** | Profit Erasure | One-shot defection profit erased for $\delta > 0.17$ (with friction) | Short-term gains wiped by long-term costs |
| **T16** | Maximum Welfare | Cooperation uniquely maximizes $SW = \sum \pi_i - \mathcal{C}$ | Ethics is the system-welfare-maximizing strategy |
| **C16.1** | Central Result | Cooperation is the unique efficient NE | Ethics ≡ mathematically optimal algorithm |

---

## 12. Notation Index

| Symbol | Meaning |
|---|---|
| $E_R$ | Energy value of contested resource |
| $c$ | Coordination/trade cost per agent |
| $\theta$ | Exploitation efficiency (cost to defect against cooperator) |
| $T, R, P, S$ | Temptation, Reward, Punishment, Sucker payoffs |
| $\delta$ | Discount factor (value of future relative to present) |
| $\sigma$ | Per-period survival probability |
| $r$ | Time-preference rate |
| $\delta^*$ | Critical discount factor for cooperation |
| $\tilde{\delta}^*$ | Network-adjusted critical discount factor |
| $\delta_N^*$ | $N$-player critical discount factor |
| $\Phi_{\text{PD}}$ | Maximum friction multiplier for PD structure: $2 + 4\theta(1+\kappa)\delta^{\text{def}}$ |
| $\alpha$ | Cooperative multiplier (efficiency gain from cooperation) |
| $n_C$ | Number of cooperating agents |
| $n_D$ | Number of defecting agents |
| $r_{ij}$ | Relatedness coefficient between agents $i$ and $j$ |
| $w_{ij}$ | Effective payoff coupling weight |
| $\Pi_i^{\text{incl}}$ | Inclusive fitness payoff |
| $\Pi_i^{\text{eff}}$ | Effective (extended) payoff |
| $SW$ | System welfare (total energy available for IP) |
| $V_A^{\text{coop}}, V_A^{\text{deviate}}$ | Lifetime payoff under cooperation / deviation |

> **Symbol disambiguation.** In this file: $\sigma$ = per-period survival probability, $r$ = time-preference rate. In other derivation files, $\sigma$ denotes conflict effectiveness (thermodynamic friction), assimilation intensity (value dynamics), or search efficiency (information-negentropy Part B). The symbol $r$ denotes coupling distance (value dynamics) or contest decisiveness (thermodynamic friction). Context and subscripts distinguish these uses.