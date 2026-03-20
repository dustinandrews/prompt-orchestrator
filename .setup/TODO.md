# FullAutoTemplate TODO

## Open Questions

### 1. Answer Questions Between Tasks?
Current behavior: Models can ask clarifying questions mid-workflow.
- **Option A**: Allow questions (current) - may interrupt flow but catches issues early
- **Option B**: Force proceed mode (K.I.S.S.) - faster but risks misinterpretation
- **Decision needed**: Which approach for v1?

## Implementation Tasks

### 2. Retry Failed Steps
Add automatic retry with exponential backoff and context hints:
```yaml
retry_policy:
  max_attempts: 3
  backoff: exponential  # 1s, 2s, 4s
  hint_template: "Previous attempt failed with: {error}. Try alternative approach."
```

**Considerations**:
- Distinguish transient errors (API timeout) vs permanent failures (syntax error)
- Add retry counter to output for visibility
- Circuit breaker: abort after N consecutive failures across all steps

## Completed
- [x] Fix `/compact` commands to use coder-model (was defaulting to qwen)
- [x] Optional `--step N` argument to manually start at specific step with extra context

## Won't Do
- ~~Resume from Ctrl-C / crash~~ - Complexity not justified for current use case. Use `--step N` to manually resume.
