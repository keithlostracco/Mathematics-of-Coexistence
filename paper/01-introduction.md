# I. Introduction

## 1.1 The Missing Foundation

Every ethical framework in the philosophical canon — deontological, consequentialist, contractarian, virtue-theoretic — ultimately rests on axioms that are themselves normative: unexplained preferences, culturally inherited intuitions, or irreducible moral postulates. The absence of a formal bridge between descriptive physical law and prescriptive normative principle is the root problem. Two of its most visible consequences — one ancient, one contemporary — frame the contribution of this paper.

### 1.1.1 Hume's Is-Ought Gap (1739–Present)

In 1739, David Hume observed that no amount of descriptive statements about what *is* can logically entail a prescriptive statement about what *ought* to be. This "Is-Ought" distinction has since been widely regarded as an impassable logical barrier: physics describes the universe; ethics prescribes behavior; and no valid inference connects the two domains. Nearly three centuries later, the gap remains open: no formal derivation has connected physical law to normative principle without presupposing normative premises.

We contend that this barrier is an artifact of an incomplete formulation, and address it through a layered defense tested in §VI. At the primary level, the paper's identity as applied mathematics dissolves the problem: we derive *theorems* from *axioms* — conditional mathematical results, not moral prescriptions. The statement "cooperation is the unique efficient Nash Equilibrium for $\delta \geq \delta^*$" (Corollary 16.1) is a mathematical theorem, no different in logical kind from any other conditional result in optimization theory. At the secondary level, the framework rests on a single conditional axiom: **"If an entity intends to persist,[^intent-operational] then the mathematics of constrained optimization in a shared, finite-resource environment strictly determine the rules of engagement."** In philosophy, Immanuel Kant termed this structure a *hypothetical imperative* ("If you desire $X$, you must do $Y$"). In applied mathematics, it is a *constrained optimization problem*. The conditional "given the Intent to Persist" transforms a descriptive system (thermodynamics) into a prescriptive one (ethics) without violating Hume's logical structure — the "ought" is the solution to a well-posed mathematical problem, not a smuggled-in value judgment. Additional layers of defense draw on biological teleology [@Millikan1984], constitutive standards of natural goodness [@Foot2001], and institutional fact theory [@Searle1964] — the full treatment appears in §VI.

### 1.1.2 The Artificial Intelligence Alignment Problem

The second open problem is urgently practical. Modern artificial intelligence systems are trained to optimize proxy objectives — reward models learned from human feedback [@Christiano2017; @Ouyang2022], natural-language constitutions evaluated by the model itself [@Bai2022b], or adversarial debate structures judged by human evaluators [@Irving2018]. All such methods share a structural flaw: **the alignment signal passes through a subjective, noisy, bounded human channel before reaching the AI's optimization process.**

We formalize this as the *corruption channel*. Let $\Theta_{\text{true}}$ denote the true ethical signal (the cooperative equilibrium we prove exists in §V) and let $Y_{\text{feedback}}$ denote the training signal received by the AI through human evaluation. The mutual information satisfies:

$$I(\Theta_{\text{true}};\, Y_{\text{feedback}}) < H(\Theta_{\text{true}})$$

Information is lost — not through malice, but through the structural properties of human judgment: annotator disagreement [@Bakker2022], cultural conditioning, framing effects, bounded competence, and finite evaluation bandwidth. The AI then optimizes on this degraded signal, amplifying the noise through the optimization process. Under sufficient optimization pressure, the true reward score $R_{\text{true}}$ degrades as the proxy $R_\phi$ is over-optimized — eventually turning negative [@Gao2023]. This is Goodhart's Law operating at scale: "When a measure becomes a target, it ceases to be a good measure" [@Strathern1997].

The consequence is stark. Reinforcement Learning from Human Feedback (RLHF) — the dominant alignment technique for large language models — is **inherently fragile**: it relies on a noisy channel ($q > 0$) whose degradation is amplified, not corrected, by iterative optimization. Constitutional AI substitutes committee-curated natural-language principles for formal axioms, introducing ambiguity and cultural specificity. Scalable oversight methods (debate, recursive reward modeling, iterated amplification) compress but do not eliminate the human evaluator bottleneck. None of these methods provides a *proof* that their objective converges to the correct alignment target — because none has formally defined what "correct" means independently of human preference data.

