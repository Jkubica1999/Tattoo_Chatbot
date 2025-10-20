# TattooBot Build Plan

## Phase 0 — Ground Rules

**Purpose:** Define fixed principles and environment defaults before writing code.

### Rules
- Estimator = **only** source of truth for prices.
- Bot asks **one** targeted follow-up per missing slot.
- Certain cases (**neck / face / hands / under-18 / medical / offensive / “exact quote/time”**) → polite escalation to human.
- Use **one cheap default LLM model**, with:
  - One schema-repair retry.
  - Safe template fallback if both calls fail.
- Logs must identify tenant_id, user_id, correlation_id per request.

### Env defaults
LLM_MODEL=cheap-default
LLM_MAX_OUTPUT_TOKENS=120
LLM_TEMPERATURE=0.3
USE_LLM_NLU=true
USE_LLM_REPLY=true


### Acceptance
- App starts cleanly with these env vars set.
- Estimator runs using tenant config.
- LLM flags are readable at runtime.
