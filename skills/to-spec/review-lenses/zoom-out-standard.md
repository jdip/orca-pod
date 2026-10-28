> Adapted from [`resources/document_standards/zoom-out-standard.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/resources/document_standards/zoom-out-standard.md) in `google/elephant-goldfish-model` at `05f8984cb6e0077b072ba034f66d95ffdde200ee`, licensed under the
> Apache License 2.0 ([LICENSE](LICENSE)).
> Modified by Orca Pod: added this provenance header; the standard text is unchanged.

# Zoom Out Standard

This standard defines the quality bar for evaluating high-level designs,
architectures, and implementation plans from a high-altitude perspective.

## Core Principle

A design passes if it solves the root problem in the simplest possible way,
leverages existing infrastructure and codebase conventions, avoids premature
optimization or speculative features (YAGNI), and maintains appropriate
abstraction boundaries without getting bogged down in low-level code
implementation details.

## 0. Context Sufficiency (Prerequisite Check)

*   **Understanding the Objective**: The document must contain enough
    information to define the overall objective. If the reviewer cannot
    determine *what* we are trying to achieve and *why*, the review must fail
    immediately with a request for context.

## 1. Root Problem Focus

*   **Symptom vs. Root Cause**: The design must solve the underlying problem,
    not just apply a local band-aid to symptoms.
*   **Project Alignment**: The design must align with the high-level goals and
    architectural philosophy defined in the project's root documentation
    (`README.md` or `context.md`).

## 2. Simplicity & Extensibility

*   **YAGNI (You Aren't Gonna Need It)**: Reject abstractions, code paths, or
    features built solely for speculative future requirements.
*   **Premature Optimization**: Avoid introducing complexity (caching, sharding,
    async queues) before performance bottlenecks are proven.
*   **Minimalist Data Flow**: Ensure data passes through the minimal number of
    components.
*   **No Architectural Dead-Ends**: Use clean interfaces and boundaries to allow
    future expansion without blocking it, without implementing speculative
    features now.

## 3. Anti-Weeds (Altitude Control)

*   **Premature Detail**: High-level sections must focus on architecture,
    interfaces, and data flows, not code-level implementation details (e.g.,
    helper functions or loop variables).
*   **Workarounds vs. Structural Fixes**: Avoid complex local workarounds;
    propose changes to the root component if that is cleaner.
*   **Right Placement (Architectural Fit)**: Ensure new logic is placed in the
    correct layer/component according to separation of concerns.

## 4. Leverage Existing

*   **Codebase Reuse**: Search the codebase and reuse existing utilities,
    classes, or modules instead of reinventing them. Ensure the candidate for
    reuse is stable, maintained, and does not violate dependency boundaries.
*   **Pattern Consistency**: Follow established design patterns in the codebase.
*   **Platform Standards**: Use established ecosystem frameworks and standard libraries
    instead of bespoke or ad-hoc custom solutions.
*   **Identify Anti-Patterns**: Actively flag known anti-patterns
    (e.g., bypassing standard authentication, hardcoding deployment configurations).
