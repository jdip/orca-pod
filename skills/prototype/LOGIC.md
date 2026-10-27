# Logic prototype

Use this branch when the question concerns behavior, state transitions, data
shape, or an API surface that needs to be exercised before implementation.

## Shape the evidence

Write the question, candidate rule, and observations that would support or
reject it where a reviewer can see them. Choose a few representative scenarios:
the ordinary path, the consequential edge or boundary, and a rejected or
invalid action when that distinction matters.

Choose an artifact that people who need to judge the result can use in the
approved environment. For example, a directly opened HTML demo can work for a
clickable state exploration when it requires no new runtime; an existing
component, executable module, or established task runner can better expose a
candidate that must fit the repository. The question, not a preferred artifact
format, makes that choice.

## Build the smallest useful model

Express the candidate logic in the form that makes its decision boundaries
clear: a reducer, state machine, pure functions over data, or a module with a
small stateful surface. Keep presentation separate from the candidate logic
when that makes the rule easier to inspect or reuse as implementation evidence.

Give a human-readable interaction only when it helps someone exercise the
scenarios. It may use direct controls, a guided sequence, a compact script, or
another established interface. Use domain language. After each relevant action,
show the full relevant state and the transition, acceptance, or rejection that
answers the question; do not hide the evidence behind implementation names or a
raw dump when a readable presentation is practical.

## Verify and decide

Run each chosen scenario from a known state and inspect the observed result.
Record the verdict, the observations that support it, and the implementation
seam. Retain the artifact only as an authorized planning record. When the
decision is implemented, rebuild the selected logic under the repository's
normal production constraints rather than carrying the prototype shell forward.

## Boundaries

Keep integrations in memory or against an isolated disposable resource unless
the inquiry specifically concerns persistence. Use existing language, runtime,
and task-runner choices. The prototype concentrates on one decision; its
scenarios should expose that decision rather than speculate about future scope.
