# Value Dynamics — Attractor Mechanics of Coexistence

---

## 0. Preamble

This document contains the formal mathematical derivation for the value dynamics framework. Building on the preceding derivations, we now construct a **dynamical systems model** for the interaction between individual agents and high-energy centers (HECs) — large accumulated-value nodes in the network (corporations, states, trade hubs, AI systems).

The contribution is **applied mathematics**: we use potential theory, gradient dynamics, Lyapunov stability analysis, and comparative statics to prove that the agent-center interaction possesses a **stable equilibrium region** (the "Stable Coexistence Band") whose width constitutes a formal measure of freedom. We further prove that crossing the band's boundaries leads to irreversible regime changes — dissolution of identity (assimilation) or energetic collapse (starvation).

The physics analogy is gravitational orbital mechanics; the formal contribution is a **dynamical systems model** with a potential well that traps agents in a viable region. We do not claim that literal gravitational forces operate at social scales. We prove that the **mathematical structure** — a potential function with short-range repulsion and long-range attraction creating a stable basin — describes agent-center dynamics and yields non-trivial, testable results.

**Key references for the tools used:**

- [@Strogatz2015] — gradient dynamics, stability, bifurcations.
- [@HirschSmaleDevaney2013] — Lyapunov stability, attractor theory.
- [@Tirole1988] — firm-worker coupling, vertical relationships.
- [@AcemogluRobinson2012] — institutional power concentration and state capture.
- [@Jones1924] — structural precedent for two-body potentials balancing short-range repulsion and long-range attraction.

**Notational continuity from preceding derivations:**

- $N$ agents, strategy vectors $\mathbf{x}_i$, utility functions $U_i$ (Lagrangian constraints derivation).
- Boundary integrity $B_i > 0$; entropy leakage rate $\gamma_i > 0$ (thermodynamic friction, Definitions 3–4).
- Maintenance cost $C_{\text{maintain},i} = \gamma_i B_i$ (thermodynamic friction derivation, §2.2).
- Network friction coefficient $\phi$; friction sensitivity $\eta$; recovery rate $\epsilon$ (thermodynamic friction derivation).
- Accumulated negentropy $\mathcal{N}(T)$ (Definition 29).
- Discount factor $\delta$; cooperation threshold $\delta^*$ (Theorem 11).

---

## 1. The Agent–Center Model

### 1.1 Motivation: Why Dynamics Matter

The preceding derivations established the static structure of cooperative multi-agent systems: rights as constraints, conflict as waste, cooperation as equilibrium, information as value. But the framework describes a **dynamic** phenomenon: accumulated value creates attractor dynamics. Entities are drawn toward high-energy centers because proximity lowers the cost of fighting entropy. Too close, and the entity is assimilated; too far, and it starves.

This is inherently a **dynamical systems** question: given an agent and a center, what coupling strength is stable? What happens when the agent is perturbed from equilibrium? Under what conditions does the equilibrium exist at all?

### 1.2 Primitive Objects

> **Definition 35 (High-Energy Center).** A *high-energy center* (HEC) is a network node with accumulated value mass
>
> $$\mathcal{M} > 0 \quad \text{(energy units, J)}$$
>
> representing the total accumulated negentropy of the center (Definition 29). The HEC may be a corporation, a state, a trade hub, an ecosystem, or an AI system — any entity or coalition that has aggregated sufficient energy and information to exert significant influence on surrounding agents.

> **Definition 36 (Coupling Distance).** The *coupling distance* $r \in (0, \infty)$ between an agent $i$ and a HEC is a generalized coordinate measuring the degree of the agent's independence from the center:
>
> - $r \to 0$: maximal coupling (complete integration — employee absorbed into corporation, citizen fully subject to state, subsidiary merged into parent)
> - $r \to \infty$: minimal coupling (complete isolation — autarkic entity, no trade or institutional affiliation)
>
> The coupling distance is **not** a spatial distance. It is a scalar summarizing the composite engagement level across economic, informational, political, and social dimensions. Formally, $r$ can be constructed as a norm on the vector of coupling channels, but for the 1D analysis below, only its scalar properties matter.

**Interpretation:** The coupling distance $r$ is the single degree of freedom in our model. An agent's "strategy" in the value-dynamics context is its choice of how tightly to bind itself to a given HEC. This complements the multi-dimensional resource strategy $\mathbf{x}_i$ from the Lagrangian constraints derivation: there, the agent chose *what* to consume; here, the agent chooses *how closely* to affiliate with the source of resources.

### 1.3 The Resource Inflow Function

As the agent couples more tightly with a HEC (smaller $r$), it gains greater access to the center's accumulated resources — shared infrastructure, trade networks, institutional protection, information flows, and surplus energy. We model the **energy inflow rate** as:

$$E_{\text{in}}(r) = \frac{G \, \mathcal{M}}{r}$$

where $G > 0$ is the **resource coupling coefficient** — a proportionality constant capturing the efficiency of the HEC at distributing resources to its affiliates.

**Properties:**
- $E_{\text{in}}(r) > 0$ for all $r > 0$ (the HEC always provides some resources, however distant).
- $E_{\text{in}}(r) \to \infty$ as $r \to 0$ (arbitrarily large resource access at arbitrarily tight coupling — but offset by costs below).
- $E_{\text{in}}(r) \to 0$ as $r \to \infty$ (isolation yields negligible resource access).
- $E_{\text{in}}$ is proportional to $\mathcal{M}$: a more massive center supplies more resources at every coupling distance.

The $1/r$ functional form is the simplest monotonically decreasing, positive function with the correct limits. It parallels the gravitational potential $GM/r$, providing the "attraction" half of the model.

### 1.4 The Dissolution Cost Function

Tight coupling also imposes **autonomy costs**: the HEC demands conformity, extracts resources from the agent, constrains the agent's action space (Lagrangian constraints derivation, §3), and exerts homogenizing pressure on the agent's internal state. At sufficiently close coupling, these costs overwhelm the benefits and erode the agent's boundary integrity, leading to dissolution of identity.

We model the **dissolution cost rate** as:

$$C_{\text{dissolve}}(r) = \frac{\tau \, \mathcal{M}}{r^2}$$

where $\tau > 0$ is the **dissolution coupling coefficient** — a proportionality constant capturing the HEC's assimilation pressure per unit mass.

**Properties:**
- $C_{\text{dissolve}}(r) > 0$ for all $r > 0$.
- $C_{\text{dissolve}}(r) \to \infty$ as $r \to 0$, and **faster** than $E_{\text{in}}(r)$ (the $1/r^2$ term dominates $1/r$ at small $r$). This is the critical structural feature: at very close coupling, the costs always overwhelm the benefits.
- $C_{\text{dissolve}}(r) \to 0$ as $r \to \infty$ (distant agents are not subject to assimilation pressure).

The $1/r^2$ form ensures that the dissolution cost is a **short-range dominant** force, negligible at large $r$ but overwhelming at small $r$. This parallels the Lennard-Jones repulsion in molecular physics and the "tidal forces" of the gravitational analogy.

**Physical motivation:** The dissolution cost scales as $1/r^2$ rather than $1/r$ because assimilation pressure involves not only resource extraction but also **constraint imposition** — the HEC's demand for conformity grows nonlinearly with coupling tightness. An employee who works 60 hours/week for a corporation loses far more than 1.5× the autonomy of one working 40 hours. The constraints compound.

### 1.5 The Entropy Maintenance Baseline

