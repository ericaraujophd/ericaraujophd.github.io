# Bavinck-Inspired ABM: Belief–Belonging–Behavior (BBB)

This pseudocode outlines an agent-based model that operationalizes Bavinck’s categories:
- **Organic worldview** → embedded agents & emergent culture
- **Unity of truth** → multi-model toggles (different decision rules)
- **Imago Dei** → relational agents with layered states (belief, belonging, behavior)
- **Sin & grace** → dual dynamics (polarization vs. reconciliation)
- **Common grace** → stabilizing cross-group norms & institutions
- **Plurality** → heterogeneous agent types and perspectives

---

## Entities
- **Agents**: `id`, `group`, `belief`, `trust`, `mood`, `behavior`, `openness`, `status`
- **Networks**: social ties (homophily vs. cross-group), institutional ties (church, school, workplace)
- **Environment**: patches with `institution_norm` and `memory`
- **Globals**: `common_grace_strength`, `polarization_pressure`, `reconciliation_prob`, `norm_strength`, `shock_frequency`

---

## Initialization (`setup()`)
1. Create `N` agents.
2. Assign each to a `group` (e.g., A/B/C) with initial `belief` mean per group.
3. Set `trust` (random or group-based), `openness` (heterogeneity), `mood` (neutral).
4. Generate networks:
   - Local lattice or spatial proximity.
   - Add homophilous ties with prob `p_homo`.
   - Add cross-group ties with prob `p_cross = f(common_grace_strength)`.
5. Place institutions on patches with `institution_norm` in [0,1].
6. Initialize `norm_strength` and `polarization_pressure`.
7. Record baseline metrics.

---

## Step (`go()`)
For each tick:
1. **Encounter Selection**
   - Each agent selects k neighbors by weighted probability:
     - higher weight for strong ties & same-group (homophily)
     - *but* cross-group boosted by `common_grace_strength`

2. **Interaction Dynamics** (Dual: Sin & Grace)
   - Compute **influence** from neighbor’s belief (bounded confidence) and trust.
   - If perceived **threat** (belief distance > threshold & low trust):
     - increase `polarization_pressure`, decrease trust, amplify homophily.
   - Else (constructive encounter):
     - update beliefs by weighted averaging; increase trust; reduce polarization.

3. **Institutional Mediation (Common Grace)**
   - With probability proportional to `institution_norm * common_grace_strength`:
     - trigger **reconciliation** micro-event between cross-group neighbors:
       - temporary trust boost
       - small convergence of belief
       - creation/reinforcement of cross-group tie

4. **Behavior Update**
   - Agents choose behavior (cooperate / withdraw / oppose) as a function of:
     - belief extremity, trust, group norm, and current mood.
   - Optional: include moral actions (forgive/help/share) with prob rising in high-trust contexts.

5. **Norm & Memory Update**
   - Patch memory aggregates recent local cooperation vs. opposition.
   - `institution_norm` drifts toward observed cooperation (positive feedback) but decays if conflict persists.

6. **Shocks (Scenario Testing)**
   - With frequency `shock_frequency`, introduce events (media scandal, crisis):
     - increase threat perception, or
     - mobilize institutions for peacemaking (depending on scenario).

7. **Metrics**
   - Polarization index: variance of beliefs + modularity of networks.
   - Reconciliation rate: cross-group trust increases per tick.
   - Common-good index: mean cooperation weighted by diversity.
   - Fragility: probability of cascade into opposition after a shock.

---

## Experiments
- Vary `common_grace_strength` from 0 → 1 and measure steady-state polarization.
- Toggle decision rule: **utilities** vs. **norms** vs. **identity** dominance.
- Start with strong homophily vs. strong cross-ties.
- Introduce asymmetric groups (size or openness asymmetry).
- Add institutional failures (drop `institution_norm`) and observe tipping points.

---

## Validation / Calibration
- Stylized facts: polarization rises with homophily + shocks; falls with cross-group norms.
- Sensitivity analysis: sweep thresholds, learning rates, and trust dynamics.
- Use empirical survey priors (group means, variances) when available.

---

## Output / Visuals
- Time series: polarization, cooperation, reconciliation.
- Spatial maps: institution_norm heat, conflict clusters.
- Network views: cross-group edges, modularity over time.
