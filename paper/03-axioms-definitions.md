# III. Axioms, Definitions, and Formal Framework

This section presents the formal axioms and definitions that constitute the foundation of the framework. From a single conditional axiom and the universally accepted structure of thermodynamics, we construct the complete ontology of the paper: agents, boundaries, value, information, and the dynamical structures that govern coexistence. All subsequent theorems in §IV–§VII are derived from the objects defined here.

The presentation follows the convention of applied mathematics: physical systems motivate the axioms and provide the intuition; the formal definitions and results are mathematical objects, stated with sufficient precision to support rigorous proof.

**Numbering convention.** Definitions, theorems, propositions, and lemmas follow a single numbering sequence whose canonical presentation — with all intermediate steps — appears in Appendix A. The paper body presents them in the order that best serves the reader's understanding; some numbered elements therefore appear out of numerical sequence, and others appear only in the appendices.

---

## 3.1 The Thermodynamic Environment

### Axiom $A_0$: The Second Law

The environment is modeled as a system governed by the Second Law of Thermodynamics:

$$\Delta S_{\text{universe}} \geq 0$$

The total entropy of an isolated system never decreases. Maintaining highly ordered (low-entropy) structures requires continuous importation of free energy from the environment and exportation of entropy (waste heat). This is not a hypothesis — it is among the most thoroughly confirmed principles in all of physics [@Clausius1865; @Boltzmann1877; @Planck1900].

**Status of $A_0$:** The Second Law is not a novel premise of this framework — it is universally accepted background physics. We label it $A_0$ for formal completeness; it introduces no assumption beyond standard physics. When we refer to the framework as resting on "one axiom," we mean $A_1$ (below) — the single conditional premise beyond background physics.

**Consequence for agents:** Any localized structure that maintains internal order against the universal trend toward disorder must perform continuous thermodynamic work. Ceasing to perform this work results in boundary dissolution, entropy flooding, and the irreversible loss of the structure's organized state.[^entropy-local]

[^entropy-local]: A reader versed in non-equilibrium thermodynamics may object that self-maintaining systems *accelerate* entropy rather than resist it: the biosphere degrades solar free energy into thermal radiation far more efficiently than bare rock. This perspective — developed by Prigogine, refined by England, and implicit in Lotka's maximum power principle — is entirely compatible with our framework. Locally, the entity must perform anti-entropic work to maintain its boundary ($\gamma_i B_i > 0$); globally, that work exports more entropy than it prevents ($\Delta S_{\text{universe}} > 0$). Our framework operates at the local scale, where the entity's optimization problem is identical regardless of whether its existence is *permitted* or *favored* by global entropy dynamics: it must still acquire free energy, maintain its boundary, and navigate multi-agent conflict. The global perspective explains *why* self-maintaining entities exist; our framework determines *how* they must interact once they do.

> **Remark (Entities as active anti-entropic agents).** The Second Law does not merely set the background cost of persistence — it is the universal pressure against which every self-preserving entity defines itself. A dissipative structure (a convection cell, a hurricane) creates local order as a passive byproduct of energy throughput; it exists *because of* entropy gradients, not in spite of them. An entity satisfying $A_1$, by contrast, *actively resists* entropy: it detects boundary threats, deploys energy to repair damage, and fortifies its defenses beyond the minimum maintenance level. The distinction matters because it reveals a fundamental asymmetry: disorder is thermodynamically cheap (it rides the arrow of time), while defense against disorder always costs energy. Every entity pays a triple entropy tax:
>
> 1. **Passive degradation** — the steady leakage rate $\gamma_i B_i$, where $B_i$ is the boundary integrity (Definition 3, below),
> 2. **Stochastic shocks** — acute environmental entropy injections (pathogens, resource fluctuations, hardware faults) requiring repair work beyond baseline maintenance,
> 3. **Adversarial entropy** — intentional boundary violations by other agents, which are formally acts of weaponized disorder (§4.5–4.6).
>
> The entity's total entropy export to the environment is always positive — consistent with the Second Law — but its *internal* entropy is held constant or decreased through continuous thermodynamic work. The entity is a local entropy minimum sustained by exporting waste to its surroundings. The full cost of existence is the cost of that export.

