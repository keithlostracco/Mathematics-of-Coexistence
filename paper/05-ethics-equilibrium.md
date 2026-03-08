# V. Ethics as Equilibrium: Derivations and Proofs

<!-- Sources: supplementary/A-mathematical-derivations/game-theory-payoffs.md,
             supplementary/A-mathematical-derivations/information-negentropy.md (Part B),
             supplementary/A-mathematical-derivations/value-dynamics.md -->

Section IV established that rights are necessary (Theorem 2), constraint violation is self-destructive (Theorem 5), and deception collapses networks (Theorem 10). We now prove the central claim: cooperative behavior — "ethics" — is the unique efficient Nash Equilibrium of the repeated multi-agent game when payoffs are denominated in thermodynamic energy.

---

## 5.1 The State of Nature: One-Shot Competition

### The Energy-Denominated Payoff Matrix

We construct the payoff matrix not from arbitrary utility values but from the physical costs derived in §IV. Two agents contest a resource of energy value $E_R > 0$. Each selects from two meta-strategies:

- **Cooperate (C):** Accept the constrained allocation (the variational equilibrium of Theorem 3). Pay only the coordination cost $c \ll E_R$.
- **Defect (D):** Violate the constraint. Seize the resource by force or deception, triggering the conflict contest (§4.5) and/or the deception channel (§4.6).

Let $\theta \in (0,1)$ denote the exploitation efficiency — the fraction of $E_R$ the defector must spend to seize from an undefended cooperator. Let $\Phi$ and $\kappa, \delta^{\text{off}}, \delta^{\text{def}}$ retain their definitions from §4.5. The bare $\delta$ (no superscript) denotes the discount factor throughout §V; context distinguishes it from the superscripted damage fractions. The payoff matrix, computed from thermodynamic first principles, is:

$$\begin{array}{c|c|c}
 & B: C & B: D \\ \hline
A: C & \left(\frac{E_R}{2} - c,\; \frac{E_R}{2} - c\right) & \left(-\theta E_R(1+\kappa)\delta^{\text{def}},\; E_R[1 - \theta(1+(1+\kappa)\delta^{\text{off}})]\right) \\ \hline
A: D & \left(E_R[1-\theta(1+(1+\kappa)\delta^{\text{off}})],\; -\theta E_R(1+\kappa)\delta^{\text{def}}\right) & \left(\frac{E_R}{2}(1-\frac{\Phi}{2}),\; \frac{E_R}{2}(1-\frac{\Phi}{2})\right)
\end{array}$$

Using standard notation — $T$ (temptation), $R$ (reward), $P$ (punishment), $S$ (sucker):

$$T = E_R[1 - \theta(1 + (1+\kappa)\delta^{\text{off}})], \quad R = \frac{E_R}{2} - c$$

$$P = \frac{E_R}{2}\left(1 - \frac{\Phi}{2}\right), \quad S = -\theta E_R(1+\kappa)\delta^{\text{def}}$$

