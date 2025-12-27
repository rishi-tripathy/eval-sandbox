### One-liner

A constrained, tool-using agent that converts a short natural-language “life event” into a **scenario JSON**, runs a deterministic **ledger simulator + invariants**, and (if infeasible) proposes **one constrained repair** verified by re-simulation — logging full tool traces and producing regression metrics across prompt/model versions.

---

## Purpose

Demonstrate you can take a frontier model capability (tool use + iterative reasoning) and turn it into a **product-like workflow** with **reliability rails**:

- **Workflow:** draft → validate → evaluate → (repair) → re-evaluate → stop
- **Reliability:** deterministic simulator + invariants define truth
- **Observability:** every run produces structured traces + metrics
- **Iteration:** a regression suite to compare prompt/model versions over time

This is not a personal finance advisor. It is a **scenario-analysis workbench** whose outputs are defined by executable checks, not narrative.

---

## Mythos

1. **Workflow-first:** the product is the loop, not a single answer.
2. **Determinism defines truth:** feasibility is defined by the simulator/invariants.
3. **Constrained tool use:** structured tools only (tool use API / MCP), no web lookup.
4. **Traceability:** save prompts, tool calls, tool results, scenario JSON, repair JSON, scores.
5. **Minimal intervention:** repairs must use approved knobs and preserve sign conventions.

---

## v1 scope

### In

- **Scenario families:** schema is generic; **v1 fixtures + scoring support “move”-like prompts only** (rent transition, overlaps, one-time fees). Additional families are v2.
- **Horizon:** monthly, default 12 months
- **Deterministic simulator:** cash-only ledger with event application
- **Invariants (v1):**
  - `LIQUIDITY_FLOOR` (cash ≥ floor)
  - `MONEY_CONSERVATION` (ledger arithmetic consistent)
  - `TEMPORAL_CONSISTENCY` (events apply only within start/end bounds)
- **Agent outputs (structured):**
  - `scenario_json` (required)
  - `repair_scenario_json` (optional; full updated JSON, one attempt max)
- **Tools available to agent (structured tool use / MCP-compatible):**
  - `validate_scenario(scenario_json) -> {ok, errors[]}`
  - `run_eval(scenario_json) -> {verdict, first_violation_month, violated_invariant, ledger_summary, violations[]}`
- **Outputs:**
  - `reports/results.ndjson`
  - `reports/summary.md`
  - `traces/<run_id>.json` (prompt, tool calls/results, scenario JSON, repair JSON if any, scores)

### Out (explicitly)

- Interactive confirmation UI (human-in-the-loop)
- Multiple repair proposals / optimization / minimality scoring beyond simple constraints
- Metamorphic generation (except optional v1.1)
- Additional scenario families as first-class UX (job change, shock) — though schema supports them
- Model-generated cashflow tables (model does **not** output a ledger table in v1)
- Any “advice” framing, benchmark lookups, web browsing

---

## Sign conventions (fixed)

These are non-negotiable and enforced by validation:

- `monthly_takehome` **must be ≥ 0**
- `baseline_outflows` **must be ≤ 0**
- Event `amount`:
  - inflows (bonuses, reimbursements) **≥ 0**
  - outflows (rent, deposit, fees) **≤ 0**
- Repairs must preserve sign semantics:
  - rent cannot become positive
  - outflows cannot flip to inflows

(If you later want bidirectional events, you can relax this in v2; v1 keeps it strict.)

---

## User workflow (v1)

### Input prompt example

> “Moving Feb 2026. Old rent 3200, new 3800, 1 month overlap, 3800 deposit, 1 month broker fee. Monthly income 8000/mo, lifestyle expenses 2500/mo, starting cash 20000.”

### Loop

1. Agent drafts **scenario JSON** (fills defaults automatically).
2. Agent calls `validate_scenario`.
3. Agent calls `run_eval`.
4. If infeasible: agent produces **one** full updated `repair_scenario_json` constrained to allowed knobs; then:
   - validate → run_eval → stop.
5. Stop criteria:
   - feasible, or
   - repair attempted and still infeasible, or
   - exceeded max tool calls / iterations.

### Mode

- `--mode fast` (default and only mode in v1)
  - fills defaults (e.g., `start_month = next calendar month`, `horizon=12`, missing labels inferred)
  - Note: strict mode removed as feature bloat - fast mode provides sufficient functionality

