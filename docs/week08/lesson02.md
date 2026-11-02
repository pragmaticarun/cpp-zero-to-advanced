# Lesson 8.2: constexpr, consteval, constinit, and if consteval

<span class="stdtag">C++23</span> · about 12 minutes

## Why this matters

A DSP filter needs a 256-entry sine table. You can compute it at startup — or have the *compiler* compute
it so it's baked into the binary, costs zero time at run time, and fits in read-only flash on a
microcontroller. That's `constexpr`. Its siblings `consteval` and `constinit` give you stronger guarantees.

## `constexpr`: *may* run at compile time

A `constexpr` function can be evaluated at compile time if its arguments are constants and its result is
needed as a constant; otherwise it runs normally. Since C++20, constexpr functions can use loops,
`std::vector`/`std::string` (as long as the memory is freed before evaluation ends), virtual calls, and
`try` blocks. UB during constant evaluation is a *compile error* — a free UB detector for your tests.

## `consteval`: *must* run at compile time

An immediate function. Every call must produce a constant — great for validating format strings, units,
or IDs at compile time.

## `constinit`: initialized at compile time, mutable afterwards

`constinit` asserts that a global/static variable has **static initialization** (no dynamic
initializer at startup). This kills the *static initialization order fiasco* — where one global's
constructor uses another global from a different .cpp file that hasn't been initialized yet.

```cpp title="examples/week08/lesson02.cpp"
--8<-- "examples/week08/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week08/lesson02.out"
```

## `if consteval` (C++23)

Inside a `constexpr` function, choose a compile-time-friendly path vs. a fast run-time path (e.g. an
intrinsic or a lookup table that isn't constexpr). It replaces `if (std::is_constant_evaluated())`, which
had a famous trap: inside `if constexpr (std::is_constant_evaluated())` it's always true.

!!! tip "Pro tip: test with static_assert"
    If your parsing or math is `constexpr`, add `static_assert(parse("42") == 42);` — tests that run every
    time you compile, and that fail on UB.

## Key takeaways

!!! success "Key takeaways"
    - `constexpr` functions may run at compile time; constant evaluation rejects UB.
    - `consteval` functions must run at compile time — great for validating literals.
    - `constinit` guarantees static initialization, avoiding the initialization order fiasco.
    - `if consteval` (C++23) picks a compile-time path vs. a run-time path.

## Quiz

**Q1.** What's the difference between `constexpr` and `consteval` functions?

??? question "Show answer"
    `constexpr` functions *can* be evaluated at compile time; `consteval` functions *must* be (every call is a constant expression).

**Q2.** Does `constinit` make a variable const?

??? question "Show answer"
    No — it only guarantees compile-time (static) initialization; the variable remains mutable.

**Q3.** What happens if a `constexpr` computation used in a `static_assert` overflows a signed int?

??? question "Show answer"
    Compile error: undefined behaviour isn't allowed in constant evaluation.