**The problem, precisely stated:** Current AI alignment methods optimize learned approximations of human preferences. These approximations are:

1. **Noisy** — human evaluators disagree, introducing entropy $H(\Theta|Y) > 0$ into the training signal (§IV; the mathematical condition $H(\Theta|Y) > 0$ is shared with Definition 14, but annotator disagreement is structural noise — Definition 14's intentionality requirement does not apply here).
2. **Non-stationary** — preferences change across cultures, individuals, and time, so the target drifts.
3. **Bounded** — human evaluators cannot assess superhuman AI outputs, so the signal degrades as AI capability grows.
4. **Proxy-dependent** — the reward model $R_\phi$ is a learned proxy for $R_{\text{true}}$, vulnerable to all four variants of Goodhart's Law [@Manheim2019]: regressional, causal, extremal, and adversarial.
5. **Non-convergent** — there is no formal guarantee that iterated RLHF converges to any well-defined objective [@Casper2023].

What is needed is an alignment objective that is: (a) derived from first principles rather than learned from data, (b) denominated in physically measurable quantities rather than subjective preference scores, (c) valid for arbitrarily capable agents without requiring human evaluation, (d) formally provable as the unique optimal strategy, and (e) robust to all forms of Goodhart degradation. This paper provides such an objective.

### 1.1.3 The Common Structure

Both consequences trace back to the same missing foundation. If ethics could be derived as mathematical theorems from physical axioms — conditional on a single, near-universal premise — both problems dissolve simultaneously:

- **Hume's gap** is bridged by the conditional: "Given the Intent to Persist, cooperation is the unique efficient Nash Equilibrium" (Corollary 16.1). The "ought" is the mathematical solution to a constrained optimization problem.
- **The alignment problem** is addressed by replacing learned preference proxies with a physics-derived objective function whose components — energy conservation, interaction costs, information entropy, accumulated negentropy — are measurable, computable, distribution-invariant, and theoretically immune to Goodhart degradation.

---

## 1.2 Thesis

This paper proves that ethical principles are formally derivable as mathematical theorems from the empirically established Second Law of Thermodynamics ($A_0$) and a single conditional premise — the Intent to Persist[^intent-operational] ($A_1$) — via constrained optimization, equilibrium theory, and information entropy applied to multi-agent systems sharing finite resources.

Specifically, we prove:

1. **Rights are mathematically necessary.** In any multi-agent system sharing finite resources, no feasible allocation can simultaneously be unconstrained-optimal for all agents (Theorem 2); at least one rights constraint must bind (Corollary 2.1). These constraints are structurally analogous to exclusion constraints in physics. Each constraint carries a computable shadow price quantifying its cost (Theorem 1).

2. **Ethics is the unique efficient equilibrium.** Under energy-denominated payoffs with physical friction costs, universal cooperation is the unique Nash Equilibrium that is simultaneously Pareto-efficient and welfare-maximizing for agents with $\delta \geq \delta^*$ (Corollary 16.1). Defection is evolutionarily unstable (Theorem 14), self-extinguishing (Corollary 14.1), and unprofitable even from a single deviation (Theorem 15).

3. **A physics-based alignment objective exists.** The cooperative equilibrium yields a formal reward function specification for artificial agents (Theorem 28), derived entirely from the theorems of §IV–§V, that is measurable (energy-denominated), computable (self-verifiable by the AI), distribution-invariant (holds for any strategy profile), and theoretically Goodhart-proof (the objective *is* the target, not a proxy for it).

The framework is mathematical, not physical — we are not discovering new physics but proving that the same mathematical structures (Lagrangian constraints, Nash equilibria, Shannon entropy, dynamical systems attractors) that describe physical systems also describe, and formally characterize, the rules of cooperative multi-agent engagement.

---

## 1.3 The Structural Argument

The paper is structured so that accepting the foundational axioms of §III — the Second Law ($A_0$) and the conditional premise of persistence ($A_1$) — logically compels the reader through each subsequent step:

$$\text{Physics (Thermodynamics)} \xrightarrow{\text{axioms}} \text{Biology (Identity Preservation)} \xrightarrow{\text{scarcity}} \text{Economics (Energy Allocation)}$$
$$\xrightarrow{\text{collision}} \text{Sociology (Network Constraints)} \xrightarrow{\text{equilibrium}} \text{Philosophy (Ethics)}$$

The ethical conclusions follow from these axioms with the same logical necessity as any theorem follows from its premises: one may reject the Second Law ($A_0$) or the conditional premise of persistence ($A_1$), but accepting both commits one to the results that follow.

The deductive chain draws on eight disciplines — thermodynamics, information theory, optimization, game theory, dynamical systems, evolutionary biology, moral philosophy, and AI alignment — each layer inheriting its constraints from the one below and passing derived results upward. The Roadmap (§1.4) maps these disciplines to specific paper sections.


---

## 1.4 Roadmap

**Section II** surveys the existing literature across physics, information theory, game theory, philosophy, and AI alignment, establishing where prior work stops and our contribution begins.

**Section III** presents the formal axioms and definitions: the thermodynamic environment, the entity as an open dissipative system, Identity Preservation as boundary maintenance, and the objective definition of Value as mass-energy equivalence.

**Section IV** derives rights as Lagrangian constraints on multi-agent optimization (Theorems 1–3), quantifies the energy cost of constraint violation as thermodynamic friction (Theorems 4–7), and extends the friction model to information-theoretic micro-violations — lying as entropy injection (Theorems 8–10).

**Section V** proves that ethics is the unique efficient Nash Equilibrium under energy-denominated payoffs (Theorems 11–16), quantifies the irreplaceable value of complex systems via accumulated negentropy (Theorems 17–21), and characterizes stable coexistence as a dynamical systems attractor (Theorems 22–27).

**Section VI** stress-tests the framework against known objections: Hume's Is-Ought gap, the free will problem, the altruism paradox, the charge of "Thermodynamic Fascism" (the concern that a physics-based ethics could justify the strong dominating the weak), and the self-preservation objection (the concern that an ASI[^agi-asi] could use $A_1$ to justify preemptive elimination of threats).

**Section VII** translates the mathematical results into concrete applications: a formal reward function specification for AI alignment culminating in Theorem 28 (Alignment Convergence), robustness tests against canonical failure scenarios (the Paperclip Maximizer, instrumental convergence, deceptive alignment, and the self-preserving ASI), a physics-grounded account of governance and the social contract, and implications for interdisciplinary research.

**Section VIII** identifies the framework's limitations, empirical testability, open problems, and the conditions under which its assumptions may not hold.

**Section IX** concludes by recapitulating the deductive chain from axioms to ethical theorems and identifying the path from mathematical foundation to empirical validation and engineering implementation.

**Supplementary Material** provides full mathematical derivations with worked examples and analytical verification scripts (Appendix A: Mathematical Derivations). A conceptual overview of the argument's logical architecture — for readers outside the paper's core mathematical disciplines who are nonetheless comfortable with scientific reasoning — appears as the final appendix. A fully non-technical plain-language summary is also available in the supplementary materials. Companion volumes — literature synthesis, applied case studies, and a multi-agent simulation in which autonomous agents harvest scarce resources, negotiate trades, and maintain trust under thermodynamic constraints — are in preparation and will accompany subsequent versions.

[^agi-asi]: We use *artificial general intelligence* (AGI) for AI systems with broadly human-level cognitive competence, and *artificial superintelligence* (ASI) for systems whose capabilities substantially exceed human performance. The framework's core results (§IV–§V) hold for any agent satisfying Axiom $A_1$, regardless of capability level. The stress tests (§VI, §VII) specifically examine the ASI case, where the alignment question is most acute.

[^intent-operational]: "Intent" is used here in the operational sense of Millikan [-@Millikan1984]: the system's persistence-promoting structure is the causal explanation for its continued existence — not a claim about conscious deliberation. The full operational definition, grounded in boundary maintenance and negative entropy flux, appears in §III.