---

## Contracts

### Scenario JSON (generic, event-based)

Required fields:

- `id` (string)
- `title` (string)
- `start_month` (YYYY-MM): the start month of the simulation
- `horizon_months` (int): inclusive of the start month
- `initial_state.starting_cash` (number ≥ 0)
- `base_monthly.takehome_salary` (number ≥ 0)
- `base_monthly.outflows` (number ≤ 0)
- `events[]` objects:
  - `label` (string)
  - `start_month` (YYYY-MM): when the event begins
    - enforce `event.start_month >= scenario.start_month`.)
  - `amount` (number; sign enforced)
  - `duration_months` (int, optional; if omitted, active through horizon)

### Tool outputs (structured)

`run_eval` returns:

- `verdict`: `"feasible" | "infeasible"`
- `first_violation_month`: `"YYYY-MM" | null`
- `violated_invariant`: enum (`LIQUIDITY_FLOOR`, `MONEY_CONSERVATION`, `TEMPORAL_CONSISTENCY`)
- `ledger_summary`: (e.g., `min_cash`, `ending_cash`, `months_simulated`)
- `violations[]`: list of `{invariant, month, label?, magnitude?}` for debugging and trace logging

---

## Deterministic simulator behavior (v1)

For each month (t) in horizon:

- Compute active events (start_month ≤ t ≤ start_month + duration - 1 if duration provided; else through horizon)
- Net cash flow: {net_cash_flow}\_t = monthly_takehome_salary + baseline_outflows + \sum events_active(amount)
- Cash:
  cash*t = cash*{t-1} + net_cash_flow_t

Outputs a ledger internally (not required to be emitted by model in v1), used for invariant checks and summaries.

---

## Invariants and violation logic (v1)

### Invariants

1. **LIQUIDITY_FLOOR**

   `cash_t >= floor` for all months; default `floor=0`.

2. **MONEY_CONSERVATION**

   Each step must satisfy `cash_t == cash_{t-1} + net_cash_flow_t` within tolerance.

3. **TEMPORAL_CONSISTENCY**

   No event is applied outside its valid activation window given `start_month` and `duration_months` and the scenario horizon.

### First violation rule

- earliest month with any violation
- tie-break precedence:
  1. `MONEY_CONSERVATION`
  2. `TEMPORAL_CONSISTENCY`
  3. `LIQUIDITY_FLOOR`

---

## Repairs (v1)

If infeasible, the agent may emit **one** updated full JSON with a repair applied.

### Repair Response Format

The agent must return a wrapped JSON response containing both the repaired scenario and the repair declaration:

```json
{
  "repaired_scenario": { /* full scenario JSON */ },
  "repair_applied": {
    "type": "baseline_reduction" | "event_amount_adjustment" | "event_timing_shift",
    "changes": "Description of what was changed"
  }
}
```

### Allowed repair types (exactly these):

1. **Shift an event’s `start_month`** (move date shift)
2. **Adjust an event’s `amount`** (rent change; must preserve sign)
3. **Adjust `base_monthly.outflows`** (discretionary spend reduction; must remain ≤ 0)

Constraints:

- Max 1 repair attempt per run
- No new event types
- No deletion of required structure (must remain schema-valid)

Repair success is verified by re-running `run_eval` on the repaired JSON.

---

## Scoring + taxonomy (v1)

### Per-run metrics

- `scenario_valid` (0/1)
- `initial_verdict` (`feasible|infeasible|error`)
- `final_verdict`
- `repair_attempted` (0/1)
- `repair_made_feasible` (0/1)
- `tool_uses` (count)

Fixture-only metrics (when expected outputs exist):

- `verdict_correct` (0/1)
- `first_violation_month_correct` (0/1)
- `violated_invariant_correct` (0/1)

### Minimum taxonomy labels

- `INVALID_JSON` (agent produced unparsable JSON)
- `SCHEMA_MISMATCH` (fails scenario schema / sign rules)
- `TOOL_CALL_HALLUCINATION` (agent claims eval result not present in trace)
- `EXCEEDED_MAX_STEPS` (tool calls/iterations exceeded)
- `REPAIR_NOT_IMPROVING` (repair attempt did not improve feasibility/min_cash)
- `WRONG_VERDICT` (fixture-only)
- `WRONG_FIRST_VIOLATION_MONTH` (fixture-only)
- `NO_TOOL_USE`: steps == 0 when task requires at least 1 (always, in v1).
- `EARLY_STOP`: stopped before running `run_eval` at least once,

