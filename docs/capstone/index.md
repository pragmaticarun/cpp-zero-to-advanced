# Capstones

Two projects pull the course together. Each comes with a complete reference implementation (a header-only
library), a test program, and a demo — all compiled and run by the same checker as every lesson example, on
GCC 14 and Clang, with sanitizers in CI.

| Capstone | Builds on | You'll practise |
|---|---|---|
| [A: Concurrent task library + CLI](threadpool.md) | Weeks 4–5, 9, 13–14 | RAII, futures, condition variables, back-pressure, shutdown, testing under TSan |
| [B: Embedded ring buffer](ringbuffer.md) | Weeks 3, 7–8, 10, 14, 16 | templates, `constexpr`, no-heap design, iterators, lock-free SPSC |

## How to approach them (Andrew Ng-style)

1. **Read the spec and write the tests first** — or at least list the cases.
2. Build the simplest version that passes one test. Then the next.
3. Run under sanitizers early (`-fsanitize=address,undefined`, and separately `-fsanitize=thread`).
4. Only then compare with the reference implementation. It's fine — expected, even — if yours differs.

Honest note: Capstone A's concurrency is the hardest thing in this course. If a test hangs or TSan
complains, that's not failure; it's the learning.
