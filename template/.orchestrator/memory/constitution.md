# Constitution

## Core Principles

### I. Lean Development

Every feature, system, and abstraction MUST justify its existence:
- **No bloat**: zero unused code, zero unused assets, zero unused
  dependencies. Every file in the repo serves a current purpose.
- **No overengineering**: solve today's problem, not next month's. The
  simplest correct solution is the best solution. Do not add generic
  interfaces, factory patterns, or dependency injection unless a second
  concrete variant exists.
- **No scope creep**: features are aggressively scoped to the minimal size
  that delivers value. If a feature can be cut and the prototype still
  validates the core mechanic, cut it.
- **YAGNI (You Ain't Gonna Need It)**: if a feature, refactor, or abstraction
  is not required by the current iteration, do not build it.
- **Prefer deletion over addition**: when faced with a design problem, first
  ask "what can I remove?" before "what can I add?"

**Rationale**: A prototype's only goal is to validate an idea as quickly as
possible. Every line of code that doesn't serve validation is dead weight.

### II. Documented Technology Stack

Every project MUST have an explicitly documented technology stack:
- **NO assumptions**: Do NOT assume Python, TypeScript, Java, Go, or any specific language/framework
- **HALT if undocumented**: If technology stack is not documented, STOP and ask the user to specify
- Document in `constitution.md`, `AGENTS.md`, `README.md`, or similar project-level documentation
- Include: Language(s), build system, key dependencies, deployment target
- **Project over personal preferences**: Use what the project uses, not what you prefer

**CRITICAL**: When in doubt, ASK THE USER. Never guess the tech stack.

### III. Never Commit Secrets to Git

Secrets detection mandatory - scan before commit; .env files in .gitignore by default; Use environment variables or secure vaults; Rotate compromised credentials immediately.

**Rationale**: Version control is forever - exposed secrets create permanent attack vectors. Proactive scanning prevents costly incident response and maintains trust boundaries.

### IV. MVP-Focus ship quick, fail fast, pivot early

Prove value before expanding; Ship working code in hours, not days; Explicit failure criteria defined upfront; Cut scope aggressively when `future proofing` creeps in.

Rationale: Real usage validates assumptions faster than planning. Minimal scope prevents over-engineering and delivers tangible progress quickly. Failed experiments teach more than successful speculation. Slow is smooth and smooth is fast.

### V. Battle-Tested Over Build-From-Scratch

Prefer proven libraries with >1 year production history and active maintenance; MIT/Apache/BSD licenses only (no GPL/viral); Evaluate integration cost vs build cost honestly; Skip if library solves <70% of your requirements or needs heavy customization.

**Rationale**: Mature libraries carry proven reliability and edge-case handling you haven't discovered yet. Time spent on domain-specific features beats rebuilding solved problems. Selective adoption prevents dependency bloat while accelerating delivery. Docker pull takes minutes if the container is right (or a couple more minutes to try and discard).

### VI. K.I.S.S principle

Never over-engineer. Unless otherwise specified consider all programs to be internal tools for engineering use. Keep it clean, strip off anything you don't need.

**Rationale**: More stuff is more chances to get confused or break things. Less is more.

### VII. One thing at a time

Only plan and implement one feature at a time. If a user spec has more than one work item, pick the most core item not yet done. Finish that, come back for the rest later. Be ruthless about cutting and punting.

**Rationale**: User's don't know what they want until they get something they can use. Give them the core and iterate. It's the proven M.V.P. strategy.

## Development Workflow

**Code Quality Gates**
- Automated test suite must pass with minimum 80% code coverage
- Documentation updates required for all user-facing changes

**Testing Discipline**
- Unit tests for all business logic
- Integration tests for all library contracts
- Contract tests for inter-service communication
- NO Performance benchmarks. Test and tune if problems turn up later.
- Live integration with working API keys provided in .env file when possible.

**Error Handling Philosophy**
- Fail fast: Crash immediately on unexpected conditions, don't limp along
- Be loud: Errors go to stderr with clear, actionable messages
- Show the gory details: Full stack traces by default, no hiding failures
- No silent failures: If something breaks, make sure everyone knows
- Debuggable first: Optimize for understanding problems, not hiding them

**Rationale**: Hidden failures waste more time than visible crashes. Full context enables faster debugging. Better to know something broke than wonder why results are wrong.

## Governance

**Constitution Supremacy**
This constitution supersedes all other development practices and guidelines. All team members must understand and adhere to these principles.
Documented exceptions are allowed with team leader consent. Always get signoff for deviations.