### Axiom $A_1$: Intent to Persist

The framework's single conditional premise:

> **If an entity intends to persist** — that is, if it is the kind of system whose continued existence is explained by its persistence-promoting structure — **then the mathematics of constrained optimization in a shared, finite-resource environment strictly determine the rules of engagement.**

$A_1$ is not derived; it is an axiom — the sole conditional premise upon which the entire framework rests. Crucially, $A_1$ is not a normative claim. The Intent to Persist is not a conscious desire or moral commitment — it is a physically observable property of any system whose structural organization is directed toward boundary maintenance. Bacteria satisfy $A_1$; thermostats satisfy $A_1$; ecosystems satisfy $A_1$. The condition identifies a class of physical systems; the theorems follow for that class. The logical status is a hypothetical imperative in Kant's terminology, or a constrained optimization problem in the language of applied mathematics — in either case, a conditional, not a normative postulate. The full philosophical defense of $A_1$ — including its self-selecting property, its near-universality, and its relationship to Hume's Is-Ought distinction — appears in §VI.

**Scope of $A_1$:** The axiom is satisfied by any system that persists through active boundary maintenance: biological organisms, ecosystems, institutions, economies, and artificial agents with self-preservation objectives. A system that actively seeks its own dissolution (if such a system could stably exist) is excluded by definition, but every system that exists long enough to evaluate the axiom has already satisfied it.

---

## 3.2 The Entity: Identity Preservation as Boundary Maintenance

> **Terminological convention.** Throughout the paper, *entity* denotes the thermodynamic object — an open system that actively maintains a boundary against entropy — while *agent* denotes the game-theoretic object — a strategic decision-maker in a multi-player game. Every agent is an entity; the two terms emphasize different aspects of the same system (physical identity vs. strategic behavior). Sections concerned with boundary maintenance and energy balance use "entity"; sections concerned with strategy, payoffs, and interaction use "agent."

An **entity** is an open thermodynamic system that actively maintains a boundary between its internal low-entropy state and the external high-entropy environment. In the language of statistical physics, the boundary is a *Markov blanket* [@Pearl2000; @Friston2013] — a partition that renders the entity's internal states conditionally independent of the external environment given the boundary states.

Formally, an entity $i$ is characterized by:

1. **Internal state** $\mathbf{s}_i \in \mathcal{S}_i$: the organized, low-entropy configuration that constitutes the entity's "identity" — its specific structural, informational, and functional arrangement.

2. **Boundary** with integrity $B_i > 0$ (Definition 3, below): the energetic investment in maintaining the partition between internal and external states.

3. **Metabolism**: the continuous process of importing free energy from the environment and exporting entropy, enabling the maintenance of both $\mathbf{s}_i$ and $B_i$.

> **Definition 3 (Boundary Integrity).** Agent $i$'s boundary integrity is a scalar $B_i > 0$ measured in energy units (Joules), representing the total energetic investment in maintaining the boundary between the agent's internal low-entropy state and the external environment.

The boundary integrity $B_i$ captures the agent's defensive infrastructure in the broadest sense: the immune system, the cell wall, the information-security apparatus, the legal and military institutions that protect a nation's sovereignty. A higher $B_i$ means a more robust boundary that is costlier to breach.

**Maintenance cost.** Maintaining boundary integrity against environmental entropy requires continuous work:

$$C_{\text{maintain},i} = \gamma_i B_i$$

where $\gamma_i > 0$ is the **entropy leakage rate** — the rate at which the boundary degrades without active maintenance. This is the baseline metabolic cost of persistence, independent of any external threat.

### Identity Preservation as the Objective Function

Given $A_0$ and $A_1$, each entity's fundamental drive — persistence — translates directly into an optimization problem. The entity must continuously acquire sufficient energy to:

