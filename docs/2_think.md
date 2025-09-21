# Task

Build a system that automatically creates and maintains tests so developers can stay focused on product work.

# Problems we address

- High-quality tests are increasingly valuable as AI can produce implementation code on demand.
  - Code can be regenerated quickly for only the token cost.
  - Shifting stacks, libraries, or vendors is easier when tests capture the expected behavior.
  - Test quality shows in how quickly an implementation can be derived from the tests.
- Requirements change constantly, and tests translate them into a structured, measurable language.
  - Test-driven development helps teams converge on a shared understanding of the specification.
- New features can break critical existing functionality.
  - An automated test suite provides confidence that shipped code hits the quality bar.
- Refactoring for maintainability carries the risk of regressions.
  - Refactoring without supporting tests is slow and risky.

## Out of scope
- Busywork handed down by managers or leads that developers must complete for promotion.
  - Writing tests can sometimes be used to satisfy that pressure, though the real value may be questionable and the time cost significant.

# Next steps

- [x] Research the web on the solutions that already exists to do that
  - [x] Conventional solutions
  - [x] AI based solutions and vendors
  - [x] Scientific articles
- [x] Build a very small solution which actually solves the problem quickly
  - [x] Probably opencode/claude code + prompt
  - [x] 1-2 hrs
- [x] Find a way how to measure the quality of the solution
  - [x] Research the benchmarks that already exists for AI test coverage
  - [x] Choose the one that suits or come up with a way to build one and create a very small prototype not scaling it yet, but with a clear path to scale
- [ ] Make 2-3 iterations to improve the existing solution
- [ ] Wrap up
  - [ ] Who could potentially buy the company
  - [ ] How the ideal value demo could look like
  - [ ] Some vague steps to get to that goal
  - [ ] Who are the first persons to hire
  - [ ] How to survive while we are getting their