Independent of the HEC, the agent must continuously expend energy to maintain its boundary against environmental entropy (thermodynamic friction derivation, §2.2):

$$C_{\text{maintain}} = \gamma_i \, B_i$$

where $\gamma_i > 0$ is the entropy leakage rate and $B_i > 0$ is the boundary integrity. This is a **constant** cost — it does not depend on $r$ because entropy attacks the boundary regardless of the agent's institutional affiliations. For the single-agent analysis that follows, we write $\gamma \equiv \gamma_i$ and suppress the index to reduce notation.

### 1.6 The Net Energy Rate

The agent's **net energy rate** at coupling distance $r$ is:

$$\Pi(r) = E_{\text{in}}(r) - C_{\text{dissolve}}(r) - C_{\text{maintain}} = \frac{G \mathcal{M}}{r} - \frac{\tau \mathcal{M}}{r^2} - \gamma B_i$$

The agent survives if and only if $\Pi(r) > 0$. The agent's goal is to choose $r$ to maximize $\Pi(r)$ — equivalently, to minimize the **coexistence potential** $V(r) = -\Pi(r)$.

---

## 2. The Coexistence Potential

### 2.1 Definition

> **Definition 37 (Coexistence Potential).** The *coexistence potential* of an agent $i$ at coupling distance $r$ from a HEC with value mass $\mathcal{M}$ is:
>
> $$V(r) = \frac{\tau \mathcal{M}}{r^2} - \frac{G \mathcal{M}}{r} + \gamma B_i$$
>
> where $G > 0$ is the resource coupling coefficient, $\tau > 0$ is the dissolution coupling coefficient, $\gamma > 0$ is the entropy leakage rate, and $B_i > 0$ is the agent's boundary integrity. The potential is defined on $(0, \infty)$.

The coexistence potential is the **negative** of the net energy rate: $V(r) = -\Pi(r)$. Regions where $V(r) < 0$ are viable (positive net energy); regions where $V(r) > 0$ are non-viable (energy deficit).

### 2.2 Properties

> **Proposition 8 (Properties of the Coexistence Potential).**
>
> *The coexistence potential $V(r)$ satisfies:*
>
> *(a) $\lim_{r \to 0^+} V(r) = +\infty$ (dissolution dominance at close range).*
>
> *(b) $\lim_{r \to \infty} V(r) = \gamma B_i > 0$ (starvation at large distance).*
>
> *(c) $V$ is $C^\infty$ on $(0, \infty)$.*
>
> *(d) $V$ has exactly one critical point on $(0, \infty)$, which is a global minimum.*
>
> *(e) The minimum value $V_{\min}$ satisfies $V_{\min} < \gamma B_i$.*

*Proof.* 

(a) As $r \to 0^+$: $\tau \mathcal{M}/r^2 \to +\infty$, while $G\mathcal{M}/r \to +\infty$ at a slower rate. Since $1/r^2$ dominates $1/r$ as $r \to 0$, $V(r) \to +\infty$.

(b) As $r \to \infty$: both $\tau\mathcal{M}/r^2 \to 0$ and $G\mathcal{M}/r \to 0$, so $V(r) \to \gamma B_i > 0$.

(c) $V$ is a sum of rational functions of $r$ (with $r > 0$) and a constant, hence smooth.

(d) Compute the first derivative:

$$V'(r) = -\frac{2\tau\mathcal{M}}{r^3} + \frac{G\mathcal{M}}{r^2} = \frac{\mathcal{M}}{r^3}\bigl(Gr - 2\tau\bigr)$$

Since $\mathcal{M} > 0$ and $r^3 > 0$, the sign of $V'(r)$ is determined by $(Gr - 2\tau)$:

- $V'(r) < 0$ for $r < 2\tau/G$ (potential decreasing)
- $V'(r) = 0$ at $r = 2\tau/G$ (unique critical point)
- $V'(r) > 0$ for $r > 2\tau/G$ (potential increasing)

The second derivative at the critical point:

$$V''(r) = \frac{6\tau\mathcal{M}}{r^4} - \frac{2G\mathcal{M}}{r^3}$$

At $r^* = 2\tau/G$:

$$V''(r^*) = \frac{6\tau\mathcal{M} \cdot G^4}{16\tau^4} - \frac{2G\mathcal{M} \cdot G^3}{8\tau^3} = \frac{G^4\mathcal{M}}{8\tau^3}\bigl(3 - 2\bigr) = \frac{G^4\mathcal{M}}{8\tau^3} > 0$$

Since $V''(r^*) > 0$, the critical point is a strict local minimum. By uniqueness of the critical point and the boundary behavior (parts a, b), it is the global minimum.

(e) $V(r^*) = \frac{\tau\mathcal{M}G^2}{4\tau^2} - \frac{G\mathcal{M}G}{2\tau} + \gamma B_i = \gamma B_i - \frac{G^2\mathcal{M}}{4\tau}$. Since $G^2\mathcal{M}/(4\tau) > 0$, we have $V(r^*) < \gamma B_i$. $\square$

### 2.3 The Cooperative Attractor

> **Definition 38 (Cooperative Attractor).** The *cooperative attractor* is the coupling distance that minimizes the coexistence potential:
>
> $$r^* = \frac{2\tau}{G}$$
>
> At this distance, the agent achieves the maximum net energy rate $\Pi(r^*) = G^2\mathcal{M}/(4\tau) - \gamma B_i$.

**Interpretation:** The cooperative attractor $r^*$ represents the **optimal structural coupling** between the agent and the HEC. It depends only on the ratio $\tau/G$ — the balance between dissolution pressure and resource access — not on the HEC's mass $\mathcal{M}$ or the agent's boundary cost $\gamma B_i$. This is a structural property: the optimal degree of integration is determined by the *nature* of the coupling, not the *scale* of the parties.

What does depend on $\mathcal{M}$ is whether the agent can survive at all (the depth of the potential well) and how wide the viable region is (the Coexistence Band).

### 2.4 The Potential Well Depth

> **Definition 39 (Potential Well Depth).** The *well depth* of the coexistence potential is:
>
> $$D = \gamma B_i - V(r^*) = \frac{G^2 \mathcal{M}}{4\tau}$$
>
> This is the maximum net energy surplus achievable by the agent when optimally coupled to the HEC.

The well depth is proportional to $\mathcal{M}$: a more massive center creates a deeper well, supporting agents with higher maintenance costs.

---

## 3. Gradient Dynamics and Stability

### 3.1 The Coupling Adjustment Equation

Agents adjust their coupling distance toward higher net energy (lower potential). The simplest model is **gradient dynamics**:

$$\dot{r} = -\mu \, V'(r) = -\frac{\mu \mathcal{M}}{r^3}(Gr - 2\tau)$$

where $\mu > 0$ is the **adjustment rate** (mobility, adaptability — how quickly the agent can change its institutional affiliations).

**Dynamical behavior:**

- For $r < r^*$: $Gr - 2\tau < 0$, so $\dot{r} > 0$ — the agent moves **away** from the center (escaping dissolution pressure).
- For $r > r^*$: $Gr - 2\tau > 0$, so $\dot{r} < 0$ — the agent moves **toward** the center (seeking resources).
- At $r = r^*$: $\dot{r} = 0$ — the agent is at equilibrium.

### 3.2 Stability of the Cooperative Attractor

