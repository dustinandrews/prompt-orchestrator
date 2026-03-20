# Why FullAutoTemplate (working name) Exists

> "Autonomy without guardrails = bankruptcy"

## The Problem

Current AI coding agents promise autonomy but deliver cost overruns. A "vibe coding" session with Claude Code can burn $20 in an afternoon. Leave an agent running unattended and you might wake up to a $200 bill—or a broken codebase that cost $200 to break.

The issue isn't the models. It's the lack of guardrails. Autonomy without structure is expensive gambling.

## The Observation

Big models are optimized for engagement. They have a lot of chat lube. They keep you talking. But software engineering isn't a conversation; it's a structured process with review gates:

1. Understand the problem
2. Design the solution  
3. Break it into tasks
4. Implement
5. Verify

Each gate catches errors before they compound. Skip the gates and small hallucinations or developer mistakes become architectural disasters.

## The Strategy

**Use weaker models within a strong process.**

Qwen 3.5 (35B) hallucinates when asked to "build an app." But give it a template, constrain its scope to one phase, and verify its output before proceeding—it produces solid, usable code.

The workflow:
```
specify → review → plan → review → tasks → analyze → review → implement → test-review → product-review
```

Each arrow is a checkpoint. Code doesn't flow forward until it's verified. Either by a human, an agent, or best of all, a deterministic program.

## Three Pillars

**Reliable**
- Verify gates catch placeholders before they become bugs
- Checkpoint/resume prevents losing progress to crashes or rate limits
- Allows rolling a project back to the point before it lost it's mind
- Structured workflow contains failure modes, halts or rolls back execution.
- Runs unattended with less danger of infinite tool loops

**Cost Effective**  
- Model routing: local Qwen for bulk work ($0), Kimi only for specification and final review ($0.60)
- Full cycle costs $0.60 vs $2.50+ for baseline small modules
- Circuit breakers prevent runaway spending

**Efficient**
- Queue 10 specs, wake up to 10 codebases
- Human reviews output, doesn't babysit real-time generation
- Parallelization beats single-threaded "vibe coding"
- Ready for a QA agent to begin integration testing, which will also be constrained.

## The Stack

**Python** — Not because it's better than Rust or Go, but because LLMs understand it. The patterns are recognizable. Small libraries compose into larger applications.

**Local Inference** — Local VRAM isn't for "free" compute. It's for compute you control completely. No API latency. No rate limits. No network dependency. Renting low end GPUs is also a possibility.

**Templates** — Pre-defined skeletons prevent whole categories of errors. Agents don't invent directory structures or forget to use virtual environments when the scaffold is already there.

## The Pipeline Vision

1. **Queue** — Write specs, enqueue jobs
2. **Generate** — FullAutoTemplate produces code modules
3. **QA** — Integration testing wires modules together
4. **Deploy** — CI/CD validates and ships

Human attention at review gates. Everything else automated.

## Skepticism of Alternatives

Tools like Goose and Claude Code can build toy projects autonomously. But real applications need:
- Error handling for edge cases
- Tests that actually run
- Documentation that exists
- Dependencies that resolve

Until someone demonstrates real applications built end-to-end with local Ollama models, the gap between "running locally" and "working locally" remains.

FullAutoTemplate bridges that gap with process discipline.

## The Goal

A software system that is:
- **Reliable** — Errors caught early, progress never lost
- **Cost Effective** — Leverage local models where possible, premium models only where necessary  
- **Efficient** — More things in flight without breaking your brain

The bootstrap isn't the point. The bootstrap builds the system that builds the future systems—each layer battle-tested before the next layer trusts it.


FullAutoTemplate is the guardrails.
