# Lesson 15.4: Debugging, profiling, and compiler optimization

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

"It's slow" is not a diagnosis. Professionals measure first: profile to find the 5% of code that takes 90%
of the time, then optimize *that*, then measure again. And when it crashes, a debugger beats a hundred
`std::cout` lines. This lesson is a field guide to the tools.

## Debugging essentials

Build with `-g -O0` (or `-Og`) for debugging. In gdb/lldb: `break file.cpp:42`, `run`, `bt` (backtrace),
`frame 2`, `print x`, `watch buffer[3]` (stop when memory changes), `catch throw`. Enable core dumps
(`ulimit -c unlimited`) to inspect crashes after the fact.

## Optimization flags

`-O2` is the usual release level; `-O3` adds aggressive inlining/vectorization (measure — not always
faster). `-march=native` uses your CPU's instructions (don't ship it to unknown machines). **LTO** (`-flto`)
optimizes across translation units; **PGO** (`-fprofile-generate` → run → `-fprofile-use`) lets the compiler
optimize for real workloads — often 10–20% for branchy code.

## Profiling

Sampling profilers (`perf record -g ./app && perf report`, VTune, Instruments) show where time goes with
low overhead. Frame profilers like Tracy are great for games and real-time code.

## Micro-benchmarks lie unless you're careful

The compiler deletes work whose result is unused; caches are warm on the second run; timers have
resolution limits. Use Google Benchmark (`benchmark::DoNotOptimize`), repeat runs, and report medians.

```cpp title="examples/week15/lesson04.cpp"
--8<-- "examples/week15/lesson04.cpp"
```

**Output**:

```text
--8<-- "examples/week15/lesson04.out"
```

The example measures a summation two ways and is careful to *use* the result. Timings are machine-dependent,
so only the checksum is verified.

## Hints to the compiler

`[[likely]]`/`[[unlikely]]` (C++20) mark branch probabilities; `[[assume(expr)]]` (C++23) promises a
condition (UB if false!). C++26 adds `std::simd` for portable data-parallel types. Use hints only after
profiling shows they help.

## Key takeaways

!!! success "Key takeaways"
    - Measure before optimizing: sampling profilers find the hot spots.
    - `-O2` for release; LTO and PGO give cross-TU and workload-driven gains.
    - Benchmarks must defeat dead-code elimination, warm caches deliberately and repeat runs.
    - Use `[[likely]]`/`[[assume]]` sparingly and only with evidence.

## Quiz

**Q1.** Why might a benchmark of `for (...) s += x;` report 0 ns?

??? question "Show answer"
    If `s` is unused the optimizer removes the loop entirely.

**Q2.** What does PGO do?

??? question "Show answer"
    Uses profiles from representative runs to guide inlining, layout and branch decisions.

**Q3.** What happens if an `[[assume(x > 0)]]` is false at run time?

??? question "Show answer"
    Undefined behaviour — the compiler may have optimized based on it.