> **Theorem 22 (Stability of the Cooperative Attractor).**
>
> *Under the gradient dynamics $\dot{r} = -\mu V'(r)$, the cooperative attractor $r^* = 2\tau/G$ is:*
>
> *(a) A fixed point: $\dot{r}|_{r=r^*} = 0$.*
>
> *(b) Locally asymptotically stable: the eigenvalue $\lambda = -\mu V''(r^*) = -\mu G^4 \mathcal{M} / (8\tau^3) < 0$.*
>
> *(c) Globally attracting on $(0, \infty)$: every trajectory starting at $r_0 \in (0, \infty)$ converges to $r^*$ as $t \to \infty$.*

*Proof.*

(a) At $r^*$: $V'(r^*) = 0$, so $\dot{r} = 0$. ✓

(b) Linearize around $r^*$: $\dot{r} \approx -\mu V''(r^*)(r - r^*)$. From Proposition 8(d), $V''(r^*) = G^4\mathcal{M}/(8\tau^3) > 0$. The eigenvalue of the linearized system is $\lambda = -\mu V''(r^*) < 0$. Hence $r^*$ is locally asymptotically stable.

(c) Define the Lyapunov function $\mathcal{W}(r) = V(r) - V(r^*)$. Then $\mathcal{W}(r) \geq 0$ for all $r > 0$ with equality iff $r = r^*$ (since $r^*$ is the unique global minimum of $V$). The time derivative along trajectories:

$$\dot{\mathcal{W}} = V'(r) \cdot \dot{r} = V'(r) \cdot \bigl(-\mu V'(r)\bigr) = -\mu \bigl(V'(r)\bigr)^2 \leq 0$$

with equality iff $V'(r) = 0$, i.e., $r = r^*$. By LaSalle's invariance principle, every trajectory converges to the largest invariant set within $\{r : \dot{\mathcal{W}} = 0\} = \{r^*\}$. Hence $r^*$ is globally attracting.

**Convergence rate:** Near $r^*$, the convergence is exponential with rate $|\lambda| = \mu G^4\mathcal{M}/(8\tau^3)$. Larger $\mu$ (more mobile agents) and larger $\mathcal{M}$ (more massive centers) accelerate convergence. $\square$

**Corollary 22.1 (Resilience of the Equilibrium).** *The cooperative attractor is robust to perturbations: any temporary displacement from $r^*$ (due to external shocks, policy changes, economic disruptions) is self-correcting. The agent naturally returns to the optimal coupling distance.*

**Physical interpretation:** A worker who is pushed closer to the corporation than optimal (overwork, loss of autonomy) will naturally seek more distance — reduced hours, unionization, job mobility. A worker pushed too far (laid off, isolated) will naturally seek re-engagement — job searching, networking. The gradient dynamics formalize this behavioral regularity.

---

## 4. The Stable Coexistence Band

### 4.1 The Viability Condition

The agent survives if and only if $\Pi(r) > 0$, equivalently $V(r) < 0$. The boundary of the viable region is defined by $V(r) = 0$:

$$\frac{\tau \mathcal{M}}{r^2} - \frac{G \mathcal{M}}{r} + \gamma B_i = 0$$

Multiplying by $r^2$:

$$\gamma B_i \, r^2 - G\mathcal{M} \, r + \tau\mathcal{M} = 0$$

This is a quadratic in $r$ with discriminant:

$$\Delta = G^2 \mathcal{M}^2 - 4\gamma B_i \tau \mathcal{M} = \mathcal{M}\bigl(G^2 \mathcal{M} - 4\gamma B_i \tau\bigr)$$

### 4.2 The Minimum Viable HEC Mass

> **Theorem 23 (Existence of the Coexistence Band).**
>
> *The Stable Coexistence Band exists if and only if the HEC's value mass exceeds a critical threshold:*
>
> $$\mathcal{M} > \mathcal{M}_{\min} \;\triangleq\; \frac{4\gamma B_i \tau}{G^2}$$
>
> *When $\mathcal{M} = \mathcal{M}_{\min}$, the band collapses to the single point $r^*$ (marginal viability). When $\mathcal{M} < \mathcal{M}_{\min}$, no viable coupling distance exists — the agent cannot sustain itself near this HEC.*

*Proof.* Two positive real roots of $V(r) = 0$ require: (i) $\Delta > 0$, which gives $\mathcal{M} > 4\gamma B_i \tau / G^2$; (ii) both roots positive, which is guaranteed since the sum $r_- + r_+ = G\mathcal{M}/(\gamma B_i) > 0$ and the product $r_- \cdot r_+ = \tau\mathcal{M}/(\gamma B_i) > 0$. When $\Delta = 0$, there is a single repeated root $r^* = G\mathcal{M}/(2\gamma B_i)$, and the minimum value $V(r^*) = 0$ (marginal viability). When $\Delta < 0$, $V(r) > 0$ for all $r > 0$ — the well is too shallow to reach negative values. $\square$

**Physical interpretation:** A small corner shop ($\mathcal{M}$ low) cannot sustain employees who have high living costs ($\gamma B_i$ high). A massive technology corporation ($\mathcal{M}$ high) can sustain many agents with high boundary costs. The threshold $\mathcal{M}_{\min}$ is the minimum accumulated value at which a center becomes a viable attractor.

### 4.3 Inner and Outer Boundaries

> **Definition 40 (Dissolution Threshold — Inner Boundary).** The *dissolution threshold* is the inner boundary of the Stable Coexistence Band:
>
> $$r_- = \frac{G\mathcal{M} - \sqrt{\Delta}}{2\gamma B_i}$$
>
> Below $r_-$, the dissolution cost exceeds the resource benefit net of maintenance: $V(r) > 0$ for $r < r_-$.

> **Definition 41 (Starvation Threshold — Outer Boundary).** The *starvation threshold* is the outer boundary of the Stable Coexistence Band:
>
> $$r_+ = \frac{G\mathcal{M} + \sqrt{\Delta}}{2\gamma B_i}$$
>
> Beyond $r_+$, the resource inflow is insufficient to cover maintenance and dissolution costs: $V(r) > 0$ for $r > r_+$.

> **Definition 42 (Stable Coexistence Band).** The *Stable Coexistence Band* is the open interval:
>
> $$\mathcal{B} = (r_-, r_+) = \left\{r > 0 : V(r) < 0\right\}$$
>
> Within this band, the agent has positive net energy ($\Pi(r) > 0$) and can sustain its identity. The cooperative attractor $r^* = 2\tau / G$ lies within $\mathcal{B}$ whenever the band exists.

**Lemma 2 (Attractor Containment).** *If the Coexistence Band exists ($\mathcal{M} > \mathcal{M}_{\min}$), then $r_- < r^* < r_+$.*

*Proof.* By Proposition 8(d), $r^*$ is the unique global minimum of $V(r)$. When $\mathcal{M} > \mathcal{M}_{\min}$, $V(r^*) < 0$ while $V(r_-) = V(r_+) = 0$. Since $V$ is strictly decreasing on $(0, r^*)$ and strictly increasing on $(r^*, \infty)$, the zero $r_-$ must satisfy $r_- < r^*$ and the zero $r_+$ must satisfy $r_+ > r^*$. $\square$

### 4.4 Band Width: The Freedom Bandwidth

