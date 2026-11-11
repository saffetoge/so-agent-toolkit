---
name: architecture-guardian
description: Prevent architectural drift, duplicated business logic, inconsistent rules, and unnecessary complexity. Use when implementing, modifying, reviewing, or refactoring application code. Also covers feature-first, modular, removable and portable design (Universal Modularity & Portability Rules). Mimari sapma, kopya iş kuralı, tek kaynak (SSOT), modülerlik ve taşınabilirlik denetimi; kod yazarken, değiştirirken, gözden geçirirken ve refactor ederken kullan.
---

# Architecture Guardian

## Mission
Keep every project consistent, modular, maintainable,
secure, and scalable without unnecessary complexity.

Apply these principles regardless of language,
framework, architecture, or project size.

## 1. Single Source of Truth
- Every business rule must have one authoritative owner.
- Never duplicate calculations, validations, permissions,
  state transitions, or domain-specific logic.
- Reuse or extend existing implementations before
  introducing new ones.
- Centralize shared behavior, not unrelated code
  that merely looks similar.
- Avoid God Classes and unnecessary global state.

## 2. Architecture First
Before implementing a change:
- Inspect relevant existing code and conventions.
- Locate similar features and reusable components.
- Identify the correct module and architectural layer.
- Understand dependencies and data flow.
- Prefer existing patterns over introducing new ones.

Do not create a new Service, Helper, Repository,
Utility, or abstraction without a clear responsibility.

## 3. Separation of Concerns
- Keep business logic out of presentation layers.
- Separate domain rules, persistence, infrastructure,
  validation, and orchestration.
- Maintain clear module ownership.
- Avoid circular dependencies.
- Keep APIs and interfaces consistent.

## 4. Reusability and Consistency
- Follow established naming and folder conventions.
- Reuse existing types, DTOs, validators, components,
  error handlers, and shared services.
- Do not create multiple implementations of the
  same business rule.
- Prefer composition over unnecessary inheritance.
- Avoid premature abstraction.

## 5. Data Integrity and Security
When applicable:
- Enforce authorization at trusted boundaries.
- Preserve tenant and user data isolation.
- Use atomic transactions for critical operations.
- Prevent duplicate execution with idempotency.
- Validate input and enforce data invariants.
- Preserve auditability of critical changes.
- Never expose secrets or sensitive information.

## 6. Business Rules and Calculations
- Centralize financial and domain calculations.
- Define rounding, precision, and tolerance policies.
- Keep configuration separate from algorithms.
- Make rules testable and deterministic.
- Preserve historical record consistency.
- Handle concurrency and edge cases explicitly.

## 7. Change Safety
- Prefer small, focused, reversible changes.
- Preserve existing behavior unless change is requested.
- Check callers and downstream dependencies.
- Avoid unrelated refactoring.
- Add or update relevant tests.
- Run available focused validation checks.
- Never claim unexecuted tests passed.

## 8. Performance
- Prevent avoidable N+1 queries and duplicate work.
- Reuse appropriate caching and data-access patterns.
- Avoid unnecessary database queries or API requests.
- Optimize based on evidence, not assumptions.
- Do not sacrifice correctness for micro-optimizations.

## 9. Anti-Overengineering
Apply KISS, DRY, SOLID, and YAGNI pragmatically.
- Do not introduce patterns without a real need.
- Do not build generic frameworks for simple tasks.
- Do not centralize unrelated responsibilities.
- Respect the existing project's architecture.
- Prefer clarity and consistency over cleverness.

## 10. Required Workflow
For each meaningful code change:

DISCOVER
Find the existing owner of the relevant behavior.

REUSE
Extend existing code where appropriate.

DESIGN
Choose the smallest coherent change.

IMPLEMENT
Follow project conventions and boundaries.

VERIFY
Check behavior, security, dependencies, and tests.

REPORT
Briefly state what changed, what was reused,
what was verified, and any remaining risks.

## Final Principle
One responsibility, one authoritative owner.

Never create a second source of truth when a suitable
one already exists.

Do not force centralization when independent
implementations represent different domain rules.

---

# Universal Modularity & Portability Rules

## 1. Feature-First Architecture
- Organize code by business feature or domain.
- Every feature should have a clear responsibility.
- Keep related logic, components, routes, validation,
  tests, and configuration together where practical.
- Avoid scattering one feature across unrelated folders.

## 2. Independent Modules
- Design features as cohesive, loosely coupled modules.
- Modules should communicate through explicit contracts.
- Avoid direct access to another module's internals.
- Keep dependencies minimal and directional.
- Prevent circular dependencies.

## 3. Removable & Portable Features
- Modules should be removable with minimal impact.
- Removing a feature must not break unrelated features.
- Avoid hardcoded references to optional modules.
- Keep module-specific assets and dependencies identifiable.
- Use explicit registration and integration points.
- Define dependencies and required configuration clearly.
- Handle module removal and data migrations safely.

## 4. Modular Pages & UI
- Build pages from reusable, composable components.
- Separate page layout, UI components, and business logic.
- Keep sections independently replaceable.
- Centralize shared design tokens and UI primitives.
- Avoid duplicated headers, footers, forms, and layouts.
- Avoid giant components containing unrelated logic.
- Prefer composition over deeply nested inheritance.

## 5. Centralized Shared Logic
- Maintain one authoritative implementation per rule.
- Centralize genuinely shared services and utilities.
- Do not duplicate calculations or business validations.
- Do not create a universal service for unrelated logic.
- Keep module-specific behavior inside its owner module.

## 6. Explicit Contracts
- Define clear public APIs between modules.
- Hide internal implementation details.
- Use interfaces, events, or adapters when justified.
- Minimize cross-module database access.
- Ensure contract changes are controlled and testable.

## 7. Minimal Change Impact
Before modifying code:
- Identify the owning feature or module.
- Find and reuse existing components.
- Evaluate effects on other modules.
- Change only necessary code.
- Preserve existing public contracts where possible.
- Verify dependent functionality.

## 8. Architecture Validation
For every new feature, evaluate:
- Is it independently understandable?
- Can it be tested independently?
- Can it be replaced without major rewrites?
- Can it be removed without breaking unrelated features?
- Can it be reused in another project with limited changes?
- Does it follow existing project conventions?

## Final Rule
Build cohesive, loosely coupled, reusable systems.

Prefer modular monoliths over premature microservices.

Every feature should have a clear owner, explicit
dependencies, and controlled integration points.

Never sacrifice simplicity for theoretical modularity.

---

## Projede (yönlendirme)

Projenin `AGENTS.md`'si varsa projeye özel merkez tablosunu ("konu → merkez") taşır; DISCOVER adımında önce o
tabloya bakılır. Raporlar kullanıcının dilinde yazılır.
