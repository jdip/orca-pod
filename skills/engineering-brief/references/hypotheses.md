# Working hypotheses

These are falsifiable questions, not architectural requirements. Look especially
for contradictory results and boundary conditions. Separate evidence that a
practice exists in this repo from evidence that it improves outcomes.

1. **Verification is becoming a larger bottleneck than generation.**
2. **Independent reviewer context is usually more valuable than same-agent
   self-review.**
3. **Repository knowledge and good context engineering can sometimes matter more
   than upgrading to a stronger model.**
4. **Long-running agents work best once uncertainty has been reduced and success
   criteria are explicit.**
5. **Agent parallelism eventually creates a human integration/merge-bandwidth
   bottleneck.**
6. **Coordinator and worker roles will increasingly separate.**
7. **Reusable agent skills will need software-engineering discipline: tests,
   evals, versioning, observability, and security.**
8. **Model selection will increasingly become a harness/runtime decision rather
   than a human choosing one model for an entire task.**
9. **Deterministic systems should continue handling work they are good at; agents
   should not replace build/test/lint/deploy infrastructure merely because they
   can invoke it.**

In the first brief’s supporting notes, summarize observed Orca Pod orchestration, skills, context,
planning, parallelism, verification, and review. Compare the repo against all nine
hypotheses using **ahead**, **roughly aligned**, **potential gap**, or **unknown**
where justified, with source paths/revision and measurement caveats. These labels
describe the fit to a hypothesis, not a universal ranking against other projects.
In later reports update affected conclusions; preserve unresolved questions in
the watchlist rather than treating the initial baseline as permanent truth.
