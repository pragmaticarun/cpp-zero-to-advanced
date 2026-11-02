# Lesson 13.5: Latches, barriers, semaphores, and thread_local

<span class="stdtag">C++20</span> · about 10 minutes

## Why this matters

Some coordination patterns are so common C++20 gave them names: "wait until all N workers are ready"
(latch), "everyone finish phase 1 before anyone starts phase 2" (barrier), "at most 3 downloads at once"
(semaphore). Using the named tool is clearer and less bug-prone than building it from a mutex and condition
variable.

## The tools

| Primitive | Pattern |
|---|---|
| `std::latch` | single-use countdown: workers `count_down()`, someone `wait()`s for zero |
| `std::barrier` | reusable phase sync; optional completion function runs once per phase |
| `std::counting_semaphore<N>` | limit concurrent access to N; `acquire()`/`release()` |
| `std::binary_semaphore` | a lightweight signal between two threads |

```cpp title="examples/week13/lesson05.cpp"
--8<-- "examples/week13/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week13/lesson05.out"
```

## `thread_local`

A `thread_local` variable has one instance per thread — e.g. a per-thread scratch buffer or random engine,
with no locking. It's constructed on first use in each thread and destroyed when the thread exits.

## Choosing

Start with the highest-level tool that fits: a future for one result, a queue for streams of work, latch/
barrier for phases, a mutex for shared state. Atomics (next week) are the lowest level — reach for them last.

## Key takeaways

!!! success "Key takeaways"
    - `latch` = one-shot countdown; `barrier` = reusable phases with a completion step.
    - Semaphores bound concurrency; `binary_semaphore` is a cheap signal.
    - `thread_local` gives each thread its own instance — no locking needed.
    - Prefer the highest-level primitive that fits the pattern.

## Quiz

**Q1.** Can a `std::latch` be reused after it reaches zero?

??? question "Show answer"
    No — it's single-use; use `std::barrier` for repeated phases.

**Q2.** What does a barrier's completion function do?

??? question "Show answer"
    Runs once per phase, after all threads arrive and before they're released.

**Q3.** How many instances of a `thread_local` variable exist with 5 threads?

??? question "Show answer"
    One per thread that uses it (up to 5, plus main if it uses it).