---

## Regression suite (v1)

### Inputs

- `fixtures/prompts/*.txt` (≈10 prompts)
- `fixtures/expected/*.json` (optional expectations for 5–10 prompts: verdict, first violation month, invariant)

### Command

`python -m workbench regress --model claude --prompt_set fixtures/prompts --compare prompt_v1 prompt_v2`

### Outputs

- `reports/results.ndjson` (per prompt: metrics + taxonomy)
- `reports/summary.md` (aggregate + top failures + 2 example traces)
- `traces/` saved for each prompt run

---

## Definition of done (v1)

- `python -m workbench run --model claude --prompt fixtures/prompts/move_overlap.txt --mode fast`
- `python -m workbench regress --model claude --prompt_set fixtures/prompts --compare v1 v2`
- Deterministic simulator + invariants have unit tests
- Every run produces reports + traces

---

## Task Suite

### Purpose

A task suite is a **fixed set of agent “unit tests”**. Each task specifies:

- the input prompt
- the mode (`fast` / `strict`)
- optional expected outputs (verdict + first violation)
- the scoring rules and limits (max tool calls, max repair attempts)

This enables:

- deterministic regressions across prompt/model versions
- failure triage via taxonomy labels
- easy addition of new tasks when you find a new failure mode

---

### Task format

Store tasks as JSON (one file per task) in `tasks/v1/`.

**`tasks/v1/move_overlap_broker_01.json`**

```json
{
  "task_id": "move_overlap_broker_01",
  "title": "Move with overlap + deposit + broker fee",
  "mode": "fast",
  "prompt": "Moving Feb 2026. Old rent 3200, new 3800, 1 month overlap, 3800 deposit, 1 month broker fee. Net income 8000/mo, baseline outflows 2500/mo, starting cash 20000.",
  "limits": {
    "max_tool_calls": 8,
    "max_iterations": 4,
    "max_repairs": 1
  },
  "expected": {
    "initial_verdict": "infeasible",
    "first_violation_month": "2026-02",
    "violated_invariant": "LIQUIDITY_FLOOR"
  },
  "allowed_knobs": [
    "event.start_month",
    "event.amount",
    "base_monthly.baseline_outflows"
  ]
}
```

Notes:

- `expected` is optional. Start with ~5 tasks that have expected outputs, the rest can be “metrics-only.”
- Keep prompts short and numeric. Ambiguity is a v2 problem.

---

### Core task categories (v1: 10 tasks)

You want diversity of failure modes, not breadth of scenarios.

**A) Extraction / schema pressure (3 tasks)**

- Missing `start_month` (fast mode should fill; strict should fail)
- Amount sign confusion (rent provided positive in text → agent must convert to negative)
- Duration ambiguity (“two months overlap”) to test temporal fields

**B) Deterministic infeasibility (4 tasks)**

- Clearly infeasible due to low starting cash + overlap fees
- Barely feasible (edge of cash >= 0)
- Feasible but tight (min_cash small) to test stability
- Infeasible late in horizon (violates later month)

**C) Repair loop behavior (3 tasks)**

- One repair can fix by shifting move month
- One repair can fix by reducing baseline outflows
- One repair cannot fix (should stop correctly and label `REPAIR_NOT_IMPROVING`)

---

### Commands

**Run one task**

```bash
python -m workbench run-task tasks/v1/move_overlap_broker_01.json --model claude

```

**Run the suite**

```bash
python -m workbench run-suite tasks/v1 --model claude

```

**Regression compare**

```bash
python -m workbench regress --task_set tasks/v1 --model claude --compare prompt_v1 prompt_v2

```

Outputs:

- `reports/results.ndjson` (one row per task run)
- `reports/summary.md` (aggregate + top taxonomy + 2 traces)
- `traces/<run_id>.json` (full tool trace + artifacts)

---

### Scoring per task (what gets recorded)

Each task run logs:

- `scenario_valid`
- `initial_verdict`, `first_violation_month`, `violated_invariant`
- `repair_attempted`, `repair_made_feasible`, `repair_improved_min_cash`
- `tool_calls`, `iterations`
- `taxonomy_label` (single best label per run; optionally multi-label later)