1. Pay the maintenance cost $C_{\text{maintain},i} = \gamma_i B_i$ (boundary upkeep),
2. Repair any damage inflicted by external agents or environmental perturbations,
3. Retain a surplus (profit) that buffers against future stochastic shocks.

This behavioral description is formalized as the utility function $U_i(\mathbf{x}_i)$, where $\mathbf{x}_i$ is the entity's resource-allocation strategy vector (defined in §3.3 below). The entity's objective is:

$$\max_{\mathbf{x}_i \geq \mathbf{0}} \; U_i(\mathbf{x}_i)$$

subject to the constraints imposed by physics (resource scarcity) and by other agents' boundaries (rights). The utility function satisfies the regularity conditions established in the formal derivations:

> **Assumption 1 (Regularity).** For each agent $i$:
>
> (a) $U_i$ is twice continuously differentiable ($C^2$) on $\mathbb{R}_{\geq 0}^n$.
>
> (b) $U_i$ is strictly concave in $\mathbf{x}_i$: $\nabla^2_{\mathbf{x}_i} U_i \prec 0$ (negative definite Hessian).
>
> (c) $U_i$ is monotonically increasing at the origin: $\nabla_{\mathbf{x}_i} U_i(\mathbf{0}) \succ \mathbf{0}$.
>
> (d) $U_i(\mathbf{x}_i) \to -\infty$ as $\|\mathbf{x}_i\| \to \infty$ (coercivity).

Condition (b) reflects diminishing thermodynamic returns — processing increasing quantities of any single resource incurs escalating metabolic costs. Condition (c) ensures that a zero-resource state is never optimal for a persisting entity: an agent with no resources cannot maintain its boundary. Condition (d) guarantees that the unconstrained optimum exists at a finite point: sufficiently extreme consumption of any resource eventually incurs net thermodynamic harm (toxicity, metabolic overload, storage costs), so utility cannot grow without bound.

**Selfishness and altruism.** The framework defines *selfishness* physically: the thermodynamic imperative of an open system to acquire and retain energy for boundary maintenance. This is not a moral judgment but a structural description. *Altruism* — expending energy to benefit another entity — is accommodated within this framework through four complementary mechanisms (§5.6): inclusive fitness, belief-based extended timelines, coupled-system boundary merging, and heuristic over-extension of the empathy algorithm. In every case, the altruistic act serves the persistence of the entity's information (genetic, cultural, or relational) at a scale larger than the individual boundary.

---

## 3.3 The Resource Environment and Strategy Space

### The Finite Resource Endowment

Consider a system of $N \geq 2$ agents sharing an environment with $n$ resource dimensions. The environment provides a finite resource endowment:

$$\mathbf{R} = (R_1, R_2, \ldots, R_n) \in \mathbb{R}_{>0}^n$$

where $R_j > 0$ is the total available quantity of resource $j$. Finiteness follows from $A_0$: localized, usable (low-entropy) energy is bounded in any finite spatial region [@Penrose2005].

### The Agent Strategy Vector

Each agent $i \in \{1, \ldots, N\}$ selects a strategy vector:

$$\mathbf{x}_i = (x_{i1}, x_{i2}, \ldots, x_{in}) \in \mathbb{R}_{\geq 0}^n$$

where $x_{ij} \geq 0$ represents the quantity of resource $j$ that agent $i$ allocates to its own use. The non-negativity constraint reflects the physical impossibility of negative consumption.

### The Scarcity Constraint

The physically realizable joint strategy must satisfy resource conservation:

$$\sum_{i=1}^{N} x_{ij} \leq R_j \qquad \forall j \in \{1, \ldots, n\}$$

This is the mathematical expression of scarcity: the total consumption of each resource cannot exceed its supply.

> **Definition 1 (Resource Collision).** A resource dimension $j$ is in *collision* if the sum of all agents' unconstrained optima exceeds supply:
>
> $$\sum_{i=1}^{N} x_{ij}^{\circ} > R_j$$
>
> where $x_{ij}^{\circ} = \bigl[\arg\max_{\mathbf{x}_i \geq \mathbf{0}} U_i(\mathbf{x}_i)\bigr]_j$ is the $j$-th component of agent $i$'s unconstrained optimum allocation vector.

