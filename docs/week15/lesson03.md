# Lesson 15.3: Testing, sanitizers, and static analysis

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

In C++, a bug can sit silently for months — reading freed memory "works" until a different allocator
layout makes it crash in production. The defence is layered: tests prove behaviour, sanitizers catch UB
while the tests run, static analysis finds bugs without running anything, and fuzzing finds inputs you
didn't think of. This course's own CI does exactly this for every example.

## Unit tests

Frameworks (GoogleTest, Catch2, doctest) give you assertions, fixtures and test discovery. The core idea
fits in a few lines — here's a tiny self-contained harness so the example compiles on its own:

```cpp title="examples/week15/lesson03.cpp"
--8<-- "examples/week15/lesson03.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson03.out"
```

With Catch2 the same test is `TEST_CASE("ring wraps") { ... REQUIRE(r.size() == 2); }`.

Test **edge cases** (empty, one element, full, wrap-around, max values), not just the happy path. A
**property test** checks an invariant over many random inputs (e.g. "pushing then popping N items returns
them in order").

## Sanitizers: run your tests under them

| Sanitizer | Flag | Finds |
|---|---|---|
| AddressSanitizer | `-fsanitize=address` | out-of-bounds, use-after-free, leaks (with LSan) |
| UndefinedBehaviorSanitizer | `-fsanitize=undefined` | signed overflow, bad shifts, misaligned access, null deref |
| ThreadSanitizer | `-fsanitize=thread` | data races, some deadlocks |
| MemorySanitizer (Clang) | `-fsanitize=memory` | reads of uninitialized memory |

Cost: roughly 2× (ASan) to 5–15× (TSan) slowdown. Run them in CI on every commit, not just when hunting.

## Static analysis and formatting

- Compile with `-Wall -Wextra -Wpedantic -Werror` (and `-Wconversion -Wshadow` for new code).
- **clang-tidy** with `cppcoreguidelines-*`, `bugprone-*`, `modernize-*` checks.
- **cppcheck** as a second opinion.
- **clang-format** with a committed `.clang-format` ends style debates.

## Fuzzing

libFuzzer calls `extern "C" int LLVMFuzzerTestOneInput(const uint8_t*, size_t)` millions of times with
mutated inputs, under ASan/UBSan. Any parser that reads untrusted data should be fuzzed.

## Key takeaways

!!! success "Key takeaways"
    - Test edge cases and invariants (property tests), not only happy paths.
    - Run tests under ASan+UBSan and TSan in CI on every commit.
    - Warnings-as-errors, clang-tidy and cppcheck catch bugs before running.
    - Fuzz any code that parses untrusted input.

## Quiz

**Q1.** Which sanitizer finds a data race?

??? question "Show answer"
    ThreadSanitizer (`-fsanitize=thread`).

**Q2.** Can ASan and TSan be combined in one build?

??? question "Show answer"
    No — they're incompatible; use separate builds.

**Q3.** What's a property-based test?

??? question "Show answer"
    A test that checks an invariant holds across many generated inputs, often against a simple reference model.