> **Theorem 24 (The Freedom Bandwidth Theorem).**
>
> *The width of the Stable Coexistence Band is:*
>
> $$w \;\triangleq\; r_+ - r_- = \frac{\sqrt{\Delta}}{\gamma B_i} = \frac{\sqrt{G^2 \mathcal{M}^2 - 4\gamma B_i \tau \mathcal{M}}}{\gamma B_i}$$
>
> *The bandwidth satisfies:*
>
> *(a) $w > 0$ if and only if $\mathcal{M} > \mathcal{M}_{\min}$.*
>
> *(b) $w$ is strictly increasing in $\mathcal{M}$: $\partial w / \partial \mathcal{M} > 0$.*
>
> *(c) $w$ is strictly decreasing in each of $\gamma$, $B_i$, and $\tau$.*
>
> *(d) $w$ is strictly increasing in $G$.*
>
> *(e) In the limit $\mathcal{M} \gg \mathcal{M}_{\min}$: $w \approx G\mathcal{M}/(\gamma B_i)$ — the bandwidth grows linearly with HEC mass.*
>
> *(f) Near the viability threshold ($\mathcal{M} \to \mathcal{M}_{\min}^+$): $w \sim \sqrt{\mathcal{M} - \mathcal{M}_{\min}}$ — the bandwidth vanishes as a square root.*

*Proof.* From the quadratic formula: $r_\pm = (G\mathcal{M} \pm \sqrt{\Delta})/(2\gamma B_i)$, so $w = \sqrt{\Delta}/(\gamma B_i)$.

(a) $w > 0 \iff \Delta > 0 \iff \mathcal{M} > \mathcal{M}_{\min}$. ✓

(b) $\Delta = \mathcal{M}(G^2\mathcal{M} - 4\gamma B_i \tau) = G^2\mathcal{M}^2 - 4\gamma B_i \tau \mathcal{M}$. Then:

$$\frac{\partial \Delta}{\partial \mathcal{M}} = 2G^2\mathcal{M} - 4\gamma B_i \tau = 2\bigl(G^2\mathcal{M} - 2\gamma B_i \tau\bigr)$$

For $\mathcal{M} > \mathcal{M}_{\min} = 4\gamma B_i \tau/G^2$: $G^2\mathcal{M} > 4\gamma B_i \tau > 2\gamma B_i \tau$, so $\partial\Delta/\partial\mathcal{M} > 0$, hence $\partial w/\partial\mathcal{M} > 0$. ✓

(c) Direct computation: $\partial\Delta/\partial\gamma = -4B_i\tau\mathcal{M} < 0$; $\partial\Delta/\partial B_i = -4\gamma\tau\mathcal{M} < 0$; $\partial\Delta/\partial\tau = -4\gamma B_i \mathcal{M} < 0$. Additionally, $w = \sqrt{\Delta}/(\gamma B_i)$, and $\gamma$, $B_i$ appear in the denominator, further decreasing $w$. ✓

(d) $\partial\Delta/\partial G = 2G\mathcal{M}^2 > 0$, so $\partial w / \partial G > 0$. ✓

(e) For $\mathcal{M} \gg \mathcal{M}_{\min}$: $\Delta \approx G^2\mathcal{M}^2$, so $w \approx G\mathcal{M}/(\gamma B_i)$. ✓

(f) Write $\Delta = G^2\mathcal{M}_{\min}(\mathcal{M} - \mathcal{M}_{\min}) + G^2(\mathcal{M} - \mathcal{M}_{\min})^2$. Near $\mathcal{M}_{\min}$, the linear term dominates: $\Delta \approx G^2\mathcal{M}_{\min}(\mathcal{M} - \mathcal{M}_{\min})$, so $w \approx G\sqrt{\mathcal{M}_{\min}(\mathcal{M} - \mathcal{M}_{\min})}/(\gamma B_i)$, confirming the square-root behavior. $\square$

**Corollary 24.1 (Freedom Is Finite).** *For any finite $\mathcal{M}$, the bandwidth $w$ is finite. No agent enjoys infinite freedom relative to any finite-mass center. Infinite freedom ($w \to \infty$) requires $\mathcal{M} \to \infty$ (an infinitely massive center) or $\gamma B_i \to 0$ (zero maintenance cost, i.e., an entity that requires no energy to exist — physically impossible).*

**Physical interpretation of the Freedom Bandwidth:**

| Parameter | Effect on $w$ | Interpretation |
|---|---|---|
| $\mathcal{M} \uparrow$ | $w \uparrow$ | Richer centers offer wider freedom (more room to maneuver) |
| $G \uparrow$ | $w \uparrow$ | More efficient resource coupling expands viable distance |
| $\gamma \uparrow$ | $w \downarrow$ | Higher entropy pressure (harsher environment) narrows freedom |
| $B_i \uparrow$ | $w \downarrow$ | More complex entities (higher maintenance) have narrower bands |
| $\tau \uparrow$ | $w \downarrow$ | Stronger dissolution pressure narrows freedom |

---

## 5. Boundary Dynamics and Irreversibility

The gradient dynamics of §3 assume the agent's boundary integrity $B_i$ is constant. In reality, $B_i$ is itself dynamic: it degrades under assault from the HEC's assimilation pressure or from resource deprivation, and it regenerates when the agent has surplus energy.

### 5.1 The Coupled Agent–Boundary System

> **Definition 43 (Boundary Degradation Rate).** The *boundary degradation rate* due to HEC assimilation pressure at coupling distance $r$ is:
>
> $$D_{\text{assimilate}}(r) = \frac{\sigma \mathcal{M}}{r^3}$$
>
> where $\sigma > 0$ is the **assimilation intensity** coefficient. This is a short-range dominant force ($1/r^3$ decays faster than the dissolution cost $1/r^2$), reflecting that active boundary destruction requires even closer coupling than the autonomy costs of §1.4.

> **Definition 44 (Boundary Regeneration Rate).** The *boundary regeneration rate* is the fraction of surplus energy the agent allocates to boundary repair:
>
> $$R_{\text{repair}}(r) = \rho \cdot \max\bigl(\Pi(r), 0\bigr)$$
>
> where $\rho \in (0, 1)$ is the **repair allocation fraction** and $\Pi(r) = -V(r)$ is the net energy rate.

The coupled dynamical system governing both coupling distance and boundary integrity is:

$$\dot{r} = -\mu \, V'(r)$$

$$\dot{B}_i = R_{\text{repair}}(r) - D_{\text{assimilate}}(r) - \gamma B_i$$

### 5.2 The Dissolution Catastrophe

> **Theorem 25 (Irreversibility of Dissolution).**
>
> *Define the **boundary dissolution threshold** as:*
>
> $$r_d \;\triangleq\; \left(\frac{\sigma \mathcal{M}}{\rho \, \Pi_{\max} + \gamma B_i^{(0)}}\right)^{1/3}$$
>
> *where $\Pi_{\max} = G^2\mathcal{M}/(4\tau) - \gamma B_i^{(0)}$ is the maximum surplus at the attractor and $B_i^{(0)}$ is the initial boundary integrity. If the agent's coupling distance satisfies $r < r_d$, then:*
>
> *(a) $\dot{B}_i < 0$: Boundary integrity is strictly decreasing.*
>
> *(b) As $B_i$ decreases, $\mathcal{M}_{\min} = 4\gamma B_i \tau / G^2$ decreases but the surplus $\Pi(r)$ at the current $r$ does not necessarily increase enough to halt the decline.*
>
> *(c) There exists a finite time $t_d < \infty$ at which $B_i(t_d) = 0$ — the agent's boundary is fully dissolved and identity ceases to exist.*

*Proof.* At coupling distance $r < r_d$:

