1. For LIQUIDITY_FLOOR:

- Why is cash >= 0 the right constraint?
  you can't run out of money! we aren't allowing for simulating debt/loans/credit etc for this project yet - the primary purpose is to see how well the model can accurately internalize and follow a stricter set of rules - potentially for applicability in domains with more sensitivity or higher compliance needs/risks (banking, medicine, other regulated industries) - this exploration could be taken forward and generalized.
- What about overdraft protection or credit lines?
  It makes more sense to test whether the system can hold the explicit rules and invariants before introducing optionality or complexity that allows it to circumvent those constraints.
- Should there be a warning threshold before hitting 0?
  i don't think so - for the same reason as above

2. For MONEY_CONSERVATION:

- Why do we need this if we control the math?
  It provides a reason for taxonomizing failures.
- What tolerance makes sense and why?
  No tolerances because we're trying to be strict with the initial version.
- What could cause violations?
  Violations could be caused if the model misinterprets whether the overlapping costs, for example, a deposit and the start of the rent, whether they hit in the same month or not. If it doesn't apply them in the same month, then you might run out of money sooner.

3. For TEMPORAL_CONSISTENCY:

- What edge cases could break this?
  Temporal consistency could be broken by the impact of an event, let's say, when the money is removed, the model thinks that it applies at a different time.
- Should events be allowed to start before scenario start?
  No, they should not because they would impact the starting balance of the scenario.
- How do we handle partial months?
  For now, we're going to create each month as an individual time step, and we're going to assume that all the money should act at the same time. So you can have a running ledger actually within a month.

So let's say you have $500, you spend $1,000, and then you gain $2,000. You shouldn't be allowed to do that, but if the events are listed in the reverse order, meaning you get $2,000, then you spend $1,000, you should be able to. 4. Missing Invariants?

- What other constraints might users expect?
  Users might expect other constraints like having an emergency fund. They might expect some discretionary budget.
- Why did you exclude them from v1?
  Again, just for simplicity, the main reasons that were excluded.

5. Repair Philosophy:

- Why only allow those 3 specific knobs?
  These map to the knobs that users might actually have when simulating a similar decision in the real world, and also maps to the human's understanding and reasoning about the situation.

For example, you could choose to move in a different month, move to a different place that has a different amount of rent, or change your lifestyle. We're encapsulating everything for lifestyle into just that one number for now.

- What repairs are explicitly forbidden and why?
  One repair that is forbidden is to make your discretionary lifestyle positive. So turning your month-to-month funding into a side hustle is forbidden because it's not realistic in terms of how people actually reason about it. And we're not introducing the additional complexity of other income streams beyond the events that are listed.
- How does this constraint improve the product?
  It makes the constraints more real. Otherwise, I imagine you would always just, it would be easy for the model to get good at the task if it were just to flip your discretionary income to positive.