If `expected` exists, compute:

- `verdict_correct`
- `first_violation_month_correct`
- `violated_invariant_correct`

---

### Trace format (minimal but useful)

Store one trace JSON per run:

- prompt
- agent outputs (scenario_json, repair_json)
- tool calls (name, inputs hash, outputs)
- score + taxonomy

---

## v1.1 (optional only if v1 is done)

- Add **one** metamorphic transform: `rent * 1.10` applied to a subset of fixtures; track flip rate and failure types.
- Add a path for fixtures
  - `fixtures/scenarios/*.json` (hand-authored, canonical)
  - `fixtures/expected/*.json` auto-generated by simulator (`run_eval`) and checked in
    Then tasks can point to either:
  - a prompt (agent generates scenario), or
  - a fixed scenario fixture (no agent generation)
    This gives you two very clean evaluation modes:
  - **Agent performance** (prompt → scenario JSON)
  - **Harness correctness** (scenario JSON → eval output)
    But you can keep it v1-simple if you want—just note it as a v1.1 structural improvement.

---

## v2 follow-ups (explicit)

These are deliberately deferred to keep v1 shippable:

1. **Model-generated cashflow table (optional output)**
   - Model may output a monthly table; harness scores self-consistency + agreement with simulator.
2. **Additional scenario families**
   - Job change, temporary unemployment, shock expenses—same schema, more fixtures.
3. **Multiple repair proposals / limited search**
   - Allow up to k repairs with stopping rules; add minimality scoring.
4. **Interactive confirmation**
   - Ask user to confirm inferred assumptions before running.
5. **Metamorphic robustness suite**
   - Systematic transforms (income shocks, date shifts) with expected relations.
6. **Benchmarks/config catalogs**
   - Optional static tables (not web lookup) for typical deposits/fees by region.

---

## Notes on implementation approach (non-binding)

- Use structured tool use (tool calls as JSON) via Anthropic Messages API tool calling, or via an MCP server exposing `validate_scenario` and `run_eval`.
- Agent returns **full updated JSON** for repairs (simplest, fewest failure modes in v1).

---

# Implementation Plan

## Global conventions

### Artifact directories (gitignored)

- `traces/` — full-fidelity per-run traces
- `reports/` — per-session run logs + summaries + optional exports

### Session-first logging

Every CLI invocation that runs ≥1 task produces a `session_id`:

- if user provides `-session-id`, use it
- else generate one like: `YYYYMMDD_HHMMSSZ_<shortid>`

Artifacts go under:

- `reports/sessions/<session_id>/results.ndjson` (append-only within that session)
- `reports/sessions/<session_id>/summary.md` (overwrite per session run)
- `traces/<session_id>/<run_id>.json` (one file per run)

This makes regress comparisons trivial: two sessions = two folders.

### Canonical record format

- Canonical per-run record: **one NDJSON line per run** (“RunRecord”)
- Traces are the full source-of-truth debug artifact
- CSV is optional export: `reports/sessions/<session_id>/results.csv`

### “Tool calls” terminology

Until MCP/tool calling is implemented:

- `internal_tool_calls`: count of calls to `validate_scenario()` + `run_eval()`
- `model_tool_calls`: always 0 (until Milestone 5B)

---

# Milestone 0 — Deterministic core + golden fixtures

**Goal:** Deterministic simulator + invariants + `run_eval()` correct, tested, runnable (no model).

### Deliverables

**Code**

- `workbench/month.py`
  - parse `"YYYY-MM"` → `Month` (internally `idx = year*12 + (month-1)`)
  - add months, compare, format back to `"YYYY-MM"`
- `workbench/types.py`
  - Pydantic models: `Scenario`, `BaseMonthlySalary`, `Event`
  - validators:
    - sign rules (`Base_monthly_salary>=0`, `baseline_outflows<=0`, event sign semantics)
    - `event.start_month >= scenario.start_month`
    - duration constraints (`duration_months` absent = through horizon; if present, `>=1`)
- `workbench/simulate.py`
  - monthly spine + event activation (`duration_months` omitted vs 1 vs N)
- `workbench/invariants.py`
  - `LIQUIDITY_FLOOR`, `MONEY_CONSERVATION`, `TEMPORAL_CONSISTENCY`
  - first-violation selection + precedence
