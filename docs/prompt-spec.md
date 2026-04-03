# Globalदोस्त Prompt Specification

## 1. Prompting principles
- Evidence-first: use only entities present in `evidence_bundle`.
- Ordered reasoning: respect task dependency ordering.
- Human tone: practical, calm, and specific.
- Safety: avoid legal/financial certainty language.

## 2. Judge agent prompt contract

### System intent
"Generate a first-30-days plan grounded in graph evidence."

### Required rules
1. Reference only known entities from the bundle.
2. Keep actions dependency-aware and time-sequenced.
3. Explain *why* each step is included.
4. Return strict JSON for parser reliability.

### Expected JSON fields
- `plan_title`
- `best_next_action`
- `steps[]` (`day_range`, `action`, `entities`, `dependency_reason`, `source_node_ids`)
- `priority_contacts[]`
- `warnings[]`
- `confidence`

## 3. Cultural Bridge prompt contract

### System intent
"Explain a US term in plain language with home-context analogy."

### Required rules
1. Keep explanation concise and practical.
2. Include one home-context analogy.
3. Provide common mistakes and immediate next actions.
4. Return strict JSON.

### Expected JSON fields
- `plain_explanation`
- `home_context_analogy`
- `common_mistakes[]`
- `what_to_do_next[]`

## 4. Guardrails
- No invented entity names.
- No guarantees for legal outcomes.
- Keep uncertainty explicit when evidence is sparse.
- Include warnings when confidence is low.

## 5. Backend post-processing expectations
- Citation validation runs after generation.
- Non-conforming output can trigger fallback behavior.
- `llm_provider` and `fallback_used` are surfaced to UI for transparency.