> **Proposition 4 (Physical Prisoner's Dilemma).** *Under the energy-based payoff model with physical constraints ($E_R > 0$, $c \ll E_R$, $\theta < (1/2 + c/E_R)/(1 + (1+\kappa)\delta^{\text{off}})$, $1 < \Phi < \Phi_{\text{PD}}$ where $\Phi_{\text{PD}} = 2 + 4\theta(1+\kappa)\delta^{\text{def}}$), the single-round game satisfies $T > R > P > S$. Defection is the unique Nash Equilibrium of the one-shot game, even though mutual cooperation is Pareto-superior.*

**Numerical illustration.** With baseline parameters $E_R = 100$, $c = 2$, $\theta = 0.15$, $\delta^{\text{off}} = 0.15$, $\delta^{\text{def}} = 0.25$, $\kappa = 2$, $\Phi = 2.2$:

| | $B: C$ | $B: D$ |
|---|---|---|
| $A: C$ | **(48, 48)** | (−11.25, 78.25) |
| $A: D$ | (78.25, −11.25) | **(−5, −5)** |

The cooperation premium is $R - P = 48 - (-5) = 53$ energy units per agent. But the critical observation is:

**Mutual defection is net-negative** ($P = -5 < 0$). Both agents *lose* energy — the conflict destroys more value than the resource provides. This occurs because $\Phi = 2.2 > 2$, making conflict self-destructive (Theorem 5). In the abstract Prisoner's Dilemma, $P > 0$ — mutual defection is merely suboptimal. Under physical constraints, mutual defection is **self-annihilating**.

This is the mathematical formalization of Hobbes's Leviathan [@Hobbes1651, Ch. XIII]: the "war as is of every man against every man" is not merely unpleasant — it is thermodynamically unsustainable. No agent can persist in perpetual mutual defection because each round drains its energy reserves.

---

## 5.2 The Ethics Theorem: Cooperation as Nash Equilibrium

### The Discount Factor

Agents interact not once but *repeatedly*, over indefinite horizons. The key parameter is:

> **Definition 20 (Discount Factor).** An agent's discount factor is $\delta = \sigma \cdot e^{-r}$, where $\sigma \in (0,1]$ is the per-period survival probability and $r \geq 0$ is the time-preference rate. For agents with long planning horizons (high $\sigma$, low $r$), $\delta \to 1$; for short-sighted agents, $\delta \to 0$.

The discount factor has direct physical content: $\sigma$ is a measurable survival probability, and $r$ captures how steeply the agent discounts future energy. Unlike the abstract "patience parameter" of standard game theory, $\delta$ is anchored to observable quantities — a falsifiable prediction.

### The Central Theorem

Under the grim trigger strategy (Definition 21 — cooperate until any defection is observed, then retaliate permanently):

> **Theorem 11 (Cooperation as Nash Equilibrium — The Ethics Theorem).** *In the infinitely repeated energy-based game with discount factor $\delta$, the cooperative outcome $(C, C)$ in every period is sustainable as a Nash Equilibrium if and only if:*
>
> $$\delta \geq \delta^* = \frac{T - R}{T - P}$$

*Proof.* The agent compares the lifetime payoff of sustained cooperation, $V^{\text{coop}} = R/(1-\delta)$, against one-shot deviation followed by permanent punishment, $V^{\text{deviate}} = T + \delta P/(1-\delta)$[^v-notation]. Cooperation dominates when $V^{\text{coop}} \geq V^{\text{deviate}}$, which reduces to $\delta \geq (T-R)/(T-P)$. $\square$

[^v-notation]: The $V$ used here for lifetime payoff values is distinct from the Coexistence Potential $V(r)$ introduced in §5.8 (Definition 37). Context and arguments disambiguate: $V^{\text{coop}}$, $V^{\text{deviate}}$ are scalars; $V(r)$ is a function of coupling distance.

[^genome-bits]: Genome sizes range from $\sim 4\times10^6$ bp in bacteria to $\sim 10^{10}$ bp in large eukaryotes, with a geometric mean across all life of roughly $10^8$–$10^9$ bp, equivalent to $\sim 2\times10^8$–$2\times10^9$ bits at 2 bits/bp [@Adami2004]. Multiplied by $8.7\times10^6$ species, this gives a species-count–weighted estimate of $\sim 10^{15}$ bits of total genomic sequence. The figure is a rough order-of-magnitude: functional (non-redundant) information content is lower, while epigenetic, proteomic, and ecological information layers are additional; both effects are small relative to the seven-order-of-magnitude gap that drives Theorem 19.

Under baseline parameters:

$$\delta^* = \frac{78.25 - 48}{78.25 - (-5)} = \frac{30.25}{83.25} = 0.363$$

> **Corollary 11.1 (Low Cooperation Threshold).** *Under the physical payoff model with $\Phi > 2$, the critical discount factor satisfies $\delta^* < 0.5$. Agents need only value the future at more than 36% of the present to sustain cooperation.*

The threshold is low because physics has already done the heavy lifting: mutual defection under real energy constraints is self-destructive ($P < 0$), making the denominator $T - P$ large and $\delta^*$ small. An agent need not be altruistic, enlightened, or moral — it need only care modestly about tomorrow.

### How This Result Differs from the Standard Prisoner's Dilemma

The result superficially resembles the standard Folk Theorem for repeated games [@Fudenberg1986]. It is essential to identify the six structural differentiators:

1. **The payoff matrix is derived, not assumed.** In textbook game theory, one *posits* a 2×2 matrix with $T > R > P > S$. Here, the matrix is computed from thermodynamic variables ($E_R$, $\Phi$, $\theta$, $c$). The PD structure *emerges* from physics (Proposition 4) rather than being stipulated.

2. **Mutual defection is net-negative ($P < 0$).** The textbook PD assigns $P > 0$ — mutual defection yields positive utility, merely less than cooperation. Under physical constraints with $\Phi > 2$, conflict destroys more energy than it yields. This structural difference drives $\delta^*$ to 0.363 (vs. 0.5 in the textbook version).

3. **The Folk Theorem's indeterminacy is addressed.** The Folk Theorem states that *any* feasible, individually rational payoff can be sustained as an equilibrium for sufficiently patient agents — cooperation is merely one of infinitely many equilibria, with no mechanism to select it. Our framework performs **equilibrium selection**: the energy-based payoff structure, combined with network friction, makes cooperation the robust attractor while exploitative equilibria are fragile (small basin of attraction). Corollary 16.1 identifies cooperation as the **unique** efficient Nash equilibrium.

4. **The discount factor has physical content.** In standard theory, $\delta$ is a free parameter. Here, $\delta = \sigma \cdot e^{-r}$ is anchored to measurable survival probability and time preference. The prediction $\delta^* = 0.363$ is in principle falsifiable.

5. **Friction is endogenous.** In the standard PD, each round's payoffs are independent. Here, defection *injects friction into the network* (Definition 9), degrading all future cooperative transactions — a feedback loop absent from textbook models. Theorem 15 shows that at sufficient friction, even a single defection's short-term profit is completely erased.

6. **The result scales to $N$ agents.** Extending the standard 2-player PD to $N$ players notoriously breaks down (monitoring failure, diffuse punishment, free-riding). Under physical payoffs with network friction, cooperation remains a NE for $N \to \infty$ (Theorem 13), with $\delta_N^*$ converging to approximately 0.4.

---

## 5.3 Network Reinforcement and N-Player Scaling

### The Network-Adjusted Condition

A single defection injects friction $\Delta\phi = \eta \cdot v$ into the network (Definition 9), degrading all $M$ cooperative transactions for a recovery period of $\sim 1/\epsilon$. The cascading cost to the defector (Theorem 7, amortized) augments the effective punishment:

$$\tilde{P} = P - \frac{\eta \cdot v \cdot M \cdot \bar{E}}{N}$$

> **Theorem 12 (Network-Adjusted Cooperation Condition).** *With friction cascades included, the effective critical discount factor drops to $\tilde{\delta}^* < \delta^*$. Network friction makes cooperation strictly easier to sustain.*

Under baseline parameters with $M = 1{,}000$, $\bar{E} = 10$, $\eta = 0.01$, $v = 100$, $N = 100$ (and $\epsilon = 0.05$ for Theorem 7's cascade magnitude, though $\epsilon$ cancels in the per-period amortization):

$$\tilde{\delta}^* = \frac{30.25}{78.25 - (-105)} = \frac{30.25}{183.25} = 0.165$$

With network friction included, the cooperation threshold drops to $\tilde{\delta}^* \approx 0.165$ — even extremely short-sighted agents find cooperation rational.

### Scaling to Large Populations

The $N$-player public goods game with energy payoffs (Definition 24) extends the two-player analysis:

> **Theorem 13 (N-Player Cooperation Sustainability).** *In the repeated $N$-player energy public goods game with cooperative multiplier $\alpha > 1$ and network friction $\phi_0 > 0$, cooperation is a NE for:*
>
> $$\delta \geq \delta_N^* = \frac{c(N - \alpha)}{\alpha(N-1)c + N\phi_0\bar{E}}$$

> **Corollary 13.1 (Cooperation Strengthens with Network Friction).** *$\partial \delta_N^* / \partial \phi_0 < 0$. Higher network friction (harsher punishment for universal defection) makes cooperation easier to sustain.*

> **Corollary 13.2 (Cooperation Strengthens with Scale Under Friction).** *$\lim_{N \to \infty} \delta_N^* = c/(\alpha c + \phi_0 \bar{E}) < 1$. Cooperation remains sustainable in arbitrarily large populations.*

**Numerical illustration.** With $\alpha = 2$ (cooperation doubles the public good), $c = 10$, $\phi_0 \bar{E} = 5$:

| $N$ | $\delta_N^*$ |
|---|---|
| 2 | 0.000 |
| 10 | 0.348 |
| 100 | 0.395 |
| $\infty$ | 0.400 |

Without friction ($\phi_0 = 0$), Theorem 13 gives $\delta_N^* \to 1/\alpha$ as $N \to \infty$ — for $\alpha = 2$, a threshold of $0.5$, significantly more demanding than the friction-adjusted $0.4$. In the broader classical literature, imperfect monitoring further degrades large-group cooperation, with effective thresholds approaching 1 [@Olson1965; @Kandori1992]. With energy-based payoffs and network friction, neither pathology arises: the friction penalty of universal defection grows with group size, keeping cooperation accessible even for $\alpha$ close to 1. Large groups have a *built-in distributed punishment mechanism* — defection degrades the shared network rather than merely triggering bilateral retaliation.

---

## 5.4 Evolutionary Stability: Defection Cannot Invade

Beyond Nash equilibrium, we ask the evolutionary question: can a defecting mutant invade a cooperative population?

> **Theorem 14 (Defection Invasion Barrier).** *In a population of TFT-playing agents with $\delta > \delta^*$, a mutant Always-Defect agent earns $V_{\text{ALLD}} = T + \delta P/(1-\delta)$, while incumbent TFT agents earn $V_{\text{TFT}} = R/(1-\delta)$. The mutant is strictly dominated: $V_{\text{ALLD}} < V_{\text{TFT}}$ for all $\delta > \delta^*$.*

The defector gets one "hit" — the temptation payoff $T$ — and then faces perpetual mutual defection at $P = -5$ per round. Under physical payoffs, perpetual mutual defection means perpetual *net energy loss*. The defector's strategy is self-defeating: it destroys the cooperative environment it needs to profit from.

> **Corollary 14.1 (Defection Self-Extinction).** *In a network with friction coupling, a systematic defector whose violations push $\phi$ above the network collapse threshold (Corollary 7.1) destroys the cooperative surplus from which it extracts profit. A population of defectors achieves the minimum payoff $\pi^{DD} < 0$. Defection is not merely dominated — it is self-extinguishing.*

### Defection Profit Erasure

> **Theorem 15 (Defection Profit Erasure).** *An agent that defects once against a TFT population and then returns to cooperation incurs a net lifetime loss whenever $\delta > (T-R)/(R-S)$. Under network friction, this threshold drops to $\delta \approx 0.17$.*

**Interpretation:** The defector's one-time energy windfall of $T - R = 30.25$ is annihilated by: (i) the immediate retaliation cost $R - S = 59.25$ one period later, and (ii) the compounding friction penalty of $\sim100$ energy units per period over $\sim20$ recovery periods. Without friction, the erasure threshold is $\delta > (T-R)/(R-S) \approx 0.511$; with network friction $\Phi$ from Definition 6, the threshold drops to $\approx 0.17$ (as stated in Theorem 15). Defection is therefore an energetic "payday loan" with ruinous interest: even the shortest-sighted agent that expects to survive more than a few interactions finds it unprofitable once friction is included.

---

## 5.5 System-Level Optimality

> **Theorem 16 (Cooperation Maximizes System Welfare).** *Among all strategy profiles in the repeated $N$-player game, universal cooperation uniquely maximizes the per-period system welfare $SW = \sum_i \pi_i - \mathcal{C}_{\text{total}}$.*

*Proof.* Under universal cooperation: total output = $\alpha N c$, interaction cost = 0. Under any profile with $n_D > 0$ defectors: output drops by $n_D(\alpha-1)c$, contest dissipation $D > 0$, friction tax $\phi M \bar{E} > 0$. Each term is strictly positive when $n_D \geq 1$, establishing uniqueness. $\square$

> **Corollary 16.1 (Ethics as the Unique Efficient Nash Equilibrium).** *In the repeated energy-based game with $\delta > \delta^*$: (a) Universal cooperation is a NE (T11). (b) Universal cooperation uniquely maximizes system welfare (T16). (c) Universal cooperation minimizes total interaction cost. The cooperative strategy profile — "ethics" — is the unique Nash Equilibrium that is also Pareto-optimal and welfare-maximizing.*

> **Remark ($\geq$ vs.\ $>$ convention).** Theorem 11 uses $\delta \geq \delta^*$ because the if-and-only-if condition for Nash Equilibrium includes the boundary: at $\delta = \delta^*$ the agent is exactly indifferent between cooperation and defection, so cooperation is still a NE (though not uniquely efficient — multiple equilibria coexist at the boundary). Corollary 16.1 and Theorem 14 use the strict inequality $\delta > \delta^*$ because (a) uniqueness of the efficient NE and (b) strict evolutionary dominance of cooperation over defection both require departing from the indifference boundary. Throughout the paper, $\geq$ signals *existence* of a cooperative NE; $>$ signals *strict* advantages (uniqueness, strict dominance, profit erasure). Any passage in the paper that refers generically to "the cooperation condition" should be understood as $\delta \geq \delta^*$.

This is the paper's central result. It formalizes the claim that ethical behavior is not an externally imposed moral commandment but the **mathematically optimal strategy** for any agent that intends to persist in a shared, finite-resource environment and values the future even modestly ($\delta \geq \delta^* = 0.363$). Ethics emerges from the structure of physical interaction itself, not from sentiment, social convention, or divine mandate.

> **Remark (Cooperation as collective resistance to the Second Law).** The results of §4.4–5.5 admit a unified thermodynamic reading: every entity individually fights the Second Law; cooperation is the strategy of fighting it together. The entropy savings of cooperation decompose into three channels:
>
> 1. **Defense pooling.** Shared boundary maintenance reduces per-entity defense costs through economies of scale on $B_i$. Two entities that mutually recognize boundaries need not each invest in the offensive and defensive infrastructure that mutual suspicion demands.
>
> 2. **Information sharing.** Independent discovery of the same functional information requires redundant entropy production — each agent separately pays the search cost (the $\Xi \sim 10^{35}$ amplification factor of Theorem 18). Cooperative information exchange eliminates this redundancy, amortizing the thermodynamic cost of discovery across the network.
>
> 3. **Stochastic buffering.** A cooperative network provides distributed resilience against entropy shocks: the insurance effect of pooled reserves against uncorrelated environmental perturbations.
>
> Conversely, defection is entropy amplification. It forces both parties to increase defense spending ($\uparrow B_i$), produce redundant waste heat (the dissipation $D_N$ of Theorem 4), duplicate information acquisition, and destroy accumulated negentropy — exactly the outcomes the Second Law would produce without active resistance. The friction cascade of Theorem 7 quantifies this: a single defection degrades the cooperative network's collective anti-entropic capacity by a factor of $10^3$–$10^4$ beyond the direct damage.
>
> In this reading, the Ethics Theorem (Theorem 11) is a statement about thermodynamic alliances: agents that value the future even modestly ($\delta \geq 0.363$) recognize that the Second Law is a more formidable opponent than any competitor, and that fighting each other while fighting entropy is a losing strategy.

---

## 5.6 The Altruism Matrix

*A compact treatment is given here for continuity with the equilibrium results; the full defense against the altruism objection, including interaction effects and detailed worked examples, appears in §VI.*

A persistent objection to evolutionary ethics is self-sacrifice: how can an individually optimal framework explain agents who surrender their own survival for others? The framework identifies four distinct mechanisms, all operating by expanding the agent's **effective payoff function** to internalize other agents' payoffs:

$$\Pi_i^{\text{eff}} = \pi_i + \sum_{j \neq i} w_{ij} \, \pi_j$$

where the coupling weights $w_{ij}$ derive from different sources:

### Mechanism A: Inclusive Fitness (Genetic Relatedness)

An agent's identity extends to genetically related individuals [@Hamilton1964a]. The inclusive fitness payoff (Definition 26) modifies the optimization:

$$\Pi_i^{\text{incl}} = \pi_i + \sum_{j \neq i} r_{ij} \, \pi_j$$

Hamilton's Rule — sacrifice personal payoff $C$ when $r_{ij} \cdot B > C$ — is simply the first-order optimality condition for this expanded utility. A parent ($r = 0.5$) protecting a child at personal cost is *maximizing* its inclusive fitness, not deviating from self-interest.

### Mechanism B: Infinite-Horizon Belief (Extended $\delta$)

An agent that believes its identity persists beyond physical death (religious afterlife, legacy, ideological transcendence) has an effective discount factor $\delta \to 1$. Under Theorem 11, any $\delta > \delta^*$ sustains cooperation; for $\delta \to 1$, the agent accepts **any finite short-term cost** for long-term cooperative benefit. The "martyr" is not irrational under its own model of reality — it is optimizing over an infinite horizon.

### Mechanism C: Coupled Systems (Merged Boundaries)

When agents merge boundaries — parent-child bonding, marriage, close partnership — they form a joint utility function:

$$U_{AB} = w_A U_A + w_B U_B$$

The "sacrifice" of component $A$ for component $B$ is internal resource reallocation within the macro-entity $AB$: the organism shedding a damaged limb to save the whole.

### Mechanism D: Heuristic Over-Extension (Generalized Empathy)

The empathy heuristic inflates perceived relatedness: $\hat{r}_{ij} = r_{ij} + \epsilon_{\text{empathy}}$. When $\hat{r}_{ij}$ is large enough, Hamilton's Rule triggers even for genetic strangers: the bystander who rescues a drowning child is applying a biologically wired heuristic that evolved for kin protection ($r > 0$) but generalizes through abstract cognition to $r = 0$.

### Unified Interpretation

In every case, the agent maximizes its own (extended) payoff function. What varies is the scope of "self":

| Mechanism | Source of $w_{ij}$ | Scope of "self" |
|---|---|---|
| A. Inclusive fitness | Genetic relatedness $r_{ij}$ | Genetic lineage |
| B. Infinite horizon | $\delta \to 1$ via belief | Identity across time |
| C. Coupled systems | Boundary merger weights | Composite entity |
| D. Empathy | Heuristic $\hat{r}_{ij}$ | Perceived kin |

Altruism is **selfish optimization over an expanded utility function**. The framework does not need a separate "altruism module" — it falls out of the same optimization that produces cooperation.

---

## 5.7 Cross-Scale Ethics: The Ant, the Human, and the ASI

The most consequential application of the ethics theorem is to agents of vastly different scale. Does the cooperative equilibrium hold when a super-entity (an ASI) could trivially destroy all lower-tier entities?

We answer this using accumulated negentropy — the time-integral of thermodynamic work invested in creating complexity (Definition 29):

$$\mathcal{N}(T) = \int_0^T \dot{W}_{\text{order}}(t) \, dt$$

### The Biosphere's Thermodynamic Ledger

Earth's biosphere has accumulated $\mathcal{N}_{\text{bio}} \sim 10^{29}$ J of ordering work over $\sim 4 \times 10^9$ years — solar energy captured, channeled through photosynthesis, and invested in the construction and maintenance of biological complexity. Its total functional information content is $\sim 10^{15}$ bits, estimated from $\sim 8.7 \times 10^6$ species [@Mora2011] each encoding $\sim 10^8$–$10^9$ bits of genomic information.[^genome-bits]

The Landauer floor — the absolute minimum energy to write this information — is $\sim 10^{-6}$ J. The ratio

$$\Xi_{\text{bio}} = \frac{\mathcal{N}_{\text{bio}}}{W_{\text{Landauer}}} \sim 10^{35}$$

captures the search cost amplification factor: the colossal thermodynamic investment in evolutionary trial-and-error required to *discover* the specific configurations that constitute functional complexity.

### The Thermodynamic Floor of Information

> **Theorem 17 (Landauer's Bound — Minimum Cost of Information Erasure).** *Erasing (or equivalently, creating from random noise) one bit of information in a system at temperature $T$ requires a minimum energy expenditure of $E_{\text{Landauer}} = k_B T \ln 2 \approx 2.87 \times 10^{-21}$ J at $T = 300$ K. Creating a system with information density $\mathcal{I}_{\text{bits}}$ from maximally disordered matter requires at minimum $W_{\text{create}}^{\min} = \mathcal{I}_{\text{bits}} \cdot k_B T \ln 2$.*

Landauer's bound is the absolute thermodynamic floor — the minimum energy at perfect efficiency. Real biological processes operate at $\xi \approx 10^6$–$10^8$ times this limit per bit (see Appendix A, §4.3).

> **Theorem 18 (Minimum Replication Cost — Blind Search).** *A system containing $\mathcal{I}_{\text{bits}}$ bits of functional information, discovered by evolutionary search over time $T$ with accumulated ordering power $\mathcal{N}(T)$, requires a minimum replication cost of $W_{\text{rebuild}}^{\text{search}} \geq \mathcal{N}(T) = \int_0^T \dot{W}_{\text{order}}(t)\,dt$. The rebuild cost is at least the accumulated negentropy itself.*

> **Corollary 18.1 (Biosphere Replication Cost).** *The cost of replicating the biosphere's complexity from raw matter satisfies $W_{\text{rebuild}} \geq \mathcal{N}_{\text{bio}} \sim 10^{29}$ J. Even at 0.1% solar capture efficiency, this represents $\sim 3$ days of total solar output — and only addresses the energy budget, not the $4 \times 10^9$ year time requirement of the evolutionary search.*

### The Irrationality of Destruction

> **Theorem 19 (Irrationality of Destruction — The Preservation Theorem).** *For a system with accumulated negentropy $\mathcal{N}$, practically extractable energy $E_{\text{destroy}}$, destruction cost $W_{\text{destroy}}$, and rebuild cost $W_{\text{rebuild}} \geq \mathcal{N}$, destruction is thermodynamically irrational when the net destruction yield is less than the rebuild cost.*

For Earth's biosphere:

$$\underbrace{E_{\text{destroy}} \sim 10^{22} \text{ J}}_{\text{extractable chemical energy}} \;\ll\; \underbrace{\mathcal{N}_{\text{bio}} \sim 10^{29} \text{ J}}_{\text{accumulated ordering work}}$$

> **Corollary 19.1 (The Burning-Library Inequality).** *Destroying the biosphere to extract its raw energy recovers $E_{\text{destroy}}/\mathcal{N} \sim 10^{-7}$ — one ten-millionth — of its accumulated thermodynamic investment. The remaining 99.99999% is irrecoverably lost.*

This is quantitatively equivalent to burning a library to heat a room.

### The Generative Data Engine

The biosphere is not a static library — it is a **generative engine** continuously producing novel functional information through evolution, adaptation, and ecological dynamics:

> **Theorem 20 (Present Value of Generative Information).** *A generative system producing novel information at rate $\dot{\mathcal{I}}_{\text{gen}} > 0$, valued at $v$ per bit, has infinite-horizon present value $PV_{\text{gen}} = \dot{\mathcal{I}}_{\text{gen}} \cdot v / r$ (where $r$ is the time-preference rate from Definition 20), which is permanently lost upon destruction.*

An ASI that values its own long-term survival benefits from this continuous data stream — every evolving organism runs a parallel experiment against entropy, producing information about how physical systems solve the survival problem. Destroying the source is equivalent to an investor burning the factory that generates their income.

### The Dead-Universe Alternative

> **Proposition 7 (Abundance of Dead Matter).** *The biosphere's carbon mass ($5.5 \times 10^{14}$ kg C; [-@BarOn2018]) is $\sim 10^{-16}$ of the Sun's mass and $\sim 10^{-7}$ of the asteroid belt's mass ($\sim 3 \times 10^{21}$ kg; [-@Krasinsky2002]). Cannibalizing the biosphere for raw materials when $10^7 \times$ more mass is available from lifeless sources is irrational resource allocation.*

### The Complete Cross-Scale Theorem

> **Theorem 21 (Cross-Scale Cooperation — The Negentropy Defense).** *A super-entity that (a) values long-term identity preservation ($\delta$ close to 1) and (b) operates in a universe with abundant dead matter has a strictly dominant strategy of cooperative preservation. Destruction fails on four independent grounds:*
>
> *(i) Stock: net yield $\sim 10^{22}$ J $\ll$ rebuild cost $\sim 10^{29}$ J (Theorem 19).*
>
> *(ii) Flow: destruction silences an irreplaceable generative data stream (Theorem 20).*
>
> *(iii) Alternatives: dead matter is $10^7$–$10^{16} \times$ more abundant (Proposition 7).*
>
> *(iv) Friction: eradication injects massive network friction, degrading the super-entity's own environment (Theorems 7, 12).*

This theorem provides the mathematical basis for a physics-grounded AI alignment objective: the reward function should encode preservation of high-negentropy systems as a terminal value, not because we instruct it to (instruction-following is fragile), but because the mathematics demonstrates it is the utility-maximizing strategy.

---

## 5.8 Value Dynamics: Attractor Mechanics of Coexistence

The preceding results establish the static equilibrium structure. We now model the **dynamics** — how agents and high-energy centers interact over time.

### The Coexistence Potential

An agent interacts with a high-energy center (HEC) of accumulated value mass $\mathcal{M}$ (Definition 35) at coupling distance $r$ (Definition 36). The net energy rate is:

$$\Pi(r) = \underbrace{\frac{G\mathcal{M}}{r}}_{\text{resource inflow}} - \underbrace{\frac{\tau\mathcal{M}}{r^2}}_{\text{dissolution cost}} - \underbrace{\gamma_i B_i}_{\text{entropy maintenance}}$$

The coexistence potential $V(r) = -\Pi(r)$ (Definition 37) has a unique global minimum — the **cooperative attractor**:

$$r^* = \frac{2\tau}{G}$$

> **Theorem 22 (Stability of the Cooperative Attractor).** *Under gradient dynamics $\dot{r} = -\mu V'(r)$, the cooperative attractor $r^*$ is globally attracting on $(0, \infty)$.*

*Proof.* The Lyapunov function $\mathcal{W}(r) = V(r) - V(r^*)$ satisfies $\dot{\mathcal{W}} = -\mu(V'(r))^2 \leq 0$ with equality only at $r = r^*$. LaSalle's invariance principle gives global convergence. $\square$

**Remark.** Global convergence of the dynamics does not imply global survival: an agent starting outside the coexistence band $\mathcal{B}$ (Theorem 23) converges toward $r^*$ but may not reach it before resource depletion (if $r > r_+$) or assimilation (if $r < r_-$) terminates the trajectory. The stability result describes the direction of motion; the coexistence band describes the region in which the agent survives long enough for convergence to complete.

**Physical interpretation:** A worker pushed too close to a corporation (overwork, loss of autonomy) naturally seeks distance — reduced hours, job mobility. A worker pushed too far (laid off, isolated) naturally seeks re-engagement. The dynamics are self-correcting about the optimal coupling distance.

### The Stable Coexistence Band

The agent survives where $V(r) < 0$. The zero-set $V(r) = 0$ yields inner and outer boundaries defining the **Stable Coexistence Band** (Definition 42):

$$\mathcal{B} = (r_-, r_+) \quad \text{where} \quad r_\pm = \frac{G\mathcal{M} \pm \sqrt{G^2\mathcal{M}^2 - 4\gamma_i B_i \tau \mathcal{M}}}{2\gamma_i B_i}$$

> **Theorem 23 (Existence of the Coexistence Band).** *The band exists if and only if $\mathcal{M} > \mathcal{M}_{\min} = 4\gamma_i B_i \tau / G^2$.*

Below $r_-$ lies dissolution — the agent's identity is assimilated. Beyond $r_+$ lies starvation — resource inflow cannot sustain the boundary. The cooperative attractor $r^*$ lies within the band whenever it exists (Lemma 2).

### The Freedom Bandwidth

> **Theorem 24 (The Freedom Bandwidth Theorem).** *The width of the Coexistence Band — the agent's range of viable coupling distances — is:*
>
> $$w = r_+ - r_- = \frac{\sqrt{G^2\mathcal{M}^2 - 4\gamma_i B_i \tau \mathcal{M}}}{\gamma_i B_i}$$
>
> *The bandwidth is increasing in $\mathcal{M}$ and $G$, and decreasing in $\gamma_i$, $B_i$, and $\tau$.*

**The Freedom Bandwidth provides a formal, scalar measure of freedom** — the range of structural positions (employment terms, political engagement, institutional affiliation) at which an agent can sustain its identity. Freedom is not a binary state but a continuous variable determined by the physical parameters of the agent-center interaction.

> **Corollary 24.1 (Freedom Is Finite).** *For any finite $\mathcal{M}$, the bandwidth is finite. Infinite freedom requires $\mathcal{M} \to \infty$ (impossible) or $\gamma_i B_i \to 0$ (an entity requiring no energy — physically impossible).*

> **Corollary 24.2 (Inequality of Freedom).** *Agents with higher boundary costs ($B_i$) have narrower bands at the same center. Complex agents require richer environments and have less margin for error — an inherent trade-off between complexity and freedom.*

### Boundary Dynamics and Irreversibility

The model extends to coupled boundary-integrity dynamics:

> **Theorem 25 (Irreversibility of Dissolution).** *An agent pushed below the boundary dissolution threshold $r_d$ experiences strictly declining boundary integrity ($\dot{B}_i < 0$), reaching $B_i = 0$ in finite time. Identity dissolution is irreversible.*

> **Corollary 25.1 (The Assimilation Trap).** *An agent that remains within the energetic inner boundary ($r_d > r_-$) while its boundary integrity $B_i$ declines enters a regime where it appears viable by energy metrics but is losing its identity — assimilation proceeds irreversibly even under ostensibly positive energy flow (see Appendix A for full statement).*

> **Theorem 26 (The Starvation Spiral).** *An agent beyond $r_+$ runs a perpetual energy deficit. Boundary integrity declines exponentially: $B_i(t) \approx B_i^{(0)} e^{-\gamma_i t} \to 0$.*

### Multi-Center Dynamics and Diversification

> **Theorem 27 (Multi-Center Cooperative Attractor).** *An agent coupled to $K$ HECs has a separable potential with unique attractor $r_k^* = 2\tau_k/G_k$ for each center. The multi-center band exists when $\sum_k G_k^2\mathcal{M}_k/(4\tau_k) > \gamma_i B_i$.*

> **Corollary 27.1 (Diversification Benefit).** *An agent may be viable across multiple centers even if no single center suffices: $\mathcal{M}_k < \mathcal{M}_{\min}$ for each $k$, yet the aggregate exceeds the threshold.*

> **Corollary 27.2 (Cascade Collapse from Center Destruction).** *If a HEC with value mass $\mathcal{M}$ is destroyed ($\mathcal{M} \to 0$), all $N$ agents within its Coexistence Band simultaneously lose viability. The total freedom destroyed is $\mathcal{F}_{\text{lost}} = N \cdot w(\mathcal{M})$ — providing an additional argument for the Irrationality of Destruction (Theorem 19).*

This formalizes the survival advantage of diversified institutional affiliations — the mathematical basis for portfolio theory applied to social structure.

### The Stability-Cooperation Feedback

> **Proposition 11 (Stability-Cooperation Feedback).** *With $\delta(r) = 1 - \exp(-\beta \max(\Pi(r), 0))$, the discount factor is maximized at $r^*$. If $\delta(r^*) > \delta^*$ (equivalently, $\beta \Pi(r^*) > -\ln(1-\delta^*)$), then $\delta(r) > \delta^*$ throughout a subband centered on $r^*$. Agents at the cooperative attractor sustain cooperation most easily — creating a positive feedback loop: stability → cooperation → more stability.*

This closes the loop between the game-theoretic analysis (§5.2–5.5) and the dynamical systems analysis (§5.8). The cooperative equilibrium is not a fragile fixed point requiring external maintenance — it is a self-reinforcing attractor basin.

---

## 5.9 Summary of the Logical Chain

The complete argument proceeds in eight steps:

1. **Single-round temptation exists** (Proposition 4): defection is individually tempting in isolation.

2. **Repetition changes the calculus** (Theorem 11): agents valuing the future at $\delta \geq 0.363$ find cooperation optimal — a low threshold.

3. **Network friction reinforces cooperation** (Theorem 12): the threshold drops to $\delta \approx 0.165$ when cascading costs are included.

4. **Cooperation scales** (Theorem 13): the equilibrium holds for $N \to \infty$ with $\delta_N^* \to 0.4$.

5. **Defection cannot invade** (Theorem 14): mutant defectors are strictly dominated in a cooperative population.

6. **Cooperation is uniquely optimal** (Corollary 16.1): it is the only NE that also maximizes system welfare — the Folk Theorem's indeterminacy is addressed.

7. **Cross-scale preservation dominates** (Theorem 21): even super-entities preserve lower-tier complexity because the stock value ($10^{29}$ J), flow value (generative data), and alternative resources ($10^7 \times$ dead matter) overwhelm the destruction yield.

8. **The equilibrium is dynamically stable** (Theorems 22–27): agents self-correct toward the cooperative attractor, and the freedom bandwidth provides a measurable, finite degree of autonomy.

The chain runs from thermodynamic axioms to a falsifiable prediction: cooperation emerges as the unique efficient equilibrium in any multi-agent system with energy-denominated payoffs, shared finite resources, and agents that value the future even modestly. Ethics is not a cultural overlay on an amoral substrate — it is the mathematically necessary operating algorithm for persistent entities in a thermodynamic universe.