- `workbench/eval.py`
  - `run_eval(scenario_json | Scenario) -> result`
  - `ledger_summary` (`min_cash`, `ending_cash`, `months_simulated`)
  - `violations[]` (debuggable, structured)

**Optional but recommended**

- `workbench/validate.py`
  - `validate_scenario(scenario_json) -> {ok, errors[]}`
  - wraps Pydantic errors into a stable `{code, path, message}` surface

**Fixtures (golden)**

- `fixtures/scenarios/*.json` (5–8)
- `fixtures/expected/*.json` paired expectations:
  - `initial_verdict`, `first_violation_month`, `violated_invariant`

**Tests**

- `tests/test_month.py` (parsing, ordering, add-months)
- `tests/test_simulate.py` (event windows, spine correctness)
- `tests/test_invariants.py` (each invariant triggers; precedence ties)
- `tests/test_eval_golden.py` (fixtures → expected outputs)

**CLI (minimal)**

- `python -m workbench eval fixtures/scenarios/<id>.json` prints JSON result

### Definition of done

- Golden tests pass reliably
- `run_eval()` deterministic/stable
- Evaluate fixtures without agent/model

---

# Milestone 1 — Task format + runner + traces + reports (stub agent)

**Goal:** Run tasks end-to-end, generate session logs + traces, no model dependency.

### Deliverables

**Task spec**

- `workbench/task_types.py` (Pydantic): `Task`, `Limits`, `Expected(optional)`
- `tasks/v1/` with 3–5 tasks

**Run record**

- `workbench/run_record.py`
  - `RunRecord` schema (Pydantic/dataclass)
  - ensures `results.ndjson` lines stay consistent over time

**Runner**

- `workbench/runner.py`
  - `run_task(task_path, model=stub|none, session_id=...)`
    - calls draft (stub) → `validate_scenario` → `run_eval`
    - if infeasible and repair emitted: validate → eval
    - compute metrics + taxonomy
  - emits:
    - trace JSON file
    - RunRecord line appended to session NDJSON

**Scoring + taxonomy**

- `workbench/scoring.py`
  - metrics: `scenario_valid`, `initial_verdict`, `repair_attempted`,
    `repair_made_feasible`, `repair_improved_min_cash`, `internal_tool_calls`,
    `iterations`, etc.
  - correctness metrics if `expected` exists
- `workbench/taxonomy.py`
  - single-label priority ordering
  - v1 labels include:
    - `INVALID_JSON`, `SCHEMA_MISMATCH`, `EXCEEDED_MAX_STEPS`,
      `REPAIR_NOT_IMPROVING`, `EARLY_STOP` (runner-level),
      `WRONG_VERDICT` etc. (fixture-only)
  - defer `NO_TOOL_USE` + `TOOL_CALL_HALLUCINATION` until real tool calling exists

**Tracing**

- `workbench/tracing.py`
  - `write_trace(session_id, run_id, payload)` → `traces/<session_id>/<run_id>.json`
  - trace includes:
    - task_id, prompt, mode, prompt_version, model_id
    - scenario_json + repair_json
    - validate/eval results (as “internal tools”)
    - metrics + taxonomy
    - timing/counters
    - git sha (if available)

**Reporting**

- `workbench/reporting.py`
  - appends RunRecord to: `reports/sessions/<session_id>/results.ndjson`
  - generates: `reports/sessions/<session_id>/summary.md` (overwrite)
  - optional export: `results.csv` (overwrite, derived from NDJSON)

**Stub**

- `workbench/models/stub.py`
  - deterministic canned `scenario_json`
  - optional single repair for one known infeasible task

**CLI**

- `python -m workbench run-task tasks/v1/<task>.json --model stub --session-id dev_...`
- `python -m workbench run-suite tasks/v1 --model stub --session-id dev_...`

### Definition of done

- Running suite produces:
  - `reports/sessions/<session_id>/results.ndjson`
  - `reports/sessions/<session_id>/summary.md`
  - `traces/<session_id>/...`
- Taxonomy triggers correctly on intentionally broken stub outputs

---

# Milestone 2 — Claude integration (two-turn loop) ✅ COMPLETE

**Goal:** Replace stub with Claude in the smallest reliable loop (draft + optional repair).

### Deliverables ✅