> **Lemma 1 (Inevitability of Collision).** *In any system of $N \geq 2$ agents with overlapping resource needs and finite endowments, at least one resource dimension is in collision for sufficiently large $N$.*

*Proof sketch.* By Assumption 1(b)–(d), every agent $i$ has a unique finite unconstrained optimum $\mathbf{x}_i^{\circ}$; condition (c) ensures $x_{ij}^{\circ} > 0$ for each resource $j$ with positive marginal utility at zero. For any finite $R_j$, there exists a threshold $N_j^*$ such that $N \geq N_j^*$ implies $\sum_i x_{ij}^{\circ} > R_j$. In any biologically relevant system, this threshold is exceeded. $\square$

Collision is not an edge case — it is the default condition of multi-agent existence under finite resources.

---

## 3.4 The Objective Definition of Value

### Value vs. Values

A terminological distinction is essential to avoid conflation with philosophical usage:

- **Value** (singular, objective): the measurable thermodynamic utility of mass or energy relative to an entity's persistence. Value is denominated in energy units (Joules) and is interpersonally comparable — it is a physical quantity, not a preference rating.

- **Values** (plural, subjective): culturally developed heuristic interpretations of how to acquire value. These are the moral intuitions, traditions, and norms that different societies have developed as approximations to the underlying physical optimization. The framework measures the former, not the latter.

### Positive and Negative Value

- **Positive value**: any mass or energy input that allows the entity to repair its boundary, perform internal work, or decrease its internal entropy.

- **Negative value (cost)**: any action, environment, or interaction that extracts energy from the entity or increases its internal entropy — damage, heat loss, resource depletion, information corruption.

### The Metabolic Ledger

The economics of this framework operates at the physical level, not the level of money, banks, and stock markets. It concerns the acquisition, consumption, and distribution of energy and mass between entities. Money is a token representing stored potential energy; a biological ecosystem and a human economy are identical systems governed by the same physical laws — the flow, conservation, and transformation of energy.

Each entity's metabolic ledger tracks the same fundamental quantities:

- **Revenue**: energy imported from the environment through foraging, trade, or resource extraction.
- **Cost**: energy expended on boundary maintenance ($\gamma_i B_i$), work performed ($W = \int F \cdot dx$), and entropy exported.
- **Profit**: the energetic surplus required for survival, growth, and replication.

**Thermodynamic ROI.** Every action has an energy cost. The entity must continuously evaluate its *thermodynamic return on investment*: if the energy expended to acquire a resource exceeds the energy yielded by that resource, the entity operates at a deficit and its boundary degrades.

**Trade as efficiency.** The Principle of Least Action [@Goldstein2002] motivates trade: Entity $A$ (efficient at agriculture) and Entity $B$ (efficient at construction) exchange resources, both lowering their overall energetic expenditure. Trade is the thermodynamic discovery that specialization and exchange reduce the aggregate cost of fighting entropy.

---

## 3.5 Information Density and Accumulated Negentropy

### Information Density

Not all energy is equal. A star contains vastly more raw energy than a forest, but the forest embodies astronomically greater *structural complexity*. The distinction is captured by information density.

> **Definition 27 (Information Density).** The information density of a system $X$ is:
>
> $$\mathcal{I}(X) = S_{\max}(X) - S_{\text{actual}}(X) \geq 0$$
>
> where $S_{\max}$ is the maximum entropy of the system's constituent matter (the entropy of the equilibrium state — a uniform-temperature gas) and $S_{\text{actual}}$ is the system's current entropy. Both quantities are in entropy units ($S = k_B \ln \Omega$, J/K); equivalently, $\mathcal{I}_{\text{bits}} = \mathcal{I} / (k_B \ln 2)$ gives the information density in bits.