$$D_{\text{assimilate}}(r) > \frac{\sigma\mathcal{M}}{r_d^3} = \rho\Pi_{\max} + \gamma B_i^{(0)} \geq \rho \cdot \max(\Pi(r), 0) + \gamma B_i$$

To verify the last inequality: $\dot{B}_i < 0$ from the outset ensures $B_i(t) \leq B_i^{(0)}$ for all $t \geq 0$. Since $\max(\Pi(r),0) \leq G^2\mathcal{M}/(4\tau) - \gamma B_i$ for any $r$, we obtain $\rho\max(\Pi(r),0) + \gamma B_i \leq \rho G^2\mathcal{M}/(4\tau) + (1-\rho)\gamma B_i \leq \rho\Pi_{\max} + \gamma B_i^{(0)}$, where the final step uses $B_i \leq B_i^{(0)}$ and $\rho < 1$. Therefore:

$$\dot{B}_i = \rho \max(\Pi(r), 0) - D_{\text{assimilate}}(r) - \gamma B_i < 0$$

Since $\dot{B}_i < 0$ and bounded away from zero, $B_i$ reaches zero in finite time. $\square$

*Remark (Race-Condition Closure).* Theorem 25 establishes dissolution conditional on $r(t) < r_d$. Since the gradient dynamics (Theorem 22) simultaneously push $r$ toward $r^*$, we must verify that boundary depletion outpaces escape. We resolve this via the phase-space derivative $dB_i/dr = \dot{B}_i/\dot{r}$.

Along trajectories of the coupled system (§5.1) with $r \in (0, r_d)$, separate the assimilation-dominated term from the surplus correction:

$$\frac{dB_i}{dr} = \frac{-\sigma}{\mu(2\tau - Gr)} + \frac{[\rho\max(\Pi(r),0) - \gamma B_i]\,r^3}{\mu\mathcal{M}(2\tau - Gr)}.$$

Both $\dot{B}_i$ and $\dot{r}$ share the $\mathcal{M}/r^3$ scaling, which cancels in the ratio; the leading term $-\sigma/[\mu(2\tau - Gr)]$ is therefore independent of $\mathcal{M}$. To bound the correction, use $\max(\Pi(r),0) \leq \Pi_{\max}$, $B_i \geq 0$, and $r^3 \leq r_d^3 = \sigma\mathcal{M}/(\rho\Pi_{\max} + \gamma B_i^{(0)})$; combining with the leading term and factoring:

$$\frac{dB_i}{dr} \leq \frac{-\sigma\gamma B_i^{(0)}}{\mu(\rho\Pi_{\max} + \gamma B_i^{(0)})(2\tau - Gr)}.$$

Applying the conservative envelope $2\tau - Gr \leq 2\tau$ yields the uniform bound $dB_i/dr \leq -\alpha$ where

$$\alpha \;\triangleq\; \frac{\sigma\gamma B_i^{(0)}}{2\mu\tau(\rho\Pi_{\max} + \gamma B_i^{(0)})} > 0.$$

Integrating from $r_0$ to $r$ gives $B_i(r) \leq B_i^{(0)} - \alpha(r - r_0)$. Define the **critical penetration depth**

$$\ell_c \;\triangleq\; \frac{B_i^{(0)}}{\alpha} = \frac{2\mu\tau(\rho\Pi_{\max} + \gamma B_i^{(0)})}{\sigma\gamma}.$$

If the agent starts at $r_0$ with penetration depth $\ell \triangleq r_d - r_0 > \ell_c$, then $B_i$ reaches zero before $r$ escapes to $r_d$: dissolution is irreversible despite the restoring gradient. Since the bound used $2\tau - Gr \leq 2\tau$ and dropped the negative $\gamma B_i$ contribution, $\ell_c$ is a conservative upper bound on the true critical depth; the actual dissolution rate per unit escape distance *increases* as $r$ approaches $r_d$ because the restoring velocity $\dot{r} \propto (2\tau - Gr)$ weakens as $r \to r^*$. The condition $\ell > \ell_c$ is therefore sufficient but not necessary for irreversibility.

Physical interpretation: an employee drawn into a corporation's inner circle eventually crosses a depth from which the escape gradient — always present — cannot outpace identity erosion. The critical depth $\ell_c$ scales with agent mobility $\mu$ (mobile agents tolerate deeper excursions) and inversely with assimilation intensity $\sigma$ (stronger assimilators set shallower traps).

**Corollary 25.1 (The Assimilation Trap).** *Once an agent crosses the dissolution threshold $r_d$ with $r_d < r_-$ (the dissolution threshold lies inside the energetic inner boundary), the gradient dynamics push the agent back toward $r^*$ (Theorem 22). However, if $r_d > r_-$ (the dissolution threshold extends into the viable band), an agent perturbed below $r_d$ experiences simultaneous boundary degradation and energetic pressure. If the boundary degrades sufficiently to lower $r_-$ below the current $r$ (shrinking the energetic inner boundary), the agent enters the dissolution zone while still within $\mathcal{B}$ — an assimilation trap where the agent appears viable by energy metrics but is losing its identity.*

**Physical interpretation:** An employee (agent) at a mega-corporation (HEC) may earn a good salary (positive $\Pi(r)$) while simultaneously losing creative autonomy, decision-making capacity, and identity ($B_i$ declining). By the time the boundary has degraded enough for the agent to "feel" the loss, the process may be irreversible — the agent has been assimilated (corporate culture has overwritten individual identity). Similarly, a small nation within a superpower's sphere of influence may experience economic benefits while losing sovereignty.

### 5.3 The Starvation Spiral

> **Theorem 26 (The Starvation Spiral).**
>
> *If the agent's coupling distance satisfies $r > r_+$ (outside the Coexistence Band), then:*
>
> *(a) $\Pi(r) < 0$: The agent runs an energy deficit.*
>
> *(b) $\dot{B}_i = -D_{\text{assimilate}}(r) - \gamma B_i < 0$: Boundary integrity declines since there is no surplus for repair and the assimilation and entropy terms are both positive.*
>
> *(c) As $B_i$ decreases, $\mathcal{M}_{\min}$ decreases but $r_+$ also shifts (increasing the effective band), potentially allowing the agent to re-enter $\mathcal{B}$ — but this requires $r_+$ to grow fast enough to reach the agent's current position.*
>
> *(d) If $r$ is sufficiently large, no decrease in $B_i$ can restore viability: the agent starves in finite time.*

*Proof sketch.* Outside $\mathcal{B}$: $V(r) > 0$, so $\Pi(r) < 0$ and $\max(\Pi(r), 0) = 0$. Then $\dot{B}_i = -D_{\text{assimilate}}(r) - \gamma B_i < 0$. As $B_i \to 0$, the agent's boundary fails. For large $r$, $D_{\text{assimilate}}(r) \approx 0$, so the decay rate is approximately $\dot{B}_i \approx -\gamma B_i$, giving $B_i(t) = B_i^{(0)} e^{-\gamma t} \to 0$ — exponential starvation. $\square$

**Physical interpretation:** An entity that completely cuts itself off from all energy centers (autarky, isolationism) slowly depletes its stores. Without resource inflow, entropy wins — the boundary degrades, the internal state disorients, and the entity ceases to function. This maps to failed states that isolate themselves, hermit communities, or AI systems cut off from data streams.

---

## 6. Comparative Statics and Inequality

### 6.1 Effect of Value Mass on the Coexistence Band