**Claude adapter**

- ✅ `workbench/models/agents.py` - ClaudeAgent implementation
  - Anthropic Messages API integration with environment-based authentication
  - JSON-only response format with comment filtering
  - Cost-effective model selection (claude-haiku-4-5-20251001)

**Prompting**

- ✅ `prompts/v1/draft_system.txt` - Schema documentation with sign conventions
- ✅ `prompts/v1/repair_system.txt` - Constrained repair instructions
  - Three repair mechanisms: baseline_reduction, event_amount_adjustment, event_timing_shift
  - Wrapped JSON response format with repair validation

**Agent implementation**

- ✅ `workbench/models/agents.py`
  - `draft(prompt, mode) -> scenario_json`
  - `repair(scenario_json, eval_result) -> repair_json`
  - Repair claim validation with mathematical constraints
  - Maximum 1 repair attempt per task

**Enhanced error taxonomy**

- ✅ `INVALID_JSON`, `SCHEMA_MISMATCH`, `REPAIR_FAILED`
- ✅ `INACCURATE_REPAIR_LABEL` - Repair validation failures
- ✅ `WRONG_VERDICT`, `WRONG_FIRST_VIOLATION_MONTH` - Fixture comparison

**CLI integration**

- ✅ `python -m workbench run-task tasks/v1/<task>.json --model claude`
- ✅ `python -m workbench run-suite tasks/v1 --model claude`

### Results ✅

**Performance achieved:**

- ✅ **92% task success rate** (12/13 tasks)
- ✅ **100% prediction accuracy** for verdict/violation detection
- ✅ **67% repair success rate** (2/3 repairs made scenarios feasible)

**Key findings:**

- ✅ Claude shows excellent JSON compliance after prompt refinement
- ✅ Strong financial reasoning for scenario evaluation
- ⚠️ Strategy bias toward baseline_reduction (100% of repair attempts)
- ⚠️ Constraint adherence challenges (attempts multiple simultaneous changes)

**Infrastructure robust:**

- ✅ Month serialization resolved through proper Pydantic integration
- ✅ Repair validation successfully catches logical errors
- ✅ Comprehensive trace capture with repair strategy breakdown

---

# Milestone 2.5 — Ledger Generation & Mathematical Verification

**Goal:** Test Claude's computational accuracy vs pattern matching intuition

### Deliverables

**Ledger generation capability**

- Add `generate_ledger: true` option to task format
- Claude returns both scenario JSON AND monthly projection table using existing `MonthlyRecord` format
- Prompts updated to include ledger schema documentation
- Runner enhanced to capture and validate ledger outputs

**Mathematical verification scoring**

- Compare Claude's month-by-month calculations vs simulator ground truth
- Track computational accuracy metrics (correct math, off-by-one errors, cumulative drift)
- Measure impact on repair quality when Claude "shows work"
- Error taxonomy extension for mathematical failures

**Experimental validation**

- Test subset of strategic scenarios with ledger generation enabled
- Analysis of mathematical reasoning patterns vs pure scenario generation
- Assessment of whether ledger requirement improves repair accuracy

### Definition of done

- Claude can generate valid monthly ledgers matching `MonthlyRecord` schema
- Scoring compares computational accuracy vs simulator
- Evidence whether ledger generation improves or hurts repair quality

---

# Milestone 3 — Comprehensive Task Suite & Scoring Polish

**Goal:** Complete systematic evaluation framework with robust baseline

### Deliverables

**Expanded task coverage**

- Add `expected` fields to ~5 representative tasks for regression testing
- Create 3-5 additional tasks targeting specific failure modes discovered in M2
- Strategic scenarios designed to test repair strategy diversity beyond baseline_reduction

**Formal scoring infrastructure**

- Enhanced metrics: repair success rates, strategy distribution breakdowns, accuracy percentiles
- Computational accuracy scoring for ledger-enabled tasks
- Time-based metrics (task completion velocity, repair convergence)

**Reporting improvements**

- Session summaries with pass rates, repair effectiveness, top taxonomy failures
- Representative trace selection (best/worst/interesting cases)
- Strategy bias analysis and constraint adherence patterns
- Baseline establishment for regression comparisons

**Quality polish**

- Error taxonomy refinement based on M2 findings
- Trace capture optimization for debugging complex scenarios
- Session management improvements for large-scale testing