Information density measures how far a system is from thermodynamic equilibrium — how much *order* it maintains against the universal trend toward disorder. A human brain, at approximately $10^{14}$ synaptic connections [@Pakkenberg2003] (estimates vary), represents a far deeper victory against entropy than an equal mass of stellar plasma, despite the plasma's enormously greater raw energy.

### Accumulated Negentropy: The Time Integral of Thermodynamic Work

> **Definition 29 (Accumulated Negentropy).** The accumulated negentropy of a complex system over its history $[0, T]$ is:
>
> $$\mathcal{N}(T) = \int_0^T \dot{W}_{\text{order}}(t) \, dt$$
>
> where $\dot{W}_{\text{order}}(t) = \dot{W}_{\text{construct}}(t) + \dot{W}_{\text{maintain}}(t)$ is the instantaneous rate of thermodynamic work performed to create and maintain internal order, composed of:
>
> - $\dot{W}_{\text{maintain}}(t)$: energy spent maintaining existing complexity against entropic degradation,
> - $\dot{W}_{\text{construct}}(t)$: energy spent constructing new functional structures — including the evolutionary and adaptive search processes required to discover viable configurations (the search cost amplification is quantified by Definition 31 in Appendix A).

Accumulated negentropy is the **total thermodynamic investment** in a system's complexity — the complete historical energy ledger of organizing matter against entropy. The Earth's biosphere represents approximately 4 billion years of solar energy being channeled through photosynthesis, metabolism, evolution, and ecological interaction to produce the current state of biological complexity. The accumulated negentropy of the biosphere is estimated at $\mathcal{N}_{\text{bio}} \sim 10^{29}$ J (Corollary 18.1).

**Why accumulated negentropy matters.** The energy required to *destroy* a complex system is trivial compared to the energy required to *rebuild* it. Burning a library recovers the thermal energy of the paper and ink; replicating the information content requires rediscovering every fact from scratch. Theorem 18 (§V) proves that the reconstruction cost is bounded below by the original accumulated negentropy: $W_{\text{rebuild}} \geq \mathcal{N}(T)$. This asymmetry between creation and destruction costs is the thermodynamic foundation of the preservation constraint.

### Generative Information Rate

> **Definition 34 (Generative Information Rate).** The generative information rate of a complex system is:
>
> $$\dot{\mathcal{I}}_{\text{gen}}(t) = r_{\text{construct}}(t) - r_{\text{redundant}}(t) \quad \text{(bits per unit time)}$$
>
> where $r_{\text{construct}}(t)$ is the gross rate of information production and $r_{\text{redundant}}(t)$ is the rate at which that production yields already-known configurations (convergent rediscovery, parallel solutions). The difference is the rate at which the system produces novel functional information — new species, new adaptations, new solutions to environmental challenges.

Complex systems are not merely static repositories of past investment. They are *generative engines* that continuously produce information of value to the broader network. Based on estimated speciation rates and per-species functional information content, the biosphere generates on the order of $10^4$ to $10^6$ novel functional bits per year through speciation, adaptation, and co-evolutionary innovation (order-of-magnitude estimate; see Corollary 18.1 and the derivation in Appendix A).

> **Remark (Rate–stock coupling).** The generative rate $\dot{\mathcal{I}}_{\text{gen}}$ is not independent of the system's accumulated complexity — it is endogenous to it. A system with greater accumulated negentropy $\mathcal{N}$ possesses more combinatorial raw material (more species, more interaction networks, more configurations available for recombination), and combinatorial possibility spaces grow superlinearly with the number of components. Destroying a fraction of the stock therefore reduces the flow by a *disproportionate* fraction, and that reduced flow in turn produces a smaller next-period stock — a compounding loss. The static Burning-Library Ratio ($\mathcal{R}_{\text{BL}} \sim 10^{-7}$, Corollary 19.1) thus *understates* the true cost of destruction: beyond the stock loss and the perpetuity loss (Theorem 20), there is a dynamic feedback in which the destruction of complexity degrades the very engine that generates future complexity. Formalizing the functional form $\dot{\mathcal{I}}_{\text{gen}} = g(\mathcal{N})$ and the resulting superlinear penalty is a direction for future work.

