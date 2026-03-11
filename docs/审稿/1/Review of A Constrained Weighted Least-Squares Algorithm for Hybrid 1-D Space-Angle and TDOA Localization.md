
# Review of "A Constrained Weighted Least-Squares Algorithm for Hybrid 1-D Space-Angle and TDOA Localization"

**Paper ID:** 331-20715

---

## General Comments

**The paper proposes a CWLS algorithm for 3-D target localization using hybrid 1-D space-angle (1-D SA) and TDOA measurements. The geometric constraint between an auxiliary range variable and the true target position is enforced via Lagrange multipliers, reducing to roots of a sixth-degree polynomial. The authors report RMSE improvement over Hu et al.'s WLS and Xing et al.'s TSWLS, with near-CRLB performance under low noise.**

**The motivation is solid. Compact linear arrays on size-constrained platforms—UAVs being the obvious example—face a real tradeoff between aperture and form factor, and the hybrid SA+TDOA geometry is a reasonable way to work around it. The CWLS-Lagrange framework has been applied to AOA-TDOA localization for some time, and extending it to 1-D SA measurements is not inherently wrong.**

**Three problems undercut the contribution, and they are substantial enough to require major revision:**

1. **The novelty is thinner than claimed.** The methodology follows the authors' own prior work [20] for AOA-based hybrid localization. Moving from AOA to 1-D SA means working with conical measurement surfaces instead of planes, but the paper never shows what new technical challenge this geometry creates or how the CWLS framework adapts beyond a substitution of one measurement model for another.
2. **The theoretical analysis is absent.** There is no discussion of consistency, asymptotic efficiency, or the conditions under which the algorithm converges to the CRLB. "Near-CRLB performance" backed only by simulation in one scenario is not an established result.
3. **The writing has real errors** — not cosmetic ones. At least one notation conflict between Eq. (1) and Algorithm 1 (the θ/ϕ parameterization is swapped), a definition error in the notation table ("0_{M,1} denotes the column vector of M ones" should be zeros).

**My recommendation is ****major revision**.

---

## Specific Comments

**PP 1, Notation box:** "0*{M,1} denotes the column vector of M ones" — this should be zeros. If the authors mean a vector of ones, the symbol should be 1*{M,1}. Please correct and check the surrounding usage.

**PP 1, Par 4 (Prior work):** The discussion of [7]–[11] is useful, but the authors need to draw a sharper line between what [20] does and what this paper adds. Currently the technical gap is not visible.

**PP 1, Par 5:** The paper criticizes [18] for ignoring the intrinsic constraint and [19] for high-noise degradation, but the proposed method also linearizes — squaring the TDOA equations and applying a first-order Taylor expansion on the SA noise model (Eq. 5). It is not immune to the same issues. The discussion of limitations should be balanced.

**PP 1, Par 7:** "In Section III, presents the derivation" and "In Section IV, provides comprehensive simulation results" — both sentences are missing subjects. "Section III presents…" and "Section IV provides…"

**PP 2, Par 2:** "The measured 1-D SA for the i th sensor given by" → "The measured 1-D SA for the i-th sensor is given by."

**PP 2, Eq. (5):** The approximation cos(ψᵢ − eᵢ) ≈ cos ψᵢ + eᵢ sin ψᵢ requires small eᵢ. State this explicitly and discuss the validity range. The performance gap at high noise (visible in Figs. 2–3) likely traces back to this step.

**PP 2, Eq. (9):** "Squaring both sides and ignoring second-order noise terms" is the critical approximation step and deserves more than one clause. The noise levels tested (σ_d up to 10 dB·m) are large enough that the ignored terms may contribute non-trivially to bias. Quantify or discuss.

**PP 4, Algorithm 1, Step 1 — critical:** In Algorithm 1 (line 1), the direction vector is gᵢ = [cos ϕᵢ cos θᵢ, sin ϕᵢ cos θᵢ, sin θᵢ]ᵀ. Equation (1) gives gᵢ = [cos θᵢ cos ϕᵢ, sin θᵢ cos ϕᵢ, sin ϕᵢ]ᵀ. The roles of θ and ϕ are swapped. This is not a notational variant — it is a different parameterization. This must be corrected and the implementation should be verified against it.

**PP 4, Comparison methods:** SDP-based methods [7], [9], [10] are cited in the introduction as the computational baseline but absent from the results. Either include them or explain why they are inapplicable to the hybrid SA+TDOA setup.

**PP 4, Computational cost:** The paper motivates the CWLS approach partly on efficiency grounds relative to SDP methods. There is no timing table. Add one.

**PP 4, Figs. 2–3:** State explicitly how CRLB-Hybrid is derived (Fisher information matrix combining both measurement types?). The performance gap between the proposed method and CRLB at high noise is visible but not discussed — quantify it, and connect it to the approximations in Eqs. (5) and (9).