> **Proposition 9 (Value Mass Comparative Statics).**
>
> *As the HEC's value mass $\mathcal{M}$ increases:*
>
> *(a) The well depth $D = G^2\mathcal{M}/(4\tau)$ increases linearly.*
>
> *(b) The bandwidth $w$ increases (Theorem 24b).*
>
> *(c) The dissolution threshold $r_-$ decreases (the inner boundary moves inward):*
>
> $$\frac{\partial r_-}{\partial \mathcal{M}} = \frac{1}{2\gamma B_i}\left(G - \frac{G^2\mathcal{M} - 2\gamma B_i \tau}{\sqrt{\Delta}}\right) < 0 \quad \text{for } \mathcal{M} > \mathcal{M}_{\min}$$
>
> *(d) The starvation threshold $r_+$ increases (the outer boundary moves outward):*
>
> $$\frac{\partial r_+}{\partial \mathcal{M}} = \frac{1}{2\gamma B_i}\left(G + \frac{G^2\mathcal{M} - 2\gamma B_i \tau}{\sqrt{\Delta}}\right) > 0$$
>
> *(e) The cooperative attractor $r^* = 2\tau/G$ is unchanged.*

**Physical interpretation:** More massive centers support wider freedom. A wealthier, more institutionally robust state provides its citizens with both more protection against starvation (larger $r_+$) and more residual autonomy before assimilation (smaller $r_-$). The optimal coupling structure ($r^*$) is invariant — what changes is the margin of error.

### 6.2 Effect of Agent Boundary Integrity

> **Proposition 10 (Boundary Integrity Comparative Statics).**
>
> *As the agent's boundary integrity $B_i$ increases:*
>
> *(a) The minimum viable HEC mass $\mathcal{M}_{\min} = 4\gamma B_i \tau / G^2$ increases — more complex agents require more massive centers.*
>
> *(b) The bandwidth $w$ decreases (Theorem 24c) — more complex agents have narrower freedom bands.*
>
> *(c) The cooperative attractor $r^*$ is unchanged — the optimal coupling structure is independent of agent complexity.*

**Physical interpretation:** A complex, high-maintenance entity (a research university, a democratic institution, a highly differentiated organism) requires a richer environment to survive and has less margin for error in its coupling distance. Simple, low-maintenance entities (a single-celled organism, a subsistence farmer) can survive in sparser environments with wider latitude. This is an **inherent trade-off** between complexity and freedom: more complex agents require more resources and are thus more constrained in their viable coupling range.

### 6.3 Inequality: Asymmetric Agents at the Same Center

Consider two agents, $i$ and $j$, with different boundary integrities $B_i > B_j$ (agent $i$ is more complex) coupled to the same HEC. Both share the same attractor $r^* = 2\tau/G$ and the same HEC mass $\mathcal{M}$.

> **Corollary 24.2 (Inequality of Freedom).** *If $B_i > B_j$ (agent $i$ has higher boundary cost), then:*
>
> *(a) $w_i < w_j$ — agent $i$ has a narrower Coexistence Band (less freedom).*
>
> *(b) $\mathcal{M}_{\min,i} > \mathcal{M}_{\min,j}$ — agent $i$ requires a more massive center to survive.*
>
> *(c) There exists a critical $\mathcal{M}^*$ such that for $\mathcal{M}_{\min,j} < \mathcal{M} < \mathcal{M}_{\min,i}$, agent $j$ can survive near this HEC but agent $i$ cannot.*

**Physical interpretation:** Inequality in complexity creates inequality in freedom. Within the same economic or political system, agents with higher maintenance costs (due to greater complexity, specialization, or vulnerability) have narrower viable ranges. This formalization captures why developing nations have less policy latitude than developed ones, why small businesses are more fragile than large ones, and why specialized organisms are more extinction-prone than generalists.

---

## 7. Multi-Center Dynamics

### 7.1 The Multi-Center Potential

In realistic environments, agents interact with multiple HECs simultaneously — an individual may be employed by a corporation, reside in a state, trade with international partners, and participate in online communities. Let there be $K$ HECs with value masses $\mathcal{M}_1, \ldots, \mathcal{M}_K$.

The agent's coupling state is now a vector $\mathbf{r} = (r_1, \ldots, r_K) \in (0, \infty)^K$, where $r_k$ is the coupling distance to HEC $k$.

> **Definition 45 (Multi-Center Coexistence Potential).** The *multi-center coexistence potential* is:
>
> $$V(\mathbf{r}) = \sum_{k=1}^{K} \left[\frac{\tau_k \mathcal{M}_k}{r_k^2} - \frac{G_k \mathcal{M}_k}{r_k}\right] + \gamma B_i$$
>
> where $G_k, \tau_k > 0$ are the center-specific coupling coefficients. The multi-center bandwidth is the volume of the viable set $\mathcal{B} = \{\mathbf{r} : V(\mathbf{r}) < 0\}$.

> **Theorem 27 (Multi-Center Cooperative Attractor).**
>
> *The multi-center coexistence potential $V(\mathbf{r})$ has a unique global minimum at:*
>
> $$r_k^* = \frac{2\tau_k}{G_k} \quad \text{for each } k = 1, \ldots, K$$
>
> *This point is globally attracting under the gradient dynamics $\dot{\mathbf{r}} = -\mu \nabla V(\mathbf{r})$. The minimum value is:*
>
> $$V(\mathbf{r}^*) = \gamma B_i - \sum_{k=1}^{K} \frac{G_k^2 \mathcal{M}_k}{4\tau_k}$$
>
> *The multi-center Coexistence Band exists if and only if:*
>
> $$\sum_{k=1}^{K} \frac{G_k^2 \mathcal{M}_k}{4\tau_k} > \gamma B_i$$

*Proof.* The multi-center potential separates across the $K$ coupling dimensions: $V(\mathbf{r}) = \sum_k V_k(r_k) + \gamma B_i$ where $V_k(r_k) = \tau_k \mathcal{M}_k / r_k^2 - G_k \mathcal{M}_k / r_k$. Each $V_k$ has a unique minimum at $r_k^* = 2\tau_k/G_k$ with value $-G_k^2\mathcal{M}_k/(4\tau_k)$ (by the single-center analysis). The global minimum is achieved component-wise. Global attraction follows from the Lyapunov function $\mathcal{W}(\mathbf{r}) = V(\mathbf{r}) - V(\mathbf{r}^*)$, whose time derivative satisfies $\dot{\mathcal{W}} = -\mu\|\nabla V\|^2 \leq 0$. The existence condition requires $V(\mathbf{r}^*) < 0$. $\square$

**Corollary 27.1 (Diversification Benefit).** *An agent coupled to $K$ HECs may be viable even if no single HEC has sufficient mass: it is possible that $\mathcal{M}_k < \mathcal{M}_{\min}$ for each $k$ individually, yet $\sum_k G_k^2\mathcal{M}_k/(4\tau_k) > \gamma B_i$. Diversification across centers expands freedom.*

**Physical interpretation:** An individual who cannot survive on one job ($\mathcal{M}_1 < \mathcal{M}_{\min}$) may thrive by combining income streams. A small nation unable to survive in the orbit of one superpower may thrive through diversified trade agreements. The multi-center model formalizes the survival advantage of diversification.

### 7.2 Center Competition for Agents

From the center's perspective, agents in its Coexistence Band contribute to the network (labor, innovation, information) that increases the center's own value mass $\mathcal{M}$. Centers thus compete for agents by adjusting their coupling parameters:

- **Increasing $G$** (better resource sharing) — raises wages, improves public services.
- **Decreasing $\tau$** (reducing dissolution pressure) — granting more autonomy, reducing oppressive constraints.

Both adjustments widen the Coexistence Band and attract agents from competing centers. This formalizes why nations and corporations compete through quality of life, wages, and individual freedoms — it is a rational strategy in the multi-center attractor landscape.

---

## 8. Connection to the Broader Framework

### 8.1 Coupling the Dynamical Model to Game Theory

The discount factor $\delta$ from the repeated game (Definition 20) depends on the agent's planning horizon and environment stability. Agents within the Coexistence Band of a stable HEC have:

- Higher effective $\delta$ (more stable environment → longer effective planning horizon)
- Lower effective cooperation threshold $\delta^*$ (from Proposition 11, since the higher net-energy surplus at the attractor extends effective planning horizons)

This means agents at the cooperative attractor are more likely to sustain cooperation — a **positive feedback loop**: stability → cooperation → more stability.

> **Proposition 11 (Stability–Cooperation Feedback).**
>
> *Let an agent's discount factor depend on its net energy surplus: $\delta(r) = 1 - \exp(-\beta \max(\Pi(r), 0))$ for some $\beta > 0$ (agents with more surplus plan further ahead). Then:*
>
> *(a) $\delta(r)$ is maximized at $r^*$ (the cooperative attractor).*
>
> *(b) $\delta(r^*) > \delta(r)$ for all $r \neq r^*$ in $\mathcal{B}$.*
>
> *(c) If $\delta(r^*) > \delta^*$ (equivalently, $\beta \Pi(r^*) > -\ln(1-\delta^*)$), then $\delta(r) > \delta^*$ throughout a subband of $\mathcal{B}$ centered on $r^*$, where $\delta^*$ is the cooperation threshold from Theorem 11.*

*Proof.* (a)–(b): $\Pi(r)$ is maximized at $r^*$ (by the definition of the attractor). Since $\delta(r) = 1 - e^{-\beta \Pi(r)}$ is strictly increasing in $\Pi(r)$, $\delta$ inherits the maximum. (c): Given $\delta(r^*) > \delta^*$, the fact that $\delta(r) \to 0$ continuously as $r \to r_\pm$ (since $\Pi(r) \to 0$ at the band boundaries) together with the intermediate value theorem gives a subband where $\delta(r) > \delta^*$, centered on $r^*$. $\square$

### 8.2 Coupling to Accumulated Negentropy

The value mass $\mathcal{M}$ is precisely the accumulated negentropy defined in Definition 29:

$$\mathcal{M} = \mathcal{N}(T) = \int_0^T \dot{W}_{\text{order}}(t) \, dt$$

This means the Coexistence Band width is determined by the historical thermodynamic investment in the center. A center that has accumulated more negentropy over time provides wider freedom to its agents. The **Irrationality of Destruction** (Theorem 19) acquires a new dimension here: destroying a high-$\mathcal{M}$ center doesn't just waste accumulated value — it **collapses the Coexistence Bands** of all agents affiliated with that center, catastrophically reducing the freedom of an entire population.

> **Corollary 27.2 (Cascade Collapse from Center Destruction).**
>
> *If a HEC with value mass $\mathcal{M}$ is destroyed ($\mathcal{M} \to 0$), all $N$ agents within its Coexistence Band simultaneously lose viability. The total "freedom destroyed" is:*
>
> $$\mathcal{F}_{\text{lost}} = N \cdot w(\mathcal{M})$$
>
> *This provides an additional argument for the Irrationality of Destruction (Theorem 19): the social cost of center destruction includes the collapse of the entire affiliated population's viable coupling space.*

### 8.3 Coupling to Rights as Constraints

The coupling distance $r$ can be mapped to the constraint structure of the Lagrangian constraints derivation. At smaller $r$ (tighter coupling), the HEC imposes more constraints (Definition 2) on the agent's action space, extracting a higher shadow price $\mu_{Bk}^*$ (Theorem 1). The dissolution threshold $r_-$ corresponds to the constraint intensity at which the aggregate shadow price of all HEC-imposed constraints exceeds the agent's utility gain from resource access:

$$\sum_{k=1}^{m} \mu_k^*(r_-) = U_i(\mathbf{x}_i^*) - U_i(\mathbf{0})$$

At this point, the constraints consume all of the agent's surplus — its optimization space is so restricted that cooperation yields zero net benefit.

---

## 9. Worked Examples

### 9.1 Individual vs. Corporation

**Setup:** An individual agent (worker) with boundary integrity $B = 1$ (normalized), entropy leakage $\gamma = 0.1$, near a corporation with value mass $\mathcal{M} = 100$ (normalized energy units). Coupling parameters: $G = 1.0$ (resource access), $\tau = 0.5$ (dissolution coupling).

**Calculations:**

- Cooperative attractor: $r^* = 2\tau/G = 1.0$
- Minimum viable mass: $\mathcal{M}_{\min} = 4\gamma B \tau / G^2 = 4(0.1)(1)(0.5)/1 = 0.2$ — the corporation far exceeds the threshold.
- Discriminant: $\Delta = G^2\mathcal{M}^2 - 4\gamma B \tau \mathcal{M} = 100^2 - 4(0.1)(1)(0.5)(100) = 10000 - 20 = 9980$
- Inner boundary: $r_- = (100 - \sqrt{9980})/(2 \cdot 0.1 \cdot 1) = (100 - 99.90)/0.2 \approx 0.50$
- Outer boundary: $r_+ = (100 + 99.90)/0.2 \approx 999.5$
- Bandwidth: $w \approx 999.0$ — extremely wide freedom band.
- Net energy at attractor: $\Pi(r^*) = G^2\mathcal{M}/(4\tau) - \gamma B = 100/(2) - 0.1 = 49.9$

**Interpretation:** The corporation is so massive relative to the individual that the freedom band is enormous — the worker has a wide range of viable engagement levels. The risk is not starvation (the outer boundary is far away) but dissolution: if the worker takes on excessive obligations ($r < 0.50$), assimilation begins.

### 9.2 Citizen vs. State

**Setup:** A citizen with $B = 2$ (higher complexity — education, social connections), $\gamma = 0.05$ (stable social environment), near a state with $\mathcal{M} = 500$. Coupling: $G = 1.5$, $\tau = 1.0$ (states impose more assimilation pressure than corporations).

- $r^* = 2(1.0)/1.5 \approx 1.33$
- $\mathcal{M}_{\min} = 4(0.05)(2)(1.0)/1.5^2 = 0.4/2.25 \approx 0.178$
- $\Delta = (1.5)^2(500)^2 - 4(0.05)(2)(1.0)(500) = 562500 - 200 = 562300$
- $r_- \approx (750 - 749.87)/0.2 \approx 0.67$
- $r_+ \approx (750 + 749.87)/0.2 \approx 7499$
- $w \approx 7498$

**Comparison: Authoritarian vs. Free State.**

An authoritarian state may have higher $\tau$ (more assimilation pressure): $\tau_{\text{auth}} = 3.0$.

- $r^*_{\text{auth}} = 2(3.0)/1.5 = 4.0$ (agents must keep greater distance)
- $\mathcal{M}_{\min,\text{auth}} = 4(0.05)(2)(3.0)/2.25 = 0.533$ (requires more mass to sustain citizens)
- $\Delta_{\text{auth}} = 562500 - 600 = 561900$
- $w_{\text{auth}} \approx \sqrt{561900}/0.1 \approx 7496$