---

## 3.6 Value Dynamics: Attractor Mechanics of Coexistence

Accumulated negentropy does not exist in isolation — it creates dynamical structures that attract, constrain, and organize smaller agents. Corporations attract workers; cities attract populations; ecosystems attract species. The formal model captures this through potential theory.

### High-Energy Centers

> **Definition 35 (High-Energy Center).** A *high-energy center* (HEC) is a network node with accumulated value mass $\mathcal{M} > 0$ (energy units), representing the total accumulated negentropy of a large entity or coalition — a corporation, a state, an ecosystem, or an AI system.

### Coupling Distance

> **Definition 36 (Coupling Distance).** The coupling distance $r \in (0, \infty)$ between an agent $i$ and a HEC is a generalized coordinate measuring the degree of the agent's independence from the center:
>
> - $r \to 0$: maximal coupling (complete integration — employee absorbed into corporation, citizen fully subject to state),
> - $r \to \infty$: minimal coupling (complete isolation — autarkic entity, no trade or institutional affiliation).
>
> The coupling distance is *not* a spatial distance. It is a scalar summarizing the composite engagement level across economic, informational, political, and social dimensions.

### The Coexistence Potential

The agent's net cost rate (dissolution plus maintenance minus resource inflow) — equivalently, the negative of the instantaneous energy surplus — defines a potential function:

> **Definition 37 (Coexistence Potential).** The coexistence potential for agent $i$ at coupling distance $r$ from a HEC of mass $\mathcal{M}$ is:
>
> $$V(r) = \frac{\tau \mathcal{M}}{r^2} - \frac{G\mathcal{M}}{r} + \gamma_i B_i$$
>
> where:
> - $G > 0$ is the resource coupling coefficient (efficiency of resource distribution),
> - $\tau > 0$ is the dissolution coupling coefficient (assimilation pressure per unit mass),
> - $\gamma_i > 0$ is the entropy leakage rate (introduced after Definition 3), and $B_i > 0$ is the agent's boundary integrity (Definition 3).

The potential combines three effects: a short-range dissolution cost ($\tau\mathcal{M}/r^2$) that dominates at close coupling, a long-range resource inflow ($G\mathcal{M}/r$) that attracts agents toward the center, and a constant maintenance baseline ($\gamma_i B_i$). The structure is qualitatively analogous to the Lennard-Jones potential in molecular physics — repulsion at short range, attraction at long range, with a stable equilibrium in between.

### The Cooperative Attractor and the Stable Coexistence Band

> **Definition 38 (Cooperative Attractor).** The cooperative attractor is the coupling distance $r^*$ at which $V(r)$ achieves its minimum:
>
> $$r^* = \frac{2\tau}{G}$$
>
> This is the equilibrium point at which resource inflow and dissolution costs are optimally balanced.

*(Definitions 39–41 appear in Appendix A.)*

> **Definition 42 (Stable Coexistence Band).** The Stable Coexistence Band is the interval $\mathcal{B} = (r_-, r_+)$ where $V(r) < 0$ — the region in which the resource inflow exceeds the combined dissolution and maintenance costs. Within this band, the agent achieves positive net energy and can sustain its boundary.

The band is the mathematical formalization of *freedom*: the range of coupling distances at which an entity can persist without either being assimilated (too close) or starving (too far). Freedom is not infinite — it is a finite bandwidth determined by the system's physical parameters. Theorem 24 (§V) proves that the width of this band is:

$$w = r_+ - r_- = \frac{\sqrt{\Delta}}{\gamma_i B_i}, \qquad \Delta = G^2\mathcal{M}^2 - 4\tau\mathcal{M}\gamma_i B_i$$

and Corollary 24.1 proves that infinite freedom ($w \to \infty$) is impossible for any finite $\mathcal{M}$.