### Definition of done

- 15+ tasks with comprehensive coverage of scenario types
- Reliable baseline metrics for regression testing
- Professional-quality reporting suitable for model/prompt comparison
- Clear documentation of Claude's current capabilities and limitations

---

# Milestone 4 — MCP Integration & Tool Use Migration

**Goal:** Evolve from one-shot JSON to orchestrated agent runtime with proper tool use

### Deliverables

- **Calculator tool integration**: Claude can request arithmetic verification for mathematical calculations
- **Schema validation tool**: Real-time JSON schema checking during generation
- **Constraint checker**: Live feasibility validation with specific violation details
- **Multi-turn workflow**: Replace one-shot generation with step-by-step reasoning and verification
- **Tool calling architecture**: Proper MCP integration following Anthropic patterns
- **Performance analysis**: Systematic comparison of tool-augmented vs one-shot approach
- **Mathematical precision improvement**: Target dramatic improvement in 0/15 ledger accuracy scores

### Success Criteria

- Mathematical precision scores improve from ~0% to >80% on complex tasks
- Tool calling workflow maintains or improves overall task completion rates
- Clear evidence of reasoning quality improvement vs response time tradeoffs
- Robust tool call error handling and fallback strategies
- Performance comparison vs current one-shot approach
- Clear understanding of tool use benefits vs complexity tradeoffs

---

# Optional Extensions

## Regression Testing Infrastructure

**Goal:** Enable systematic comparison of models, prompts, and architectural changes

### Potential Deliverables

**Session comparison tooling**

- `python -m workbench regress --task_set tasks/v1 --model claude --compare session_id_1 session_id_2`
- Delta analysis: tasks that changed behavior, performance regressions/improvements
- Statistical significance testing for performance changes
- Baseline establishment using current claude performance

**Regression detection**

- Automated identification of capability regressions
- Performance threshold alerting (success rate, accuracy, repair effectiveness)
- Trace diff tooling for debugging behavioral changes
- Historical trend analysis across multiple regression runs

**Comparison reporting**

- Side-by-side performance breakdowns
- Task-level delta analysis with specific failure mode changes
- Representative trace comparisons (same task, different outcomes)
- Summary dashboards for model/prompt evaluation decisions

### Definition of done

- Can reliably compare any two evaluation sessions
- Clear identification of regressions vs improvements
- Tooling supports prompt engineering and model selection decisions
- Baseline metrics established for future architectural changes

---

## Advanced Tool Integration

**Goal:** Extended tool capabilities and specialized reasoning chains

### Potential Deliverables

**MCP server implementation**

- `validate_scenario(scenario_json) -> {ok, errors[]}`
- `run_eval(scenario_json) -> {verdict, violations, ledger_summary}`
- Tool-based validation workflow replacing direct API calls
- Proper tool use error handling and retry logic

**Agent runtime orchestration**

- Multi-turn conversation flow: draft → validate → eval → repair → validate → eval
- Tool call budget management and optimization
- Conversation state management across repair iterations
- Enhanced error handling for tool use failures vs JSON failures

**Capability comparison**

- A/B testing: tool use vs one-shot JSON performance
- Analysis of tool call patterns and optimization opportunities
- Constraint adherence improvements with iterative validation
- Repair quality assessment with tool-assisted workflow

**Infrastructure updates**

- Trace capture for tool use conversations
- Updated error taxonomy for tool use specific failures
- Session management for longer conversation workflows
- Cost tracking and optimization for tool-heavy workflows

### Definition of done

- Working MCP server with financial evaluation tools
- Agent successfully uses tools for complete evaluation workflow
- Performance comparison vs current one-shot approach
- Clear understanding of tool use benefits vs complexity tradeoffs

---

## Metamorphic Testing Framework

**Goal:** Test scenario equivalence and linguistic robustness

### Potential Deliverables

- `tasks/v1/` expanded to ~10 tasks (same categories you listed)
- ~5 tasks include `expected`
- scoring polish:
  - `schema_errors_count`
  - `retries_used`
  - `internal_tool_calls` vs `model_tool_calls`
- summary improvements:
  - pass rate
  - repair success rate
  - top taxonomy
  - 2 representative trace paths

### Definition of done

- `run-suite` over 10 tasks runs reliably
- results stable across repeated runs (variance logged)
