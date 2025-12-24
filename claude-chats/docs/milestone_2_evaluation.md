# Milestone 2 Evaluation: Claude Integration (Design & Partial Implementation)

## Overview
Milestone 2 focuses on integrating Claude as an agent that can read prompts, generate scenarios, and perform constrained repairs. This evaluation covers the design decisions made during our planning session.

## Key Design Decisions

### 1. Repair Response Format
**Decision**: Wrapped JSON response with repair declaration
```json
{
  "repaired_scenario": { /* scenario */ },
  "repair_applied": {
    "type": "baseline_reduction",
    "changes": "Reduced outflows from -4000 to -2000"
  }
}
```

**Rationale**: 
- Keeps existing interface (returns string)
- Forces Claude to declare intent
- Enables validation of repair accuracy

**Alternative considered**: Tool-based validation
- Rejected due to tool call limits and complexity

### 2. Repair Type Validation
**Decision**: Add INACCURATE_REPAIR_LABEL error when repairs don't match claims

**Quality**: Excellent catch - prevents Claude from "cheating" by doing multiple repairs or wrong repair type

**Implementation approach**: JSON diff to validate only claimed fields changed

### 3. One-Shot JSON Generation
**Decision**: Claude must produce valid JSON without tools

**Rationale**:
- Mirrors real-world usage patterns
- Avoids tool call burn
- Simpler implementation
- Tests core capability

**Alternative considered**: Give Claude a validate_json tool
- Would test different capability (tool use vs generation)

### 4. Error Message Formatting
**Decision**: Template-based formatting of eval results for repair prompt

**Example**: "Your simulation failed in {month} because you violated the {invariant} invariant..."

**Trade-off**: Less flexible than Claude summarizing, but more deterministic

### 5. No Repair Reasonableness Limits
**Decision**: Let traces reveal if repairs are too aggressive

**Rationale**: 
- Avoid premature optimization
- Learn from data
- Simpler initial implementation

**Alternative**: Could add percentage limits on reductions

## Product Thinking Assessment

### Strengths
1. **Pragmatic choices**: Avoided over-engineering with tool loops
2. **Data-driven iteration**: Use traces to inform future constraints
3. **Backward compatibility**: Kept existing interfaces
4. **Clear validation**: Repair claims must match reality

### Good PM Instincts
- "Validate and discard" - avoided feature creep
- One-shot JSON matches user expectations
- Error taxonomy extension was minimal and targeted
- Understood tool call economics

### Areas for Growth
- Could have considered A/B testing different prompt strategies
- Didn't discuss timeout handling for Claude API calls
- No mention of rate limiting or retry strategies

## Technical Design Quality

### Well-Reasoned Aspects
1. Repair type enum values match allowed operations clearly
2. Validation happens after JSON parsing but before eval
3. Error precedence maintains existing logic
4. Wrapper format is extensible

### Questions/Gaps
1. How to handle Claude refusals?
2. What if Claude adds commentary outside JSON?
3. Should repair prompt vary by failure type?

## Learning Demonstrated

### Conceptual Understanding
- Recognized that different test approaches (tools vs direct) test different capabilities
- Understood that repair validation prevents gaming the system
- Saw connection between trace data and future improvements

### System Thinking
- Considered tool call economics
- Thought about real-world usage patterns
- Recognized need for deterministic prompts

### Growth from M0/M1
- More confident in design decisions
- Better at identifying edge cases upfront
- Thinking about Claude's perspective as a user

## Implementation Readiness

### Clear Next Steps
1. Add INACCURATE_REPAIR_LABEL to error taxonomy ✓
2. Update spec/docs with repair format ✓
3. Create repair validator
4. Update runner for wrapped response
5. Build Claude agent

### Potential Challenges
- Prompt engineering for consistent JSON
- Handling Claude edge cases
- Balancing prompt clarity vs token usage

## Implementation Progress (Session 2)

### Completed:
1. **Error Taxonomy**: Added INACCURATE_REPAIR_LABEL successfully
2. **Spec Updates**: Updated both CLAUDE.md and spec.md with repair format
3. **Runner Modifications**: 
   - Correctly parsing wrapped repair response
   - Extracting repair type and scenario
   - Added validation check before proceeding
4. **Repair Validator**: 
   - Implemented validate_repair_claim for all three repair types
   - Handles edge cases (missing fields, order)
   - Validates sign preservation for event amounts

### Implementation Quality:
- **Good debugging**: Fixed variable naming conflicts, JSON parsing issues
- **Iterative improvement**: Multiple passes to get validation logic right
- **Edge case thinking**: Added checks for event count, sign changes

### Minor Issues Found:
- Initial logic errors in baseline_reduction (checking for equality instead of inequality)
- Sign check logic was backwards (needed to check for sign CHANGE not preservation)
- Some missing top-level field validations

### Time Management:
Recognized fatigue and chose to wrap up at a logical stopping point. Good self-awareness and project management.

## Overall Grade: A

Excellent design session and solid implementation progress. The repair validation infrastructure is complete and well-tested. Ready for Claude agent implementation with all the hard architectural decisions made. Key growth: systematic debugging and iterative refinement of complex validation logic.