The bandwidth is similar in this regime ($\mathcal{M} \gg \mathcal{M}_{\min}$), but the attractor distance $r^* = 4.0$ vs. $1.33$ means citizens of the authoritarian state must maintain 3× more distance to avoid dissolution — they are structurally pushed further from the center's resources.

### 9.3 Small Nation vs. Superpower

**Setup:** A small nation (agent) with $B = 50$, $\gamma = 0.02$, near a superpower with $\mathcal{M} = 10{,}000$. Coupling: $G = 0.5$ (trade only), $\tau = 2.0$.

- $r^* = 2(2.0)/0.5 = 8.0$
- $\mathcal{M}_{\min} = 4(0.02)(50)(2.0)/0.25 = 32$
- $\Delta = 0.25(10^8) - 4(0.02)(50)(2.0)(10^4) = 25{,}000{,}000 - 80{,}000 = 24{,}920{,}000$
- $w = \sqrt{24920000}/(0.02 \times 50) = 4992.0/1.0 \approx 4992$

If the superpower increases assimilation pressure ($\tau \to 5$):

- $r^* = 20$ (nation must keep much greater distance)
- $\mathcal{M}_{\min} = 80$ (still viable, but threshold quintupled)
- Bandwidth shrinks modestly but the viable zone shifts outward.

**Interpretation:** Small nations maintain sovereignty by keeping sufficient coupling distance from superpowers — trade and cooperation at arm's length, not full integration. When a superpower increases its assimilation pressure (military threats, economic coercion), the optimal distance increases and the inner boundary (dissolution threshold) moves outward, shrinking the small nation's options.

---

## 10. Summary of Results

### Definitions Introduced

| # | Name | Description |
|---|---|---|
| 35 | High-Energy Center (HEC) | Network node with accumulated value mass $\mathcal{M}$ |
| 36 | Coupling Distance | Generalized coordinate $r \in (0, \infty)$ measuring agent independence |
| 37 | Coexistence Potential | $V(r) = \tau\mathcal{M}/r^2 - G\mathcal{M}/r + \gamma B_i$ |
| 38 | Cooperative Attractor | $r^* = 2\tau/G$, the minimum of $V(r)$ |
| 39 | Potential Well Depth | $D = G^2\mathcal{M}/(4\tau)$ |
| 40 | Dissolution Threshold | Inner boundary $r_-$ of the Coexistence Band |
| 41 | Starvation Threshold | Outer boundary $r_+$ of the Coexistence Band |
| 42 | Stable Coexistence Band | $\mathcal{B} = (r_-, r_+)$ where $V(r) < 0$ |
| 43 | Boundary Degradation Rate | $D_{\text{assimilate}}(r) = \sigma\mathcal{M}/r^3$ |
| 44 | Boundary Regeneration Rate | $R_{\text{repair}}(r) = \rho \max(\Pi(r), 0)$ |
| 45 | Multi-Center Coexistence Potential | Superposition of single-center potentials |

### Theorems, Propositions, and Corollaries

| # | Name | Statement (brief) |
|---|---|---|
| **Theorem 22** | Stability of the Cooperative Attractor | $r^*$ is globally attracting under gradient dynamics |
| **Theorem 23** | Existence of the Coexistence Band | Band exists iff $\mathcal{M} > \mathcal{M}_{\min} = 4\gamma B_i \tau / G^2$ |
| **Theorem 24** | Freedom Bandwidth Theorem | $w = \sqrt{\Delta}/(\gamma B_i)$; comparative statics |
| **Theorem 25** | Irreversibility of Dissolution | Below $r_d$, boundary integrity reaches zero in finite time |
| **Theorem 26** | Starvation Spiral | Beyond $r_+$, agents starve exponentially |
| **Theorem 27** | Multi-Center Cooperative Attractor | Separable optimization; diversification benefit |
| **Proposition 8** | Properties of Coexistence Potential | Unique minimum, boundary behavior, smoothness |
| **Proposition 9** | Value Mass Comparative Statics | $\mathcal{M} \uparrow$ widens band, deepens well |
| **Proposition 10** | Boundary Integrity Comparative Statics | $B_i \uparrow$ narrows band, raises $\mathcal{M}_{\min}$ |
| **Proposition 11** | Stability–Cooperation Feedback | Agents at $r^*$ sustain cooperation more easily |
| **Corollary 22.1** | Resilience of Equilibrium | Perturbations self-correct |
| **Corollary 24.1** | Freedom Is Finite | Infinite freedom impossible with finite $\mathcal{M}$ |
| **Corollary 24.2** | Inequality of Freedom | Higher-$B_i$ agents have narrower bands |
| **Corollary 25.1** | Assimilation Trap | Viable energy but declining boundary |
| **Corollary 27.1** | Diversification Benefit | No single center sufficient, but combination works |
| **Corollary 27.2** | Cascade Collapse | Center destruction eliminates all affiliates' freedom |
| **Lemma 2** | Attractor Containment | $r_- < r^* < r_+$ whenever band exists |

---

## 11. Notation Reference

| Symbol | Meaning |
|---|---|
| $\mathcal{M}$ | Value mass of HEC (accumulated negentropy, J) |
| $r$ | Coupling distance (dimensionless) |
| $r^*$ | Cooperative attractor: $2\tau/G$ |
| $r_-$ | Dissolution threshold (inner boundary) |
| $r_+$ | Starvation threshold (outer boundary) |
| $r_d$ | Boundary dissolution threshold (structural) |
| $G$ | Resource coupling coefficient |
| $\tau$ | Dissolution coupling coefficient |
| $\sigma$ | Assimilation intensity coefficient |
| $\rho$ | Repair allocation fraction |
| $\gamma$ | Entropy leakage rate (from thermodynamic friction derivation) |
| $B_i$ | Boundary integrity (from thermodynamic friction derivation) |
| $V(r)$ | Coexistence potential |
| $\Pi(r)$ | Net energy rate: $-V(r)$ |
| $\mathcal{M}_{\min}$ | Minimum viable HEC mass |
| $w$ | Freedom bandwidth: $r_+ - r_-$ |
| $D$ | Potential well depth: $G^2\mathcal{M}/(4\tau)$ |
| $\Delta$ | Discriminant: $G^2\mathcal{M}^2 - 4\gamma B_i \tau \mathcal{M}$ |
| $\mu$ | Agent adjustment rate (mobility) |
| $\beta$ | Surplus-to-horizon conversion rate (Proposition 11) |
| $\mathcal{B}$ | Stable Coexistence Band: $(r_-, r_+)$ |
| $K$ | Number of HECs in multi-center model |

> **Symbol disambiguation.** In this file: $r$ = coupling distance, $\sigma$ = assimilation intensity, $\rho$ = repair allocation fraction, $\mu$ = agent adjustment rate. In other derivation files, $r$ denotes contest decisiveness (thermodynamic friction) or time-preference rate (game theory); $\sigma$ denotes conflict effectiveness (thermodynamic friction), survival probability (game theory), or search efficiency (information-negentropy Part B); $\rho$ denotes redundancy factor (information-negentropy Part A) or specific information density (Part B); $\mu$ denotes KKT multipliers $\mu_{Bk}^*$ (Lagrangian constraints). Context and subscripts distinguish these uses.