# Sub-agent Prompt Discipline

> When the main agent spawns a sub-agent (or designs an agent prompt), the prompt MUST follow this discipline. Sub-agents are expensive and amnesiac — every weakness in the prompt is amplified by the agent's lack of session context.

## Overview — Why this file exists

Sub-agents fail in predictable ways: they shortcut to heuristic defaults (LLM-as-judge picks the "safe" category), they silently rewrite (polish agents inflate verbs), they leak generator-side reasoning into review verdicts. These failures are not random — they come from prompt patterns the main agent reused without realizing the cost. This file codifies the patterns; agent prompts that ignore them produce unreliable output.

## Outline (story-flow check passes)

1. Anti-shortcut bans (why a judge agent quietly converges to a default category)
2. Handoff polish drift-check (why a polishing agent silently changes verbs)
3. Fresh-session review discipline (why a review agent must not see the generator's reasoning)
4. Context-packet pattern (why agents receive paths, not content)
5. Bake positive + negative examples (why generic prompts produce generic output)
6. Acceptance gate per agent type

A reader scanning these headings should be able to predict the rule under each — that is the outline self-check.

---

## 1. Anti-shortcut bans (LLM-as-judge family)

**Rule:** Any prompt that asks a sub-agent to classify, score, or pick a category MUST explicitly ban heuristic-script derivation and bake at least one positive + one negative worked example. Without these, the agent collapses to a single safe class (observed default rate: ~87% on the largest category).

**Why (Empirical):** When a judge agent has many categories and no examples, it defers to whichever class minimizes risk of being wrong. Diagnosis comes from comparing attribution distribution across parallel chunks — if one judge converges sharply while another spreads, the converging judge is shortcutting.

**Prompt patterns to include:**
- "Do NOT derive the verdict from heuristic rules — read the artifact end-to-end."
- "Do NOT default to category X when uncertain; mark `UNCERTAIN` and surface why."
- One worked example for each category, including at least one edge case.
- An explicit "if all categories seem to apply, list them and explain which is dominant" instruction.

**Anti-pattern:**
- "Pick the best category from this list" with no examples → 87% default-class.
- "Score from 1-5" with no anchored rubric → all 3s.

## 2. Handoff polish drift-check

**Rule:** Polish / render / translate agents MUST be given a verbatim-preserve list AND the calling main agent MUST run a token-by-token diff vs source after the agent returns. Polishing agents will silently inflate verbs ("Co-built" → "Built"), strip target-role keywords, normalize informal phrasing, even when the prompt says "no bluff."

**Why (Empirical):** Observed in CV/cover-letter polish runs and HTML render handoffs. The agent's training prior toward "professional polish" overrides the explicit instruction unless the instruction is enforced by a downstream diff.

**Prompt patterns:**
- "These exact phrases MUST appear verbatim in your output: [list]."
- "If you change any verb, list it in a `## Changes` block with reason."
- "Do not strip target-role keywords: [list]."

**Caller-side check (mandatory, not optional):**
```
diff_tokens(source_text, agent_output)
assert all(p in agent_output for p in must_preserve_list)
```

If diff surfaces an unauthorized change, re-prompt; do not ship the agent's first draft.

## 3. Fresh-session review discipline

**Rule:** Review agents MUST be spawned with ZERO context from the generator agent. The review agent reads only the OUTPUT ARTIFACT (file path or rendered content), never the generator's chain-of-thought, prompt history, or intermediate scratchpads.

**Why (Causal):** A review agent that sees the generator's reasoning anchors on the generator's logic and produces a confirmation bias. The point of the review is to catch errors the generator made — sharing the generator's framing defeats the purpose.

**Prompt patterns:**
- Open prompt with: "You have no prior context. Read [path]. Critique it as if you had never seen it before."
- Do NOT pass `generator_summary`, `generator_assumptions`, or `task_brief_from_generator` as context.
- DO pass: the artifact path, the canonical rubric, and the original user task statement.

**Anti-pattern:**
- "Here is what the generator agent thought; now review the output" → review agent rubber-stamps.
- Passing the generator's TodoList into the review agent's context.

## 4. Context-packet pattern (paths, not content)

**Rule:** When briefing a sub-agent on N files, send a context packet of FILE PATHS + 1-line purpose per file, NOT the file contents. Cap the packet at ~500 tokens. The sub-agent loads the files itself with Read.

**Why (Operational):** Pasting file contents into the spawn prompt bloats the orchestrator's context (the prompt is logged in the parent session) AND wastes the sub-agent's first turn re-reading something already in its context. Paths + purpose let the agent triage.

**Packet template:**
```
Project: <name>
Goal: <one sentence>
Files to read in order:
1. <path> — <1-line purpose>
2. <path> — <1-line purpose>
...
N. <path> — <1-line purpose>
Constraints: <max 3 bullets>
Output: <expected deliverable + format>
```

If the packet exceeds 500 tokens, drop file purpose lines first, then files (start from least essential). Never dump full file content.

## 5. Bake positive + negative examples

**Rule:** Generic prompts ("write a summary," "find issues," "rate quality") produce generic output. The fix is concrete: include 1 GOOD example and 1 BAD example with 1-line explanation of WHY each is good/bad.

**Why (Comparative):** Anchored examples calibrate the agent's distribution of acceptable outputs faster than any list of adjectives. "Good prose" is a vague target; "good prose like example A, bad prose like example B" is a measurable target.

**Pattern:**
```
GOOD example: <2-3 lines of artifact>
Why good: <1 line>

BAD example: <2-3 lines of artifact>
Why bad: <1 line>

Now produce your output matching the GOOD pattern.
```

Avoid laundry-list adjective prompts ("be clear, concise, professional, accurate, insightful"). Examples beat adjectives.

## 6. Acceptance gate per agent type

Before the calling main agent uses a sub-agent's output, it must run the gate matching the agent's role:

| Agent role | Acceptance gate |
|------------|-----------------|
| Judge / classifier | Attribution distribution check — no class >70% by default |
| Polish / render | Token diff vs source + verbatim-preserve list check |
| Review | Output cites the artifact (line numbers / quotes), not the generator's framing |
| Context tracer (read-heavy) | Output is a structured summary, not a raw paste of file contents |
| Method auditor | Output names the specific method gap + a remediation method, not a generic "improve rigor" |

A sub-agent output that fails its gate is discarded — re-prompt or fall back to the main agent doing the task inline.

---

## Cross-references

- Anti-shortcut origin: `feedback_subagent_judge_anti_shortcut.md` (auto-memory).
- Handoff drift origin: `feedback_handoff_polish_drift_check.md` (auto-memory).
- Why-Explanation meta-rule: every prompt section above ships with a `Why` per Rule 4 (`universal-workflow-rules.md`).
- Outline self-check: this file's headings 1-6 tell the story; reader scanning only headings can predict each rule's content.
